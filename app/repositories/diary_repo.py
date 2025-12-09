from typing import List, Tuple, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.diary import Diary
from app.schemas.diary import DiaryCreate, DiaryUpdate


def create_diary(db: Session, user_id: int, data: DiaryCreate) -> Diary:
    diary = Diary(
        user_id=user_id,
        title=data.title,
        content=data.content,
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    return diary


def get_diary_by_id(db: Session, diary_id: int) -> Optional[Diary]:
    return db.query(Diary).filter(Diary.id == diary_id).first()


def list_diaries_by_user(
    db: Session,
    user_id: int,
    *,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Diary], int]:
    q = db.query(Diary).filter(Diary.user_id == user_id)
    total = q.count()
    items = q.order_by(Diary.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def update_diary(db: Session, diary: Diary, data: DiaryUpdate) -> Diary:
    if data.title is not None:
        diary.title = data.title
    if data.content is not None:
        diary.content = data.content

    db.add(diary)
    db.commit()
    db.refresh(diary)
    return diary


def delete_diary(db: Session, diary: Diary) -> None:
    db.delete(diary)
    db.commit()
