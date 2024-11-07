from fastapi import APIRouter, HTTPException, status
router = APIRouter(
    prefix="/courses",
    tags=["auth"],
)

