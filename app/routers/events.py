from fastapi import APIRouter, HTTPException, status
router = APIRouter(
    prefix="/events",
    tags=["auth"],
)

