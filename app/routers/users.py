from typing import List

from fastapi import APIRouter, Depends, HTTPException
from app.src.auth.auth import get_current_user, get_password_hash
from app.src.models.schemas import  User,  UserIn,UserOut
from db import prisma



router = APIRouter()



@router.get("/", response_model=List[UserOut])
async def list_users():
    try:
        db_users =  prisma.user.findMany(
            where={
                "role":"USER"
            },
            order={
                "createdAt":"desc"
            }

        )

        return db_users
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=User)
async def create_user(user: UserIn):
    try:
        hashed_password = get_password_hash(user.password)

        db_user =  prisma.user.create(
            data={
                "name": user.name,
                "email": str(user.email),
                'password':hashed_password,

            }
        )

        return db_user
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserOut)
async def read_user_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
async def update_user_me(user_update: UserOut, current_user: UserOut = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="User Not Found")

    try:
        updated_user =  prisma.user.update(
            where={"id": current_user.id},
            data=user_update.model_dump(exclude_unset=True)
        )
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = await prisma.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


