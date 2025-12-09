# app/repositories/quote_repo.py
from typing import Optional, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.quote import Quote, QuoteBookmark


# -------------------------
# 기본 명언 관련 함수
# -------------------------
def get_random_quote(db: Session) -> Optional[Quote]:
    return db.query(Quote).order_by(func.random()).first()


def get_quote_by_id(db: Session, quote_id: int) -> Optional[Quote]:
    return db.query(Quote).filter(Quote.id == quote_id).first()


# -------------------------
# 북마크(QuoteBookmark) 관련 기본 함수
# -------------------------
def get_bookmark(
    db: Session,
    user_id: int,
    quote_id: int,
) -> Optional[QuoteBookmark]:
    return (
        db.query(QuoteBookmark)
        .filter(
            QuoteBookmark.user_id == user_id,
            QuoteBookmark.quote_id == quote_id,
        )
        .first()
    )


def create_bookmark(db: Session, user_id: int, quote_id: int) -> QuoteBookmark:
    """명언 북마크 생성 (이미 있으면 기존 북마크 반환)"""
    bookmark = QuoteBookmark(user_id=user_id, quote_id=quote_id)
    db.add(bookmark)
    try:
        db.commit()
        db.refresh(bookmark)
        return bookmark
    except IntegrityError:
        # 이미 같은 (user_id, quote_id)가 있을 때 여기로 옴
        db.rollback()
        return (
            db.query(QuoteBookmark)
            .filter(
                QuoteBookmark.user_id == user_id,
                QuoteBookmark.quote_id == quote_id,
            )
            .first()
        )


def delete_bookmark_by_id(
    db: Session,
    user_id: int,
    bookmark_id: int,
) -> bool:
    bookmark = (
        db.query(QuoteBookmark)
        .filter(
            QuoteBookmark.id == bookmark_id,
            QuoteBookmark.user_id == user_id,
        )
        .first()
    )

    if not bookmark:
        return False

    db.delete(bookmark)
    db.commit()
    return True


def list_bookmarks(
    db: Session,
    user_id: int,
    *,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[QuoteBookmark], int]:
    q = db.query(QuoteBookmark).filter(QuoteBookmark.user_id == user_id)
    total = q.count()
    items = (
        q.order_by(QuoteBookmark.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items, total


# -------------------------
# HTML 라우터용 래퍼
# -------------------------
def create_quote_bookmark(db: Session, user_id: int, quote_id: int) -> QuoteBookmark:
    return create_bookmark(db, user_id, quote_id)


def get_user_quote_bookmarks(db: Session, user_id: int) -> List[QuoteBookmark]:
    return (
        db.query(QuoteBookmark)
        .filter(QuoteBookmark.user_id == user_id)
        .order_by(QuoteBookmark.created_at.desc())
        .all()
    )


def delete_quote_bookmark(db: Session, bookmark_id: int, user_id: int) -> bool:
    return delete_bookmark_by_id(db, user_id=user_id, bookmark_id=bookmark_id)
