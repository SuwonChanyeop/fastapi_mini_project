from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.schemas.user import (
    UserSignupRequest,
    UserResponse,
    Token,
    TokenPayload,
)
from app.repositories.user_repo import (
    get_user_by_email,
    get_user_by_id,
    create_user,
)
from app.models.user import User
from app.db.session import get_db


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# --------------------------------------------------
# JWT 토큰으로 로그인 사용자 확인
# --------------------------------------------------
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_data = TokenPayload(**payload)

    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, int(token_data.sub))

    if not user:
        raise credentials_exception

    return user


# --------------------------------------------------
# 회원가입
# --------------------------------------------------
@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(payload: UserSignupRequest, db: Session = Depends(get_db)):

    exist = get_user_by_email(db, payload.email)
    if exist:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(payload.password)

    user = create_user(
        db,
        email=payload.email,
        password=hashed_pw,
        nickname=payload.nickname,
        name=payload.name,
        phone=payload.phone,
    )

    return user


# --------------------------------------------------
# 로그인 (Access Token만 발급)
# --------------------------------------------------
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access = create_access_token(subject=str(user.id))

    return Token(access_token=access, refresh_token=None)


# --------------------------------------------------
# 내 정보 조회
# --------------------------------------------------
@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
