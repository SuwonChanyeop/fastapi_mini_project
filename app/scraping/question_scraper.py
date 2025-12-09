import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.question import Question

TARGET_URL = "https://media-jotter.tistory.com/entry/%EC%8D%B8%EB%82%A8-%EC%8D%B8%EB%85%80-%EB%8C%80%ED%99%94-%EC%A3%BC%EC%A0%9C-%ED%98%B8%EA%B0%90%EC%9D%84-%EB%86%92%EC%9D%B4%EB%8A%94-%EC%A7%88%EB%AC%B8-50%EA%B0%80%EC%A7%80-%EB%AA%A8%EC%9D%8C"


def fetch_page() -> str:
    print(f"[QUESTION SCRAPER] Fetching from: {TARGET_URL}")
    resp = requests.get(TARGET_URL, timeout=10)
    resp.raise_for_status()
    return resp.text


def parse_questions(html: str) -> list[str]:
    """
    - 페이지 내 모든 <li>에서 텍스트 추출
    - 최소 1글자 이상의 한글 포함된 문장만 사용
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[str] = []

    for li in soup.select("li"):
        text = li.get_text(" ", strip=True)
        if not text:
            continue
        if len(text) < 4:
            continue

        if not any("가" <= ch <= "힣" for ch in text):
            continue

        results.append(text)

    return results


def save_questions(db: Session, questions: list[str]) -> int:
    added = 0

    for q_text in questions:
        exists = db.query(Question).filter(Question.text == q_text).first()
        if exists:
            continue

        q = Question(text=q_text)
        db.add(q)
        added += 1

    if added > 0:
        db.commit()

    return added


def scrape_questions() -> None:
    """
    전체 흐름:
    1) 한국어 질문 페이지에서 HTML 가져오기
    2) 질문 문장 리스트로 파싱
    3) questions 테이블에 저장
    """
    html = fetch_page()
    questions = parse_questions(html)
    print(f"[QUESTION SCRAPER] Parsed {len(questions)} Korean questions")

    if not questions:
        print("[QUESTION SCRAPER] No questions parsed. (0개) – 사이트 구조가 바뀐 것일 수 있습니다.")
        return

    db = SessionLocal()
    try:
        added = save_questions(db, questions)
        print(f"[QUESTION SCRAPER] Added {added} new questions to DB")
    finally:
        db.close()

    print("[QUESTION SCRAPER] Done.")


if __name__ == "__main__":
    scrape_questions()
