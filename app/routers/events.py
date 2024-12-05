from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.src.auth.auth import get_current_user
from app.src.models.schemas import EventCreate, Event, EventUpdate
from db import prisma
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=Event)
async def create_event(event: EventCreate, current_user = Depends(get_current_user)):

    try:

        if current_user.role not in ["ADMIN", "EXPERT", "PARTNER", "ORGANIZATION"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        event_data = event.model_dump()



        if current_user.role == "EXPERT":
            event_data["expertId"] = current_user.id
        elif current_user.role == "PARTNER":
            event_data["partnerId"] = current_user.id
        elif current_user.role == "ORGANIZATION":
            event_data["organizationId"] = current_user.id





        db_event =  prisma.event.create(data=event_data)

        return db_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Event])
async def list_events():

    events =  prisma.event.find_many(include={
        "expert": True,
        "attendees": True
    },
        order={
            "date": "desc",
        }
    )


    return events

@router.get("/upcoming", response_model=List[Event])
async def list_upcoming_events():
    current_datetime = datetime.utcnow()


    events =  prisma.event.find_many(
        where={
            "date": {
                "gte": current_datetime
            }
        },
        include={
        "expert": True,
        "attendees": True
    },
        order={
            "date": "asc",
        }
    )


    return events
@router.get("/me", response_model=List[Event])
async def list_events_created_by_me(current_user = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=400, detail="User Does not exist")

    if current_user.role not in ["ADMIN", "EXPERT", "PARTNER", "ORGANIZATION"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    events =  prisma.event.find_many(
        where={
            'OR': [
                {"expertId": current_user.id},
                {"partnerId": current_user.id},
                {"organizationId":current_user.id}
            ]
        },include={
        "expert": True,
        "attendees": True,
        "partner": True,
        "organization": True
    },
        order={
            "createdAt":"desc",
        }
    )

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
        raise HTTPException(status_code=402, detail="Already registered for this event")

    try:
         prisma.event.update(
            where={"id": event_id},
            data={
                "attendees": {
                    "connect": [{"id": current_user.id}]
                }
            })
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
        updated_event =  prisma.event.update(
            where={"id": event_id},
            data=event_update.model_dump(exclude_unset=True)
        )
        return updated_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.delete("/{event_id}")
async def delete_expert(event_id: int, current_user=Depends(get_current_user)):
    if current_user.role not in ["ADMIN","EXPERT","PARTNER","ORGANIZATION"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        deleted_event =  prisma.event.delete(where={"id": event_id})
        return deleted_event

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/enrolled/me", response_model=List[Event])
async def list_events_enrolled_to_by_me(current_user = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=400, detail="User Does not exist")

    try:


        events =  prisma.event.find_many(
            where={
               "attendees":{
                   "some":{
                       "id":current_user.id
                   }
               }
            },include={
            "expert": True,
            "attendees": True,
            "partner": True,
            "organization": True
        },
            order={
                "createdAt":"desc",
            }
        )

        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
