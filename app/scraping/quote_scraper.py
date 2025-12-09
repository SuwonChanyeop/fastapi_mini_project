import time
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.quote import Quote


BASE_URL = "https://saramro.com/quotes"


def fetch_quote_list(page: int = 1) -> str:
    """
    주어진 페이지의 HTML을 가져옵니다.
    필요에 따라 ?page=2 이런식으로 바꿔주세요.
    """
    url = f"{BASE_URL}?page={page}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def parse_quotes(html: str) -> List[Tuple[str, str | None]]:
    """
    HTML에서 명언(text)과 author를 파싱합니다.
    사이트 구조에 맞게 selector는 약간 수정이 필요할 수 있습니다.
    return: [(text, author), ...]
    """
    soup = BeautifulSoup(html, "html.parser")
    results: List[Tuple[str, str | None]] = []

    # 예시: <div class="quote-item"><p class="content">...</p><p class="author">...</p></div>
    quote_items = soup.select(".quote-item")

    for item in quote_items:
        text_el = item.select_one(".content")
        author_el = item.select_one(".author")

        if not text_el:
            continue

        text = text_el.get_text(strip=True)
        author = author_el.get_text(strip=True) if author_el else None

        if text:
            results.append((text, author))

    return results


def save_quotes(db: Session, quotes: List[Tuple[str, str | None]]) -> int:
    """
    quotes: (text, author) 리스트를 DB에 저장.
    text 중복은 건너뜁니다.
    반환값: 새로 추가된 개수
    """
    added = 0
    for text, author in quotes:
        # 중복 체크: text 동일한 것이 있으면 skip
        exists = db.query(Quote).filter(Quote.text == text).first()
        if exists:
            continue

        q = Quote(text=text, author=author)
        db.add(q)
        added += 1

    if added:
        db.commit()
    return added


def scrape_quotes(pages: int = 1, sleep_sec: float = 1.0) -> None:
    """
    pages: 몇 페이지까지 가져올지
    sleep_sec: 사이트에 너무 많은 요청을 보내지 않도록 delay
    """
    db = SessionLocal()
    try:
        total_added = 0
        for page in range(1, pages + 1):
            print(f"[QUOTE SCRAPER] Fetch page {page} ...")
            html = fetch_quote_list(page)
            parsed = parse_quotes(html)
            if not parsed:
                print(f"[QUOTE SCRAPER] page {page}: no quotes found, stop.")
                break

            added = save_quotes(db, parsed)
            total_added += added
            print(f"[QUOTE SCRAPER] page {page}: {added} quotes added.")

            time.sleep(sleep_sec)

        print(f"[QUOTE SCRAPER] Done. Total added: {total_added}")
    finally:
        db.close()


if __name__ == "__main__":
    scrape_quotes(pages=3)
