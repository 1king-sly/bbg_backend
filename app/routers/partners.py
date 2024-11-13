from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Annotated
from app.src.auth.auth import get_current_user,get_password_hash
from app.src.models.schemas import  PartnerIn, Partner, PartnerOut
from db import prisma

router = APIRouter()


@router.post("/", response_model=PartnerOut)
async def create_partner(partner: Partner, current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        hashed_password = get_password_hash(str(partner.email))

        db_partner =  prisma.partner.create(
            data={
                "name": partner.name,
                "email": str(partner.email),
                'password': hashed_password,
                "phone":partner.phone,
                "description": partner.description,
                "website": partner.website,
                "isVerified": partner.isVerified,

            }
        )
        return db_partner
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PartnerOut])
async def list_partners():
    partners =  prisma.partner.find_many(
        include={
            'courses': True,
            'events': True,
            'sessions': True,
        }
    )

    partner_list = []
    for partner in partners:
        partner_dict = partner.dict()
        partner_dict['coursesCreated'] = len(partner.courses)
        partner_dict['eventsCreated'] = len(partner.events)
        partner_dict['sessionsHeld'] = len(partner.sessions)
        partner_list.append(partner_dict)

    return partner_list


@router.get("/{partner_id}", response_model=Partner)
async def read_partner(partner_id: int):
    partner =  prisma.pertner.find_unique(where={"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Expert not found")
    return partner

@router.get("/profile/me", response_model=Partner)
async def read_user_me(current_user: Partner = Depends(get_current_user)):
    return current_user



def get_month_key(date: datetime) -> str:
        return f"{date.year}-{date.month:02d}"


@router.get("/me/stats", response_model=dict)
async def read_user_me_stats(current_user: Partner = Depends(get_current_user)):
    courses_count = prisma.course.count(
        where={"partnerId": current_user.id}
    )
    events_count = prisma.event.count(
        where={"partnerId": current_user.id}
    )
    sessions_count = prisma.session.count(
        where={"partnerId": current_user.id}
    )
    # noinspection SqlResolve
    courses_monthly = prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Course"
            WHERE "partnerId" = '{current_user.id}'
            GROUP BY month
            ORDER BY month;
        """
    )

    events_monthly = prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Event"
            WHERE "partnerId" = '{current_user.id}'
            GROUP BY month
            ORDER BY month;
            """
    )

    sessions_monthly = prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Session"
            WHERE "partnerId" = '{current_user.id}'
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
@router.put("/{partner_id}", response_model=Partner)
async def update_partner(
        partner_id: int,
        partner_update: Partner,
        current_user=Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        updated_partner =  prisma.partner.update(
            where={"id": partner_id},
            data=partner_update.model_dump(exclude_unset=True)
        )

        return updated_partner
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{partner_id}")
async def delete_partner(partner_id: int, current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        await prisma.partner.delete(where={"id": partner_id})
        return {"message": "Partner deleted successfully"}
    except Exception:
        raise HTTPException(status_code=404, detail="Partner not found")