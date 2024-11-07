from fastapi import APIRouter, HTTPException, status
router = APIRouter(
    prefix="/sessions",
    tags=["auth"],
)

