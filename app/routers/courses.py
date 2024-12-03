from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.src.auth.auth import get_current_user
from app.src.models.schemas import CourseCreate, CourseResponse
from db import prisma

router = APIRouter()

@router.post("/", response_model=CourseResponse)
async def create_course(course: CourseCreate, current_user = Depends(get_current_user)):
    if current_user.role not in ["ADMIN", "EXPERT","PARTNER","ORGANIZATION"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:


        course =  prisma.course.create(
            data = {
                "expertId": current_user.id if current_user.role == "EXPERT" else None,
                "partnerId": current_user.id if current_user.role == "PARTNER" else None,
                "organizationId": current_user.id if current_user.role == "ORGANIZATION" else None,
                'title': course.title,
                'description': course.description,
                "category": course.category,
                "modules": {
                "create": [
                    {
                        "title": module.title,
                        "content": module.content,
                        "videoUrl": module.videoUrl,
                        "order": module.order,
                        "Quiz": {
                            "create": {
                                "questions": {
                                    "create": [
                                        {
                                            "content": question.question,
                                            "options": question.options,
                                            "correctAnswer": question.correctAnswer,
                                        }
                                        for question in module.Quiz.questions
                                    ]
                                }
                            }
                        } if module.quiz else {},
                    }
                    for module in course.modules
                ]
            },
            },
            include={"modules": {"include": {"Quiz": True}}},

        )
        return course
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CourseResponse])
async def list_courses():
    return  prisma.course.find_many(include={
        "expert": True,
        "modules": {
                "include": {
                    "Quiz": {
                        "include": {
                            "questions": True
                        }
                    }
                }
            },
        "enrollments":True,
    })


@router.get("/created", response_model=List[CourseResponse])
async def list_courses_created_by_me(current_user = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(status_code=404, detail="User does not exist")


    if current_user.role not in ["ADMIN", "EXPERT","ORGANIZATION","PARTNER"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return  prisma.course.find_many(
        where={
            "expertId": current_user.id if current_user.role == "EXPERT" else None,
            "partnerId": current_user.id if current_user.role == "PARTNER" else None,
            "organizationId": current_user.id if current_user.role == "ORGANIZATION" else None,
        },
        include={
        "expert": True,
        "modules": {
                "include": {
                    "Quiz": {
                        "include": {
                            "questions": True
                        }
                    }
                }
            },
        "enrollments":True,
    })
@router.get("/{course_id}", response_model=CourseResponse)
async def read_course(course_id: int):
    course =  prisma.course.find_unique(
        where={"id": course_id},
        include={
            "expert": True,
            "modules": True
        }
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseCreate,
    current_user = Depends(get_current_user)
):
    course =  prisma.course.find_unique(where={"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if current_user.role != "ADMIN" and course.expertId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        updated_course =  prisma.course.update(
            where={"id": course_id},
            data=course_update.dict(exclude_unset=True)
        )
        return updated_course
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))