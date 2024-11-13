import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Annotated
from app.src.auth.auth import get_current_user, get_password_hash
from app.src.models.schemas import OrganizationIn, Organization, OrganizationOut
from db import prisma

router = APIRouter()


@router.post("/", response_model=Organization)
async def create_organization(organization: Organization, current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        hashed_password = get_password_hash(str(organization.email))

        db_partner = prisma.organization.create(
            data={
                "name": organization.name,
                "email": str(organization.email),
                'password': hashed_password,
                "phone": organization.phone,
                "description": organization.description,
                "website": organization.website,
                "isVerified": organization.isVerified,

            }
        )
        return db_partner
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[OrganizationOut])
async def list_organizations():
    organizations = prisma.organization.find_many(
        include={
            'courses': True,
            'events': True,
            'sessions': True,
        }
    )

    organization_list = []
    for organization in organizations:
        organization_dict = organization.dict()
        organization_dict['coursesCreated'] = len(organization.courses)
        organization_dict['eventsCreated'] = len(organization.events)
        organization_dict['sessionsHeld'] = len(organization.sessions)
        organization_list.append(organization_dict)

    return organization_list


@router.get("/profile/me", response_model=Organization)
async def read_user_me(current_user: Organization = Depends(get_current_user)):
    return current_user

def get_month_key(date: datetime.datetime) -> str:
        return f"{date.year}-{date.month:02d}"
@router.get("/me/stats", response_model=dict)
async def read_user_me_stats(current_user: Organization = Depends(get_current_user)):
    courses_count =  prisma.course.count(
        where={"organizationId": current_user.id}
    )
    events_count =  prisma.event.count(
        where={"organizationId": current_user.id}
    )
    sessions_count =  prisma.session.count(
        where={"organizationId": current_user.id}
    )
    # noinspection SqlResolve
    courses_monthly =  prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Course"
            WHERE "organizationId" = '{current_user.id}'
            GROUP BY month
            ORDER BY month;
        """
    )

    events_monthly =  prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Event"
            WHERE "organizationId" = '{current_user.id}'
            GROUP BY month
            ORDER BY month;
            """
    )

    sessions_monthly =  prisma.query_raw(
        f"""
            SELECT DATE_TRUNC('month', "createdAt") as month, COUNT(*) as count 
            FROM "Session"
            WHERE "organizationId" = '{current_user.id}'
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


@router.get("/{organization_id}", response_model=Organization)
async def read_partner(organization_id: int):
    organization = prisma.organization.find_unique(where={"id": organization_id})
    if not organization:
        raise HTTPException(status_code=404, detail="Partner not found")
    return organization


@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
        organization_id: int,
        organization_update: Organization,
        current_user=Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        updated_partner = prisma.organization.update(
            where={"id": organization_id},
            data=organization_update.model_dump(exclude_unset=True)
        )

        return updated_partner
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{organization_id}")
async def delete_organization(organization_id: int, current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        await prisma.organization.delete(where={"id": organization_id})
        return {"message": "Organization deleted successfully"}
    except Exception:
        raise HTTPException(status_code=404, detail="Partner not found")
