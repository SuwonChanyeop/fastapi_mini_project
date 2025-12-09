from fastapi import APIRouter
import random

router = APIRouter(prefix="/questions", tags=["Questions API"])

SAMPLE_QUESTIONS = [
    "오늘 내가 가장 감사한 일은 무엇이었나요?",
    "지금 가장 하고 싶은 일은 무엇인가요?",
    "오늘 나를 힘들게 한 일은 무엇이었나요?",
    "내가 바꾸고 싶은 나의 습관은 무엇인가요?",
    "최근에 나를 웃게 만든 순간은 언제였나요?",
]


@router.get("/random")
async def random_question_json():
    return {"content": random.choice(SAMPLE_QUESTIONS)}
