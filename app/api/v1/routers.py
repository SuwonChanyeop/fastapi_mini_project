from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.diary import router as diary_router
from app.api.v1.question import router as questions_router
from app.api.v1.quote import router as quotes_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(diary_router)
api_v1_router.include_router(questions_router)
api_v1_router.include_router(quotes_router)
