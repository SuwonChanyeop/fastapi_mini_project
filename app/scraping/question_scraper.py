from typing import List

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.question import Question


# 예시 자기성찰 질문들
DEFAULT_QUESTIONS: List[tuple[str, str | None]] = [
    ("오늘 하루 중 가장 감사했던 순간은 무엇이었나요?", "일상"),
    ("최근에 나를 가장 힘들게 했던 일은 무엇이며, 거기서 무엇을 배웠나요?", "자기성찰"),
    ("지금 나에게 가장 소중한 사람은 누구이며, 그 이유는 무엇인가요?", "관계"),
    ("1년 뒤 내가 어떤 모습이었으면 좋겠는지 떠올려 보세요.", "미래"),
    ("최근에 내가 했던 선택 중 가장 잘했다고 느끼는 것은 무엇인가요?", "선택"),
    ("오늘 나 자신을 위해 해줄 수 있는 작은 선물은 무엇인가요?", "자기돌봄"),
]


def save_questions(db: Session, questions: List[tuple[str, str | None]]) -> int:
    """
    (text, category) 리스트를 DB에 저장.
    text 중복은 건너뜁니다.
    """
    added = 0
    for text, category in questions:
        exists = db.query(Question).filter(Question.text == text).first()
        if exists:
            continue

        q = Question(text=text, category=category)
        db.add(q)
        added += 1

    if added:
        db.commit()
    return added


def load_default_questions() -> None:
    db = SessionLocal()
    try:
        added = save_questions(db, DEFAULT_QUESTIONS)
        print(f"[QUESTION LOADER] Added {added} questions.")
    finally:
        db.close()


if __name__ == "__main__":
    load_default_questions()
