from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# -------------------------------------------------------------------
# 비밀번호 해시 설정 (pbkdf2_sha256 사용)
# -------------------------------------------------------------------
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


# -------------------------------------------------------------------
# 비밀번호 해시 생성
# -------------------------------------------------------------------
def hash_password(password: str) -> str:
    """평문 비밀번호를 안전하게 해시"""
    return pwd_context.hash(password)


# -------------------------------------------------------------------
# 비밀번호 검증
# -------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    로그인 시 입력한 평문 비밀번호와
    DB에 저장된 해시가 일치하는지 비교
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False   # 예외를 False 처리하여 로그인 실패 유도


# -------------------------------------------------------------------
# JWT 토큰 생성
# -------------------------------------------------------------------
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT Access Token 생성 함수
    data: 반드시 dict 형태여야 함. 예) {"sub": "1"}
    """

    # payload 반드시 copy()로 분리
    to_encode = data.copy()

    # 만료 시간
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    # 토큰 생성
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
