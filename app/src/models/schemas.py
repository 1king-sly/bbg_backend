from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    EXPERT = "EXPERT"
    PARTNER = "PARTNER"
    ORGANIZATION = "ORGANIZATION"

class UserBase(BaseModel):
    email: EmailStr
    name: str
    cycleDays:int
    image:Optional[str] = None
    phone: Optional[str] = None
    dateOfBirth: Optional[datetime] = None
    pregnancyDate: Optional[datetime] = None
    isPregnant: Optional[bool] = False
    isMenstruating: Optional[bool] = False
    hasChild: Optional[bool] = False
    childBirthDate: Optional[datetime] = None
    childGender: Optional[str] = None
    lastPeriodDate: Optional[datetime] = None
    periodEndDate: Optional[datetime] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class UserIn(BaseModel):
    name:str
    email:EmailStr
    password:str

class ExpertBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    fieldOfExpertise: str
    bio: Optional[str] = None
    isVerified: bool = False
    image: Optional[str] = None



class ExpertCreate(ExpertBase):
    password: str

class ExpertOut(ExpertBase):
    rating: float = 0.0
    coursesCreated: int = 0
    eventsCreated: int = 0
    sessionsHeld: int = 0

class Expert(ExpertBase):
    id:int
    rating: float = 0.0
    coursesCreated: int = 0
    eventsCreated: int = 0
    sessionsHeld: int = 0

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    location: str
    maxAttendees: Optional[int] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    attendees:Optional[list] = []
    expert: Optional[list] = None


    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: str
    category: str
    expertId: Optional[int] = None
    partnerId: Optional[int] = None
    organizationId: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class EnrollmentBase(BaseModel):
    userId: int
    courseId: int
    status: str = "in_progress"
    progress: int = 0

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int
    completedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    userId: int
    expertId: int
    startTime: datetime
    type: str
    notes: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int
    status: str = "scheduled"
    endTime: Optional[datetime] = None
    rating: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class UserUpdate(UserCreate):
    id:int


class EnrollmentUpdate(Enrollment):
    pass


class Progress(BaseModel):
    score:int


class EventUpdate(Event):
    pass


class CourseUpdate(Course):
    pass


class ExpertUpdate(Expert):
    pass


class SessionUpdate(Session):
    pass

class Partner(BaseModel):
    name:str
    email:EmailStr
    phone:str
    description:str | None
    website:str | None
    isVerified:bool


class PartnerIn(Partner):
    password:str


class PartnerOut(Partner):
    rating: float = 0.0
    coursesCreated: int = 0
    eventsCreated: int = 0
    sessionsHeld: int = 0

class Organization(BaseModel):
    name: str
    email: EmailStr
    phone: str
    description: str | None
    website: str | None
    isVerified: bool

class OrganizationIn(Organization):
    password:str


class OrganizationOut(Organization):
    rating: float = 0.0
    coursesCreated: int = 0
    eventsCreated: int = 0
    sessionsHeld: int = 0

class ChatRequest(BaseModel):
    message:str


