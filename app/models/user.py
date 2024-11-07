from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="USER")
    phone = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    is_pregnant = Column(Boolean, default=False)
    pregnancy_date = Column(DateTime, nullable=True)
    has_child = Column(Boolean, default=False)
    child_birth_date = Column(DateTime, nullable=True)
    child_gender = Column(String, nullable=True)
    last_period_date = Column(DateTime, nullable=True)
    period_end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events = relationship("Event", secondary="user_events")
    enrollments = relationship("Enrollment", back_populates="user")
    menstrual_cycles = relationship("MenstrualCycle", back_populates="user")
    messages = relationship("Message", back_populates="sender")
    sessions = relationship("Session", back_populates="user")