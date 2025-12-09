from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.question import Question


def get_random_question(db: Session) -> Optional[Question]:
    """DB에서 랜덤 질문 하나 가져오기"""
    return db.query(Question).order_by(func.random()).first()
