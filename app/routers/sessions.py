from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.src.auth.auth import get_current_user
from app.src.models.schemas import SessionCreate, Session, SessionUpdate
from db import prisma

router = APIRouter()

@router.post("/", response_model=Session)
async def create_session(session: SessionCreate, current_user = Depends(get_current_user)):
    try:
        db_session =  prisma.session.create({
            "data": {
                **session.model_dump(),
                "userId": current_user.id
            }
        })
        return db_session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Session])
async def list_sessions(current_user = Depends(get_current_user)):
    # Users can see their sessions, experts can see sessions where they're the expert
    if current_user.role == "EXPERT":
        return  prisma.session.find_many(
            where={"expertId": current_user.id},
            include={"user": True}
        )
    else:
        return  prisma.session.find_many(
            where={"userId": current_user.id},
            include={"expert": True}
        )

@router.put("/{session_id}", response_model=Session)
async def update_session(
    session_id: int,
    session_update: SessionUpdate,
    current_user = Depends(get_current_user)
):
    session =  prisma.session.find_unique(where={"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user.id != session.userId and current_user.id != session.expertId:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        updated_session =  prisma.session.update(
            where={"id": session_id},
            data=session_update.model_dump(exclude_unset=True)
        )
        return updated_session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/complete")
async def complete_session(
    session_id: int,
    rating: int = None,
    current_user = Depends(get_current_user)
):
    session =  prisma.session.find_unique(where={"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user.id != session.userId:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        await prisma.session.update(
            where={"id": session_id},
            data={
                "status": "completed",
                "endTime": datetime.now(),
                "rating": rating
            }
        )
        
        # Update expert's rating if rating was provided
        if rating:
            expert =  prisma.expert.find_unique(where={"id": session.expertId})
            total_ratings = await prisma.session.count(
                where={
                    "expertId": session.expertId,
                    "rating": {"not": None}
                }
            )
            
            new_rating = ((expert.rating * total_ratings) + rating) / (total_ratings + 1)
            
            await prisma.expert.update(
                where={"id": session.expertId},
                data={"rating": new_rating}
            )
        
        return {"message": "Session completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))