from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    """
    bcrypt는 72바이트(= 영어 72자, 한글 약 24자) 이상 비밀번호를 처리하지 못함.
    길이가 초과되면 자동으로 72바이트까지만 잘라서 해싱하도록 처리.
    """
    password_bytes = password.encode("utf-8")

    # 72바이트 초과하면 자동 자르기
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    safe_password = password_bytes.decode("utf-8", "ignore")
    return pwd_context.hash(safe_password)


# JWT 토큰 생성 (24시간 유지)
def create_access_token(subject: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

