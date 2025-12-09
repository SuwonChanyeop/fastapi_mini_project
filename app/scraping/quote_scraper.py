import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.quote import Quote

TARGET_URL = "https://namu.wiki/w/%EB%AA%85%EC%96%B8"


def fetch_page() -> str:
    print(f"[QUOTE SCRAPER] Fetching from: {TARGET_URL}")
    resp = requests.get(TARGET_URL, timeout=10)
    resp.raise_for_status()
    return resp.text


def contains_hangul(text: str) -> bool:
    return any("가" <= ch <= "힣" for ch in text)


def parse_quotes(html: str) -> list[tuple[str, str | None]]:
    """
    - 페이지 내 모든 <li> 태그 텍스트 추출
    - 한글이 포함된 문장만 명언 후보로 사용
    - 너무 긴 설명/해설은 제외
    - "문장 — 화자" 또는 "문장 - 화자" 형태면 화자를 분리
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[tuple[str, str | None]] = []

    for li in soup.select("li"):
        text = li.get_text(" ", strip=True)
        if not text:
            continue
        if len(text) < 6:
            continue
        if len(text) > 120:
            continue

        if not contains_hangul(text):
            continue

        quote_text = text
        author: str | None = None

        for sep in ["—", "-", "―"]:
            if sep in text:
                parts = text.split(sep)
                if len(parts) >= 2:
                    quote_text = parts[0].strip()
                    author = parts[-1].strip()
                break

        results.append((quote_text, author))

    return results


def save_quotes(db: Session, quotes: list[tuple[str, str | None]]) -> int:
    added = 0

    for q_text, q_author in quotes:
        exists = db.query(Quote).filter(Quote.text == q_text).first()
        if exists:
            continue

        q = Quote(text=q_text, author=q_author)
        db.add(q)
        added += 1

    if added > 0:
        db.commit()

    return added


def scrape_quotes() -> None:
    """
    전체 흐름:
    1) 한국어 명언 페이지에서 HTML 가져오기
    2) 명언/화자 리스트로 파싱
    3) quotes 테이블에 저장
    """
    html = fetch_page()
    quotes = parse_quotes(html)
    print(f"[QUOTE SCRAPER] Parsed {len(quotes)} Korean quotes")

    if not quotes:
        print("[QUOTE SCRAPER] No quotes parsed. (0개) – 사이트 구조가 바뀐 것일 수 있습니다.")
        return

    db = SessionLocal()
    try:
        added = save_quotes(db, quotes)
        print(f"[QUOTE SCRAPER] Added {added} new quotes to DB")
    finally:
        db.close()

    print("[QUOTE SCRAPER] Done.")


if __name__ == "__main__":
    scrape_quotes()
