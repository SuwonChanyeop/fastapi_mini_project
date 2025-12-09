from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.diary import Diary
from app.repositories import diary_repo
from app.schemas.diary import DiaryCreate, DiaryUpdate


def create_diary(db: Session, current_user: User, data: DiaryCreate) -> Diary:
    return diary_repo.create_diary(db, user_id=current_user.id, data=data)


def get_diary_or_404(db: Session, diary_id: int) -> Diary:
    diary = diary_repo.get_diary_by_id(db, diary_id)
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diary not found")
    return diary


def ensure_owner(diary: Diary, user: User) -> None:
    if diary.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )


def list_diaries_for_user(
    db: Session,
    current_user: User,
    *,
    skip: int = 0,
    limit: int = 20,
):
    return diary_repo.list_diaries_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


def update_diary(
    db: Session,
    diary: Diary,
    current_user: User,
    data: DiaryUpdate,
) -> Diary:
    ensure_owner(diary, current_user)
    return diary_repo.update_diary(db, diary, data)


def delete_diary(
    db: Session,
    diary: Diary,
    current_user: User,
) -> None:
    ensure_owner(diary, current_user)
    diary_repo.delete_diary(db, diary)
