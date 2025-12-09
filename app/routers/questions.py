from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import random

from app.db.session import get_db
from app.repositories.user_repo import get_user_by_id
from app.core.config import settings

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/questions", tags=["Questions"])

SAMPLE_QUESTIONS = [
    "오늘 내가 가장 감사한 일은 무엇이었나요?",
    "지금 가장 하고 싶은 일은 무엇인가요?",
    "오늘 나를 힘들게 한 일은 무엇이었나요?",
    "내가 바꾸고 싶은 나의 습관은 무엇인가요?",
    "최근에 나를 웃게 만든 순간은 언제였나요?",
]


#  쿠키 기반 로그인 사용자 확인
def get_logged_in_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = int(payload.get("sub"))
    except JWTError:
        return None

    return get_user_by_id(db, user_id)


#  HTML 페이지 (로그인 유지 포함)
@router.get("/", response_class=HTMLResponse)
async def questions_page(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)
    question = random.choice(SAMPLE_QUESTIONS)

    return templates.TemplateResponse(
        "questions.html",
        {
            "request": request,
            "user": user,  
            "question": question,
        }
    )
