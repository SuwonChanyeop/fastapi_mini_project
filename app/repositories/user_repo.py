from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    nickname: str | None = None,
    name: str | None = None,
    phone: str | None = None,
) -> User:
    user = User(
        email=email,
        password=password,
        nickname=nickname,
        name=name,
        phone=phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
