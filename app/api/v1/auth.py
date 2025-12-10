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

    # 🔹 인증 실패 시 메시지: 설계서대로 한글로 통일
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="로그인이 필요합니다.",
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_data = TokenPayload(**payload)

    except JWTError:
        # 토큰이 없거나 / 잘못되었거나 / 만료된 경우
        raise credentials_exception

    user = get_user_by_id(db, int(token_data.sub))

    if not user:
        # 토큰은 맞는데 유저가 삭제된 경우 등
        raise credentials_exception

    return user


# --------------------------------------------------
# 회원가입
# --------------------------------------------------
@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(payload: UserSignupRequest, db: Session = Depends(get_db)):

    # 🔹 (1) 비밀번호 규칙 검사
    # - 길이 6자 이상
    # - 영어 + 숫자 모두 포함
    password = payload.password

    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 너무 짧습니다. 6자 이상이어야 합니다.",
        )

    has_alpha = any(ch.isalpha() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)

    if not (has_alpha and has_digit):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호 형식이 올바르지 않습니다. 영어와 숫자를 모두 포함해야 합니다.",
        )

    # 🔹 (2) 이메일 중복 체크
    exist = get_user_by_email(db, payload.email)
    if exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="중복된 아이디(이메일)입니다.",
        )

    # 🔹 (3) 비밀번호 해시 후 저장
    # DB 컬럼 이름은 password지만, 실제로는 해시된 값만 저장 (설계서 내용과 일치)
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

    # OAuth2PasswordRequestForm의 username 필드를 이메일로 사용
    user = get_user_by_email(db, form_data.username)

    # 🔹 로그인 실패 메시지: 설계서에 적어둔 문장으로 통일
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    # JWT Access Token 발급 (sub에 유저 id 저장)
    access = create_access_token(subject=str(user.id))

    # Refresh 토큰은 이번 프로젝트에선 사용 안 함 → None
    return Token(access_token=access, refresh_token=None)


# --------------------------------------------------
# 내 정보 조회
# --------------------------------------------------
@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    # 헤더에 토큰을 넣어 호출하면 현재 로그인한 유저 정보 반환
    return current_user
