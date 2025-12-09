from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    author = Column(String(100), nullable=True)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    bookmarks = relationship(
        "QuoteBookmark",
        back_populates="quote",
        cascade="all, delete-orphan",
    )


class QuoteBookmark(Base):
    __tablename__ = "quote_bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "quote_id", name="uq_user_quote_bookmark"),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    quote_id = Column(
        Integer,
        ForeignKey("quotes.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship(
        "User",
        back_populates="bookmarks",
    )

    quote = relationship(
        "Quote",
        back_populates="bookmarks",
    )
