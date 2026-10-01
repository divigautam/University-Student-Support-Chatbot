import json
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from openai import OpenAI

from config import get_settings
from database import get_db
from models import User, Conversation, Message
from auth import get_current_user
from rag.retriever import retrieve

router = APIRouter()
settings = get_settings()
client = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class SourceReference(BaseModel):
    source: str
    page: int
    relevance_score: float
    text_snippet: str

class ChatResponse(BaseModel):
    message: str
    response: str
    sources: list[SourceReference]
    conversation_id: int

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation_id = request.conversation_id
    
    if not conversation_id:
        new_conv = Conversation(user_id=current_user.id, title=request.message[:50])
        db.add(new_conv)
        await db.commit()
        await db.refresh(new_conv)
        conversation_id = new_conv.id
    else:
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id))
        if not result.scalars().first():
            raise HTTPException(status_code=404, detail="Conversation not found")

    user_message = Message(conversation_id=conversation_id, role="user", content=request.message)
    db.add(user_message)
    await db.commit()

    # Retrieve context
    retrieved = retrieve(request.message)
    sources = []
    context_text = ""
    for r in retrieved:
        context_text += f"Relevant University Information:\n---\nSource: {r['source']}, Page {r['page']}\n{r['text']}\n---\n"
        sources.append(SourceReference(
            source=r['source'],
            page=r['page'],
            relevance_score=r['score'],
            text_snippet=r['text'][:100] + "..."
        ))

    # Get history
    history_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).limit(10)
    )
    history = history_result.scalars().all()[::-1]

    messages = [
        {"role": "system", "content": "You are an AI assistant for ABES Engineering College, Ghaziabad. You help students with questions about academics, schedules, policies, and campus life. Use the provided context from university documents to give accurate, helpful answers. If the context doesn't contain relevant information, say so honestly. Always be friendly and supportive."}
    ]
    if context_text:
        messages.append({"role": "system", "content": context_text})

    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
        
    messages.append({"role": "user", "content": request.message})

    response = client.chat.completions.create(
        model="qwen3.5:4b",
        messages=messages
    )
    
    bot_reply = response.choices[0].message.content

    bot_message = Message(
        conversation_id=conversation_id, 
        role="assistant", 
        content=bot_reply,
        sources_json=json.dumps([s.model_dump() for s in sources])
    )
    db.add(bot_message)
    await db.commit()

    return ChatResponse(
        message=request.message,
        response=bot_reply,
        sources=sources,
        conversation_id=conversation_id
    )

@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Conversation).where(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc()))
    return result.scalars().all()

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv_result = await db.execute(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id))
    if not conv_result.scalars().first():
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    result = await db.execute(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()))
    return result.scalars().all()

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    conv_result = await db.execute(select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == current_user.id))
    conv = conv_result.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    await db.delete(conv)
    await db.commit()
    return {"status": "deleted"}
