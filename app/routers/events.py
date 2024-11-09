from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.src.auth.auth import get_current_user
from app.src.models.schemas import EventCreate, Event, EventUpdate
from db import prisma

router = APIRouter()

@router.post("/", response_model=Event)
async def create_event(event: EventCreate, current_user = Depends(get_current_user)):


    
    try:


        if current_user.role not in ["ADMIN", "EXPERT"]:
            raise HTTPException(status_code=403, detail="Not authorized")


        db_event =  prisma.event.create(
            data = event.model_dump()
        )
        return db_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Event])
async def list_events():

    events =  prisma.event.find_many(include={
        "expert": True,
        "attendees": True
    })

    return events
@router.get("/me", response_model=List[Event])
async def list_events(current_user = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=400, detail="User Does not exist")

    if current_user.role not in ["ADMIN", "EXPERT"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    events =  prisma.event.find_many(
        where={
            'OR': [
                {"expertId": current_user.id},
                {"partnerId": current_user.id}
            ]
        },include={
        "expert": True,
        "attendees": True
    })

    return events


@router.post("/{event_id}/register")
async def register_for_event(event_id: int, current_user = Depends(get_current_user)):

    event =  prisma.event.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is already registered
    existing_registration =  prisma.event.find_first(
        where={
            "id": event_id,
            "attendees": {
                "some": {
                    "id": current_user.id
                }
            }
        }
    )

    if existing_registration:
        raise HTTPException(status_code=400, detail="Already registered for this event")

    try:
        await prisma.event.update(
            where={"id": event_id},
            data={
                "attendees": {
                    "connect": [{"id": current_user.id}]
                }
            }
        )
        return {"message": "Successfully registered for event"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{event_id}", response_model=Event)
async def update_event(
        event_id: int,
        event_update: EventUpdate,
        current_user=Depends(get_current_user)
):

    event =  prisma.event.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != "ADMIN" and event.expertId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        updated_event = await prisma.event.update(
            where={"id": event_id},
            data=event_update.model_dump(exclude_unset=True)
        )
        return updated_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
