from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.routers import api_v1_router
from app.routers.front import router as front_router
from app.routers.quotes import router as quotes_router
from app.routers.questions import router as questions_router

from app.db.session import engine
from app.models import Base

# --------------------------------------
# 경로 설정
# --------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------
# FastAPI 앱 생성
# --------------------------------------
app = FastAPI(title="FastAPI Mini Project")

# static 파일
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

# templates 생성
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --------------------------------------
#   KST 필터 등록
# --------------------------------------
KST = timezone(timedelta(hours=9))

def to_kst(dt: Optional[datetime]):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST)

def datetime_format(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M"):
    if dt is None:
        return ""
    return dt.strftime(fmt)

# Jinja2 필터 등록
templates.env.filters["to_kst"] = to_kst
templates.env.filters["datetime_format"] = datetime_format

# --------------------------------------
#   DB 생성
# --------------------------------------
Base.metadata.create_all(bind=engine)

# --------------------------------------
#   라우터 등록
# --------------------------------------
app.include_router(front_router)
app.include_router(quotes_router)
app.include_router(questions_router)
app.include_router(api_v1_router, prefix="/api/v1")
