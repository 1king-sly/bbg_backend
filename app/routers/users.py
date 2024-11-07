from fastapi import APIRouter, HTTPException, status
router = APIRouter(
    prefix="/users",
    tags=["auth"],
)

