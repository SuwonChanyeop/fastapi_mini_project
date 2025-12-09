from fastapi import APIRouter

# ──────────────────────────────────────────
# 각 도메인 라우터 임포트
# ──────────────────────────────────────────
from app.api.v1.auth import router as auth_router
from app.api.v1.diary import router as diary_router
from app.api.v1.quote import router as quote_router
from app.api.v1.question import router as question_router

api_v1_router = APIRouter()

# ──────────────────────────────────────────
# v1 엔드포인트 등록
# ──────────────────────────────────────────
api_v1_router.include_router(auth_router, prefix="/auth")
api_v1_router.include_router(diary_router, prefix="/diary")
api_v1_router.include_router(quote_router, prefix="/quotes")
api_v1_router.include_router(question_router, prefix="/questions")
