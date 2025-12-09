from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.question_repo import get_random_question

router = APIRouter(tags=["Questions"])

@router.get("/random")
def random_question(db: Session = Depends(get_db)):
    question = get_random_question(db)
    if not question:
        raise HTTPException(status_code=404, detail="No questions in DB")
    return {"id": question.id, "text": question.text}

