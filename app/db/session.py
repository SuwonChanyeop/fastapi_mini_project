from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# SQLAlchemy 2.0 스타일 엔진
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False,  # 필요하면 True로
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
