from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.src.auth.auth  import get_current_user
from app.src.models.schemas import  Enrollment,  Progress
from db import prisma

router = APIRouter()

@router.post("/courses/{course_id}", response_model=Enrollment)
async def enroll_in_course(course_id: int, current_user = Depends(get_current_user)):
    try:
        enrollment =  prisma.enrollment.create(
            data={
                "userId": current_user.id,
                "courseId": course_id,
                "status": "in_progress"
            }
        )
        return enrollment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-courses", response_model=List[Enrollment])
async def list_my_enrollments(current_user = Depends(get_current_user)):
    return  prisma.enrollment.find_many(
        where={"userId": current_user.id},
        include={
            "course": True,
            "progress": True
        }
    )

@router.post("/progress", response_model=Progress)
async def update_progress(
    module_id: int,
    completed: bool,
    score: int = None,
    current_user = Depends(get_current_user)
):
    try:
        progress =  prisma.progress.create(
            data = {
                "userId": current_user.id,
                "moduleId": module_id,
                "completed": completed,
                "score": score
            }
        )
        
        # Update enrollment progress
        module =  prisma.module.find_unique(
            where={"id": module_id},
            include={"course": True}
        )
        
        total_modules =  prisma.module.count(
            where={"courseId": module.courseId}
        )

        completed_modules =  prisma.progress.count(
            where={
                "AND": [
                    {"userId": current_user.id},
                    {"completed": True},
                    {"module": {"courseId": module.courseId}}
                ]
            }
        )
        
        progress_percentage = (completed_modules / total_modules) * 100

        enrollment =  prisma.enrollment.find_first(
            where={
                "userId": current_user.id,
                "courseId": module.courseId
            }
        )

        # Check if the enrollment exists
        if enrollment is None:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        await prisma.enrollment.update(
            where={"id": enrollment.id},
            data={
                "progress": int(progress_percentage),
                "status": "completed" if progress_percentage == 100 else "in_progress"
            }
        )
        
        return progress
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))