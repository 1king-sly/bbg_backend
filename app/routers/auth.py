from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from db import prisma
from app.src.models.schemas import UserLogin



from app.src.auth.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: UserLogin = Depends()):

    print(form_data.model_dump())
    user = await prisma.user.find_unique(where={"email": form_data.username})
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}