from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# --- 공통 베이스 ---
class UserBase(BaseModel):
    email: EmailStr


# --- Request 스키마 ---

class UserSignupRequest(UserBase):
    password: str
    nickname: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Response 스키마 ---

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # ORM -> 스키마 변환용

    id: int
    email: EmailStr
    nickname: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user id (string으로 저장)
    exp: int
