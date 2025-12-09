# app/api/v1/diary.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.diary import (
    DiaryCreate,
    DiaryUpdate,
    DiaryResponse,
    DiaryListResponse,
)
from app.services import diary_service

router = APIRouter(prefix="/diaries", tags=["diaries"])


@router.post("", response_model=DiaryResponse, status_code=201)
def create_diary(
    payload: DiaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diary = diary_service.create_diary(db, current_user, payload)
    return diary


@router.get("", response_model=DiaryListResponse)
def list_diaries(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * size
    items, total = diary_service.list_diaries_for_user(
        db, current_user, skip=skip, limit=size
    )
    return DiaryListResponse(items=items, total=total)


@router.get("/{diary_id}", response_model=DiaryResponse)
def get_diary(
    diary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diary = diary_service.get_diary_or_404(db, diary_id)
    # 조회 권한은 "본인 것만 볼지, 아닐지" 정책에 따라 아래 한 줄 추가/제거
    diary_service.ensure_owner(diary, current_user)
    return diary


@router.patch("/{diary_id}", response_model=DiaryResponse)
def update_diary(
    diary_id: int,
    payload: DiaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diary = diary_service.get_diary_or_404(db, diary_id)
    diary = diary_service.update_diary(db, diary, current_user, payload)
    return diary


@router.delete("/{diary_id}", status_code=204)
def delete_diary(
    diary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    diary = diary_service.get_diary_or_404(db, diary_id)
    diary_service.delete_diary(db, diary, current_user)
    return
