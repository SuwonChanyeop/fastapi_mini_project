from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=True)
    name = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    diaries = relationship(
        "Diary",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    bookmarks = relationship(
        "QuoteBookmark",
        back_populates="user",
        cascade="all, delete-orphan",
    )

