from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_password_hash
from app.schemas.expert import ExpertCreate, ExpertUpdate, Expert
from app.models.expert import Expert as ExpertModel

from db import prisma

router = APIRouter(prefix="/experts", tags=["experts"])

@router.post("/", response_model=Expert)
async def create_expert(expert: ExpertCreate, db: Session = Depends(get_db)):
    # existing_expert = await prisma.expert.find_unique(
    #     where={"email": expert.email},
    # )
    #
    # if existing_expert:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    db_expert = db.query(ExpertModel).filter(ExpertModel.email == expert.email).first()
    if db_expert:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(expert.password)

    # new_expert = await prisma.expert.create(
    #     email=expert.email,
    #     name=expert.name,
    #     phone=expert.phone,
    #     fieldOfExpertise=expert.fieldOfExpertise,
    #     password = hashed_password
    # )
    db_expert = ExpertModel(
        **expert.dict(exclude={"password"}),
        hashed_password=hashed_password
    )
    
    db.add(db_expert)
    db.commit()
    db.refresh(db_expert)
    return db_expert

@router.get("/", response_model=List[Expert])
def get_experts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    experts = db.query(ExpertModel).offset(skip).limit(limit).all()
    return experts

@router.get("/{expert_id}", response_model=Expert)
def get_expert(expert_id: int, db: Session = Depends(get_db)):
    expert = db.query(ExpertModel).filter(ExpertModel.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return expert

@router.put("/{expert_id}", response_model=Expert)
def update_expert(expert_id: int, expert: ExpertUpdate, db: Session = Depends(get_db)):
    db_expert = db.query(ExpertModel).filter(ExpertModel.id == expert_id).first()
    if not db_expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    update_data = expert.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_expert, field, value)
    
    db.commit()
    db.refresh(db_expert)
    return db_expert

@router.delete("/{expert_id}")
def delete_expert(expert_id: int, db: Session = Depends(get_db)):
    expert = db.query(ExpertModel).filter(ExpertModel.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    
    db.delete(expert)
    db.commit()
    return {"message": "Expert deleted successfully"}