from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.src.auth.auth import get_current_user
from app.src.models.schemas import CourseCreate, Course, CourseUpdate
from prisma import Prisma

router = APIRouter()
prisma = Prisma()

@router.post("/", response_model=Course)
async def create_course(course: CourseCreate, current_user = Depends(get_current_user)):
    if current_user.role not in ["ADMIN", "EXPERT"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        db_course = await prisma.course.create(
            data = course.model_dump()
        )
        return db_course
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Course])
async def list_courses():
    return await prisma.course.find_many(include={
        "expert": True,
        "modules": True
    })

@router.get("/{course_id}", response_model=Course)
async def read_course(course_id: int):
    course = await prisma.course.find_unique(
        where={"id": course_id},
        include={
            "expert": True,
            "modules": True
        }
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user = Depends(get_current_user)
):
    course = await prisma.course.find_unique(where={"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if current_user.role != "ADMIN" and course.expertId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        updated_course = await prisma.course.update(
            where={"id": course_id},
            data=course_update.dict(exclude_unset=True)
        )
        return updated_course
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))