from fastapi import APIRouter, Depends, HTTPException
from typing import List, Annotated
from app.src.auth.auth import get_current_user,get_password_hash
from app.src.models.schemas import  OrganizationIn, Organization, OrganizationOut
from db import prisma

router = APIRouter()


@router.post("/", response_model=Organization)
async def create_organization(organization: OrganizationIn, current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        hashed_password = get_password_hash(organization.password)

        db_partner =  prisma.organization.create(
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
    organizations =  prisma.organization.find_many(
        include={
            'courses': True,
            'events': True,
            # 'sessions': True,
        }
    )

    organization_list = []
    for organization in organizations:
        organization_dict = organization.dict()
        organization_dict['coursesCreated'] = len(organization.courses)
        organization_dict['eventsCreated'] = len(organization.events)
        # organization_dict['sessionsHeld'] = len(organization.sessions)
        organization_dict.append(organization_dict)

    return organization_list


@router.get("/{organization_id}", response_model=Organization)
async def read_partner(organization_id: int):
    organization =  prisma.organization.find_unique(where={"id": organization_id})
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
        updated_partner =  prisma.organization.update(
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