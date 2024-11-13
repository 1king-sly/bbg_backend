from datetime import timedelta

from fastapi import APIRouter,  HTTPException, status
from db import prisma
from app.src.models.schemas import UserLogin



from app.src.auth.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password

router = APIRouter()


@router.post("/token")
async def login_for_access_token(form_data: UserLogin):


    # Attempt to find the user in each of the models
    user =  prisma.user.find_unique(where={"email": form_data.email})
    partner =  prisma.partner.find_unique(where={"email": form_data.email})
    organization =  prisma.organization.find_unique(where={"email": form_data.email})
    expert =  prisma.expert.find_unique(where={"email": form_data.email})

    # Determine which model returned a result, if any, and verify the password
    account = None
    role = None

    if user and verify_password(form_data.password, user.password):
        account = user
        role = user.role
    elif partner and verify_password(form_data.password, partner.password):
        account = partner
        role = "partner"
    elif organization and verify_password(form_data.password, organization.password):
        account = organization
        role = "organization"
    elif expert and verify_password(form_data.password, expert.password):
        account = expert
        role = "expert"

    if account is None:
        # If no account was found or password did not match, raise an authentication error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate an access token with both email and role in the payload
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": account.email, "role": role},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token,"role":role ,"token_type": "bearer"}
