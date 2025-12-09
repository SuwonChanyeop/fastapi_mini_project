import re
import requests
from bs4 import BeautifulSoup

from app.db.session import SessionLocal
from app.models.question import Question


TARGET_URL = (
    "https://media-jotter.tistory.com/entry/"
    "%EC%8D%B8%EB%82%A8-%EC%8D%B8%EB%85%80-%EB%8C%80%ED%99%94-%EC%A3%BC%EC%A0%9C-"
    "%ED%98%B8%EA%B0%90%EC%9D%84-%EB%86%92%EC%9D%B4%EB%8A%94-%EC%A7%88%EB%AC%B8-50%EA%B0%80%EC%A7%80-%EB%AA%A8%EC%9D%8C"
)


def contains_hangul(text: str) -> bool:
    """문장 안에 한글이 1글자라도 있으면 True"""
    return any("가" <= ch <= "힣" for ch in text)


def clean_number_prefix(text: str) -> str:
    """'1. ~', '01) ~' 같은 번호 제거"""
    return re.sub(r"^\s*\d+\s*[.)]\s*", "", text)


def fetch_page() -> str:
    print(f"[QUESTION SCRAPER] Fetching from: {TARGET_URL}")
    resp = requests.get(TARGET_URL, timeout=10)
    resp.raise_for_status()
    return resp.text


def parse_questions(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[str] = []

    for li in soup.select("li"):
        text = li.get_text(" ", strip=True)

        if not text:
            continue
        if len(text) < 4:
            continue
        if not contains_hangul(text):
            continue

        text = clean_number_prefix(text)
        results.append(text)

    print(f"[QUESTION SCRAPER] Parsed {len(results)} Korean questions.")
    return results


def save_to_db(questions: list[str]) -> int:
    print("[QUESTION SCRAPER] Saving to DB ...")
    db = SessionLocal()
    added = 0

    try:
        for q_text in questions:
            exists = (
                db.query(Question)
                .filter(Question.text == q_text)
                .first()
            )
            if exists:
                continue

            q = Question(text=q_text)
            db.add(q)
            added += 1

        if added > 0:
            db.commit()
    finally:
        db.close()

    print(f"[QUESTION SCRAPER] Saved {added} new questions.")
    return added


def main():
    html = fetch_page()
    questions = parse_questions(html)

    if not questions:
        print("[QUESTION SCRAPER] No questions parsed. (0개)")
        return

    save_to_db(questions)
    print("[QUESTION SCRAPER] Done.")


if __name__ == "__main__":
    main()
