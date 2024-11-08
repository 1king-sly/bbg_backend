from fastapi import APIRouter, Depends, HTTPException
from typing import List, Annotated
from app.src.auth.auth import get_current_user,get_password_hash
from app.src.models.schemas import  PartnerIn, Partner, PartnerOut
from db import prisma

router = APIRouter()


@router.post("/", response_model=Partner)
async def create_partner(partner: PartnerIn, current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        hashed_password = get_password_hash(partner.password)

        db_partner = await prisma.partner.create(
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
    partners = await prisma.partner.find_many(
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
    partner = await prisma.pertner.find_unique(where={"id": partner_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Expert not found")
    return partner


@router.put("/{partner_id}", response_model=Partner)
async def update_partner(
        partner_id: int,
        partner_update: Partner,
        current_user=Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        updated_partner = await prisma.partner.update(
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