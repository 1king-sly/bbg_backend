from fastapi import APIRouter, Depends, HTTPException
from typing import List,Annotated
from app.src.auth.auth import get_current_user
from app.src.models.schemas import ExpertCreate, Expert, ExpertUpdate,ExpertBase
from db import prisma

router = APIRouter()


@router.post("/", response_model=ExpertBase)
async def create_expert(expert: ExpertCreate, current_user = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        db_expert = await prisma.expert.create(
            data =  expert.model_dump()
        )
        return db_expert
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Expert])
async def list_experts():
    experts = await prisma.expert.find_many(
        include={
            'courses': True,
            'events': True,
            'sessions': True,
        }
    )

    expert_list = []
    for expert in experts:
        expert_dict = expert.dict()
        expert_dict['coursesCreated'] = len(expert.courses)
        expert_dict['eventsCreated'] = len(expert.events)
        expert_dict['sessionsHeld'] = len(expert.sessions)
        expert_list.append(expert_dict)

    return expert_list

@router.get("/{expert_id}", response_model=Expert)
async def read_expert(expert_id: int):
    expert = await prisma.expert.find_unique(where={"id": expert_id})
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return expert

@router.put("/{expert_id}", response_model=Expert)
async def update_expert(
    expert_id: int,
    expert_update: ExpertBase,
    current_user = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        updated_expert = await prisma.expert.update(
            where={"id": expert_id},
            data=expert_update.model_dump(exclude_unset=True)
        )

        return updated_expert
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{expert_id}")
async def delete_expert(expert_id: int, current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        await prisma.expert.delete(where={"id": expert_id})
        await prisma.disconnect()
        return {"message": "Expert deleted successfully"}
    except Exception:
        raise HTTPException(status_code=404, detail="Expert not found")