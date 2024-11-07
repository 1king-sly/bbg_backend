from fastapi import APIRouter, HTTPException, status
router = APIRouter(
    prefix="/organizations",
    tags=["auth"],
)

