from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.repositories.question_repo import get_random_question
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/questions", tags=["Questions"])
templates = Jinja2Templates(directory="app/templates")


# -------------------------
#   로그인 유저 가져오기
# -------------------------
def get_logged_in_user(request: Request, db: Session) -> User | None:
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
    except (JWTError, TypeError, ValueError):
        return None

    return db.query(User).get(user_id)


# -------------------------
#   질문 UI 페이지
# -------------------------
@router.get("/", response_class=HTMLResponse)
def questions_page(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)

    question = get_random_question(db)
    question_text = question.text if question else None

    return templates.TemplateResponse(
        "questions/random.html",
        {
            "request": request,
            "user": user, 
            "question_text": question_text,
        },
    )
