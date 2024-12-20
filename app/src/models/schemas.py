from pydantic import BaseModel, EmailStr, Field
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

class UserOut(UserBase):
    id: int
    role: str

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

class EventCreators(BaseModel):
    name:str


class Event(EventBase):
    id: int
    createdAt: datetime
    updatedAt: datetime
    attendees:Optional[list] = []
    expert: Optional[EventCreators] = None
    partner: Optional[EventCreators] = None
    organization: Optional[EventCreators] = None


    class Config:
        from_attributes = True


class EnrollmentBase(BaseModel):
    userId: int
    courseId: str
    status: str = "in_progress"
    progress: int = 0

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int
    completedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    course: Optional[list] | None = None


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

class QuestionBase(BaseModel):
    content: str
    options: List[str]
    correctAnswer: int = Field(ge=0)

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    quizId: int


    class Config:
        from_attributes = True

class QuizBase(BaseModel):
    questions: List[QuestionCreate]

class QuizCreate(QuizBase):
    pass

class QuizResponse(QuizBase):
    id: int
    moduleId: str
    questions: List[QuestionResponse]


    class Config:
        from_attributes = True

class QuizAttemptRequest(BaseModel):
    user_id: int
    answers: List[int]

class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    question_id: int
    answer: int
    is_correct: bool
    created_at: datetime

    class Config:
        from_attributes = True

class QuizSubmissionResponse(BaseModel):
    score: float
    attempts: List[QuizAttemptResponse]



class ModuleBase(BaseModel):
    title: str
    content: str
    videoUrl: Optional[str] = None
    order: int

class ModuleCreate(ModuleBase):
    Quiz: Optional[QuizCreate] = None

class ModuleResponse(ModuleBase):
    id: str
    courseId: str
    Quiz: Optional[QuizResponse] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: str
    category: str
    max_enrollments: int = Field(default=100, ge=1)

class CourseCreate(CourseBase):
    modules: List[ModuleCreate]

class CourseResponse(CourseBase):
    id: str
    expertId: Optional[int] | None = None
    partnerId: Optional[int] | None = None
    organizationId:Optional[int] | None = None
    enrollments: Optional[list] | None = None
    modules:Optional[list] | None = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class CourseEnrollmentRequest(BaseModel):
    user_id: int
    course_id: int

class CourseEnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str
    progress: int
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ModuleProgressUpdate(BaseModel):
    user_id: int
    is_completed: bool

class ModuleProgressResponse(BaseModel):
    id: int
    user_id: int
    module_id: int
    is_completed: bool
    is_locked: bool
    last_accessed: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NextModule(BaseModel):
    index:int

