from fastapi import APIRouter
from app.api.v1 import auth, diary, quote, question

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth")
api_v1_router.include_router(diary.router, prefix="/diary")
api_v1_router.include_router(quote.router, prefix="/quotes")
api_v1_router.include_router(question.router, prefix="/questions")
