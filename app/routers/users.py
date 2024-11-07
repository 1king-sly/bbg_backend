from fastapi import APIRouter, Depends, HTTPException
from app.src.auth.auth import get_current_user, get_password_hash
from app.src.models.schemas import UserCreate, User, UserUpdate, UserIn
from prisma import Prisma

router = APIRouter()
prisma = Prisma()

@router.post("/", response_model=User)
async def create_user(user: UserIn):
    # print(user.model_dump(exclude_unset=True))
    hashed_password = get_password_hash(user.password)
    try:
        # Hash the password before adding it to the user data
        hashed_password = get_password_hash(user.password)

        # Use model_dump to get data excluding password
        data = user.model_dump(exclude={"password"})

        # Add hashed password back into the data
        data["password"] = hashed_password

        # Create the user in the database
        db_user = await prisma.user.create(data=data)

        return db_user
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=User)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    try:
        updated_user = await prisma.user.update(
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