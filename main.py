from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, experts, sessions, events, courses, enrollments, auth, partners, organizations,chat
from db import  connect_db, disconnect_db
import subprocess

from prisma import Prisma

prisma = Prisma()

app = FastAPI(title="BabyGal Backend API Routes")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(experts.router, prefix="/api/experts", tags=["experts"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(courses.router, prefix="/api/courses", tags=["courses"])
app.include_router(partners.router, prefix="/api/partners", tags=["Partners"])
app.include_router(organizations.router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(enrollments.router, prefix="/api/enrollments", tags=["enrollments"])

app.include_router(chat.router)

@app.on_event("startup")

async def startup():
    await connect_db()


async def generate_prisma_client():
    try:
        subprocess.run(["prisma", "generate"], check=True)
        print("Prisma client generated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating Prisma client: {e}")




# Disconnect from the database when the application stops
@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/")
async def root():
    return {"message": "Hello From  Baby Gal Backend Team"}


