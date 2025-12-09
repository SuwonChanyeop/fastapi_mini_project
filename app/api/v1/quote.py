from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import random

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

QUOTES = [
    "작은 성공을 계속 쌓아라.",
    "행동하지 않으면 아무 일도 일어나지 않는다.",
    "성공은 매일 반복하는 작은 습관에서 온다.",
    "지금 하는 선택이 내 미래를 만든다.",
]

# API: JSON
@router.get("/random")
async def quote_random_api():
    return {"content": random.choice(QUOTES)}

# PAGE: HTML UI
@router.get("/page", response_class=HTMLResponse)
async def quote_random_page(request: Request):
    quote = random.choice(QUOTES)
    return templates.TemplateResponse(
        "quote_random.html",
        {"request": request, "quote": quote}
    )
