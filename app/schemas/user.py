from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    is_pregnant: Optional[bool] = False
    pregnancy_date: Optional[datetime] = None
    has_child: Optional[bool] = False
    child_birth_date: Optional[datetime] = None
    child_gender: Optional[str] = None
    last_period_date: Optional[datetime] = None
    period_end_date: Optional[datetime] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True