from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import users, experts, sessions, events, courses, enrollments, auth
from prisma import Prisma
from db import prisma, connect_db, disconnect_db
app = FastAPI(title="BabyGal Backend API Routes")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
# app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Include all routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(experts.router, prefix="/api/experts", tags=["experts"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(enrollments.router, prefix="/api/enrollments", tags=["enrollments"])

# Database connection management
# Connect to the database before the application starts
@app.on_event("startup")
async def startup():
    await connect_db()

# Disconnect from the database when the application stops
@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/")
async def root():
    return {"message": "Hello From  Baby Gal"}