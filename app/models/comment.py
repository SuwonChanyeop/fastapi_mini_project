from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = {"extend_existing": True}  # 🔥 이미 같은 테이블이 있어도 덮어써라

    id = Column(Integer, primary_key=True, index=True)
    diary_id = Column(Integer, ForeignKey("diaries.id"))  # Diary의 __tablename__ = "diaries"
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    diary = relationship("Diary", back_populates="comments")
