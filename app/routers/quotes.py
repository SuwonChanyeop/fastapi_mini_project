# app/routers/quotes.py
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.repositories.user_repo import get_user_by_id
from app.repositories.quote_repo import (
    get_random_quote,
    create_quote_bookmark,
    get_user_quote_bookmarks,
    delete_quote_bookmark,
)
from app.core.config import settings

router = APIRouter(prefix="/quotes", tags=["Quotes"])
templates = Jinja2Templates(directory="app/templates")


# 로그인 유저
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


# GET /quotes  → 오늘의 명언 페이지
@router.get("/", response_class=HTMLResponse)
async def quotes_main_page(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_logged_in_user(request, db)
    quote = get_random_quote(db)
    return templates.TemplateResponse(
        "quote_random.html",
        {
            "request": request,
            "user": user,
            "quote": quote,
        },
    )


# GET /quotes/random → JSON
@router.get("/random")
async def random_quote_json(db: Session = Depends(get_db)):
    quote = get_random_quote(db)
    if not quote:
        return {"id": None, "content": None, "author": None}
    return {
        "id": quote.id,
        "content": quote.text,
        "author": quote.author,
    }


# GET /quotes/random/page → 새로고침용 HTML
@router.get("/random/page", response_class=HTMLResponse)
async def random_quote_page(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_logged_in_user(request, db)
    quote = get_random_quote(db)
    return templates.TemplateResponse(
        "quote_random.html",
        {
            "request": request,
            "user": user,
            "quote": quote,
        },
    )


# POST /quotes/bookmark → 북마크 추가
@router.post("/bookmark")
async def add_quote_bookmark(
    request: Request,
    quote_id: int = Form(...),
    db: Session = Depends(get_db),
):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(
            url="/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    create_quote_bookmark(db, user.id, quote_id)

    return RedirectResponse(
        url="/quotes/bookmarks",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# GET /quotes/bookmarks → 북마크 목록 페이지
@router.get("/bookmarks", response_class=HTMLResponse)
async def quote_bookmarks_page(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(
            url="/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    bookmarks = get_user_quote_bookmarks(db, user.id)

    return templates.TemplateResponse(
        "quote_bookmarks.html",
        {
            "request": request,
            "user": user,
            "bookmarks": bookmarks,
        },
    )


# POST /quotes/bookmarks/{bookmark_id}/delete → 북마크 삭제
@router.post("/bookmarks/{bookmark_id}/delete")
async def delete_quote_bookmark_view(
    bookmark_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_logged_in_user(request, db)
    if not user:
        return RedirectResponse(
            url="/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    delete_quote_bookmark(db, bookmark_id, user.id)

    return RedirectResponse(
        url="/quotes/bookmarks",
        status_code=status.HTTP_303_SEE_OTHER,
    )
