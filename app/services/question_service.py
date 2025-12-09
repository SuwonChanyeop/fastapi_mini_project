from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.question import Question
from app.repositories import question_repo


def get_random_question(db: Session) -> Question:
    question = question_repo.get_random_question(db)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions available",
        )
    return question
