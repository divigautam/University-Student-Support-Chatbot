import os
import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import User, Document
from auth import require_admin
from config import get_settings
from rag.retriever import ingest_document, delete_document as remove_from_chroma

router = APIRouter()
settings = get_settings()

async def process_document_background(file_path: str, doc_id: int):
    # This runs in background
    # But database operations should use a new session, simplified for now by just calling ingest
    try:
        chunks = ingest_document(file_path, doc_id)
        # We need a new db session to update status
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            doc = await session.get(Document, doc_id)
            if doc:
                doc.status = "completed"
                doc.chunk_count = chunks
                await session.commit()
    except Exception as e:
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            doc = await session.get(Document, doc_id)
            if doc:
                doc.status = "failed"
                doc.error_message = str(e)
                await session.commit()

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    os.makedirs(settings.DOCUMENTS_PATH, exist_ok=True)
    file_path = os.path.join(settings.DOCUMENTS_PATH, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    doc = Document(filename=file.filename, file_path=file_path, status="processing")
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    asyncio.create_task(process_document_background(file_path, doc.id))
    
    return {"id": doc.id, "filename": doc.filename, "status": doc.status}

@router.get("/documents")
async def list_documents(db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    result = await db.execute(select(Document))
    return result.scalars().all()

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception:
        pass
        
    remove_from_chroma(document_id)
    
    await db.delete(doc)
    await db.commit()
    return {"status": "deleted"}

@router.post("/documents/{document_id}/reindex")
async def reindex_document(document_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    doc.status = "processing"
    await db.commit()
    
    remove_from_chroma(document_id)
    asyncio.create_task(process_document_background(doc.file_path, doc.id))
    
    return {"status": "reindexing started"}
