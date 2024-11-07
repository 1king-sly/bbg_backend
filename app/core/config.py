from typing import List
from pydantic import BaseSettings, AnyHttpUrl
from decouple import config

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "BabyGal NGO API"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # FastAPI backend
    ]
    
    # Database Configuration
    DATABASE_URL: str = config("DATABASE_URL", cast=str)
    
    # JWT Configuration
    SECRET_KEY: str = config("SECRET_KEY", cast=str)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str = config("SMTP_USER", cast=str)
    SMTP_PASSWORD: str = config("SMTP_PASSWORD", cast=str)
    
    class Config:
        case_sensitive = True

settings = Settings()