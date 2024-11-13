from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import List,Annotated
from app.src.auth.auth import get_current_user,get_password_hash
from app.src.models.schemas import ExpertCreate, Expert, ExpertUpdate, ExpertBase, ExpertOut
from db import prisma

router = APIRouter()




@router.post("/", response_model=ExpertOut)
async def create_expert(expert: ExpertCreate, current_user = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        hashed_password = get_password_hash(expert.password)
        db_expert =  prisma.expert.create(
            data={
                "name": expert.name,
                "email": str(expert.email),
                'password': hashed_password,
                "phone": expert.phone,
                "bio": expert.bio,
                # "website": expert.website,
                "isVerified": expert.isVerified,
                "fieldOfExpertise": expert.fieldOfExpertise,

            }
        )
        return db_expert
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Expert])
async def list_experts():

    experts =  prisma.expert.find_many(
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

    expert =  prisma.expert.find_unique(where={"id": expert_id})
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return expert


@router.get("/profile/me", response_model=Expert)
async def read_user_me(current_user: Expert = Depends(get_current_user)):
    return current_user



def get_month_key(date: datetime) -> str:
        return f"{date.year}-{date.month:02d}"


@router.get("/me/stats", response_model=dict)
async def read_user_me_stats(current_user: Expert = Depends(get_current_user)):
    courses_count = prisma.course.count(
        where={"expertId": current_user.id}
    )
    events_count = prisma.event.count(
        where={"expertId": current_user.id}
    )
    sessions_count = prisma.session.count(
        where={"expertId": current_user.id}
    )
    # noinspection SqlResolve
    courses_monthly = prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Course"
            WHERE "expertId" = '{current_user.id}'
            GROUP BY month
            ORDER BY month;
        """
    )

    events_monthly = prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Event"
            WHERE "expertId" = '{current_user.id}'
            GROUP BY month
            ORDER BY month;
            """
    )

    sessions_monthly = prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Session"
            WHERE "expertId" = '{current_user.id}'
            GROUP BY month
            ORDER BY month;
            """
    )

    # Format the monthly results into a dictionary for each entity
    def format_monthly_data(data):
        return {get_month_key(datetime.strptime(row['month'], '%Y-%m-%dT%H:%M:%S%z')): row['count'] for row in data}

    stats = {
        "courses_count": courses_count,
        "events_count": events_count,
        "sessions_count": sessions_count,
        "monthly_counts": {
            "courses": format_monthly_data(courses_monthly),
            "events": format_monthly_data(events_monthly),
            "sessions": format_monthly_data(sessions_monthly),
        }
    }

    return stats
@router.put("/{expert_id}", response_model=Expert)
async def update_expert(
    expert_id: int,
    expert_update: ExpertBase,
    current_user = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        updated_expert =  prisma.expert.update(
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
            deleted_expert =  prisma.expert.delete(where={"id": expert_id})
            return deleted_expert
    except Exception:
        raise HTTPException(status_code=404, detail="Expert not found")