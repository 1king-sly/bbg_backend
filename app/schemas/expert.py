from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class ExpertBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    field_of_expertise: str
    bio: Optional[str] = None

class ExpertCreate(ExpertBase):
    password: str

class ExpertUpdate(ExpertBase):
    password: Optional[str] = None

class Expert(ExpertBase):
    id: int
    rating: float
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True