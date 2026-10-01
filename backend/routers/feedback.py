from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from database import get_db
from models import User, Message, Feedback
from auth import get_current_user, require_admin

router = APIRouter()

class FeedbackRequest(BaseModel):
    message_id: int
    rating: int
    comment: str | None = None

class FeedbackResponse(BaseModel):
    id: int
    message_id: int
    rating: int
    comment: str | None
    created_at: datetime

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not (1 <= request.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
    msg_result = await db.execute(select(Message).where(Message.id == request.message_id))
    msg = msg_result.scalars().first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    fb_result = await db.execute(select(Feedback).where(Feedback.message_id == request.message_id, Feedback.user_id == current_user.id))
    if fb_result.scalars().first():
        raise HTTPException(status_code=400, detail="Feedback already submitted for this message")
        
    feedback = Feedback(
        message_id=request.message_id,
        user_id=current_user.id,
        rating=request.rating,
        comment=request.comment
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    return FeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at
    )

@router.get("/feedback/stats")
async def get_feedback_stats(db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    result = await db.execute(select(func.avg(Feedback.rating).label('average_rating'), func.count(Feedback.id).label('total_count')))
    row = result.first()
    
    dist_result = await db.execute(select(Feedback.rating, func.count(Feedback.id)).group_by(Feedback.rating))
    distribution = {r: c for r, c in dist_result.all()}
    
    return {
        "average_rating": float(row.average_rating) if row.average_rating else 0.0,
        "total_count": row.total_count,
        "distribution": distribution
    }
