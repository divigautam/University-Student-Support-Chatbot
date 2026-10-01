from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from database import get_db
from models import User, Conversation, Message, Document, Feedback
from auth import require_admin
from rag.retriever import get_collection_stats

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    users_count = await db.execute(select(func.count(User.id)))
    convs_count = await db.execute(select(func.count(Conversation.id)))
    msgs_count = await db.execute(select(func.count(Message.id)))
    docs_count = await db.execute(select(func.count(Document.id)))
    
    avg_rating_res = await db.execute(select(func.avg(Feedback.rating)))
    avg_rating = avg_rating_res.scalar() or 0.0
    
    chroma_stats = get_collection_stats()
    
    # recent activity (last 7 days message count)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_msgs = await db.execute(
        select(func.date(Message.created_at), func.count(Message.id))
        .where(Message.created_at >= seven_days_ago)
        .group_by(func.date(Message.created_at))
    )
    activity = [{"date": str(d), "count": c} for d, c in recent_msgs.all()]
    
    # top feedback comments
    recent_comments = await db.execute(
        select(Feedback).where(Feedback.comment != None, Feedback.comment != '').order_by(Feedback.created_at.desc()).limit(5)
    )
    comments = [{"rating": f.rating, "comment": f.comment, "date": str(f.created_at)} for f in recent_comments.scalars().all()]
    
    return {
        "total_users": users_count.scalar(),
        "total_conversations": convs_count.scalar(),
        "total_messages": msgs_count.scalar(),
        "total_documents": docs_count.scalar(),
        "total_chunks": chroma_stats.get("total_chunks", 0),
        "avg_feedback_rating": float(avg_rating),
        "recent_activity": activity,
        "top_feedback_comments": comments
    }
