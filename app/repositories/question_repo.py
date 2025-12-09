from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.question import Question


def get_random_question(db: Session) -> Optional[Question]:
    return db.query(Question).order_by(func.random()).first()
