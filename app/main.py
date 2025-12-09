from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.routers import api_v1_router

from app.routers.front import router as front_router
from app.routers.quotes import router as quotes_router
from app.routers.questions import router as questions_router

from app.db.session import engine
from app.models import Base

app = FastAPI(title="FastAPI Mini Project")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# HTML 페이지 라우터들
app.include_router(front_router)
app.include_router(quotes_router)
app.include_router(questions_router)

# API v1 라우터
app.include_router(api_v1_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
