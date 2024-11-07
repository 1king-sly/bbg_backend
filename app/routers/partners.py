from fastapi import APIRouter, HTTPException, status
router = APIRouter(
    prefix="/partners",
    tags=["auth"],
)

