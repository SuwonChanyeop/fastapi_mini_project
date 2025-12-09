from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ------------------------
# 회원가입
# ------------------------
@router.post("/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    
    user = User(
        email=email,
        password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "ok"}


# ------------------------
# 로그인
# ------------------------
@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1) 이메일로 유저 찾기
    user: User | None = (
        db.query(User).filter(User.email == email).first()
    )
    if not user:
        return RedirectResponse(
            request.url_for("login_page"),
            status_code=303,
        )

    # 2) 비밀번호 검증
    if not verify_password(password, user.password):
        return RedirectResponse(
            request.url_for("login_page"),
            status_code=303,
        )

    # 3) 토큰 발급 & 쿠키 저장
    access_token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(
        request.url_for("diary_list"),
        status_code=303,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response
