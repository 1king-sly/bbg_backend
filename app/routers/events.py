from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.src.auth.auth import get_current_user
from app.src.models.schemas import EventCreate, Event, EventUpdate
from prisma import Prisma

router = APIRouter()
prisma = Prisma()

@router.post("/", response_model=Event)
async def create_event(event: EventCreate, current_user = Depends(get_current_user)):
    print(event.model_dump())


    
    try:

        await prisma.connect()

        if current_user.role not in ["ADMIN", "EXPERT"]:
            raise HTTPException(status_code=403, detail="Not authorized")


        db_event = await prisma.event.create(
            data = event.model_dump()
        )
        return db_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Event])
async def list_events():

    return await prisma.event.find_many(include={
        "expert": True,
        "attendees": True
    })

@router.post("/{event_id}/register")
async def register_for_event(event_id: int, current_user = Depends(get_current_user)):
    await prisma.connect()

    event = await prisma.event.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is already registered
    existing_registration = await prisma.event.find_first(
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
    await prisma.connect()

    event = await prisma.event.find_unique(where={"id": event_id})
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
