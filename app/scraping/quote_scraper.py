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
    페이지 HTML 가져오기 (User-Agent 포함 → 차단 방지)
    """
    url = f"{BASE_URL}?page={page}"
    print(f"[QUOTE SCRAPER] Request URL: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=10)
    print(f"[QUOTE SCRAPER] Status={resp.status_code}, Length={len(resp.text)}")
    resp.raise_for_status()
    return resp.text


def parse_quotes(html: str) -> List[Tuple[str, str | None]]:
    """
    사람로 명언 페이지는 HTML 구조가 매번 바뀔 수 있기 때문에
    '텍스트 패턴' 기반 파싱으로 안정적으로 동작하도록 재작성.

    패턴:
      1) '명언' 이라는 라인이 나오면 → 새로운 블록 시작
      2) 다음 줄들이 명언 본문
      3) '-' 로 시작하는 줄을 → 작가(author)로 인식
      4) '명언 목록 번호 제목 분류' 등을 만나면 → 블록 종료
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)  # 페이지 전체 텍스트 추출
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    results: List[Tuple[str, str | None]] = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # 명언 블록의 시작 신호
        if line == "명언":
            content_lines: List[str] = []
            author: str | None = None
            j = i + 1

            while j < len(lines):
                l = lines[j]

                # 블록 종료 조건
                if l == "명언":
                    break
                if l.startswith("명언 목록 번호 제목 분류"):
                    break
                if l.startswith("Total ") and "건" in l:
                    break
                if l.startswith("댓글"):
                    break

                # 작가 줄: "- 작가명"
                if l.startswith("-"):
                    author = l.lstrip("-").strip()
                    j += 1
                    break

                # 명언 본문 누적
                content_lines.append(l)
                j += 1

            content = " ".join(content_lines).strip()
            if content:
                results.append((content, author))

            i = j
        else:
            i += 1

    print(f"[QUOTE SCRAPER] Parsed {len(results)} quotes")
    return results


def save_quotes(db: Session, quotes: List[Tuple[str, str | None]]) -> int:
    """
    명언 저장 (중복은 무시)
    """
    added = 0
    for text, author in quotes:
        exists = db.query(Quote).filter(Quote.text == text).first()
        if exists:
            continue

        q = Quote(text=text, author=author)
        db.add(q)
        added += 1

    if added:
        db.commit()
    return added


def scrape_quotes(pages: int = 3, sleep_sec: float = 1.0) -> None:
    """
    pages: 몇 페이지까지 스크래핑 할지
    sleep_sec: 페이지당 딜레이
    """
    db = SessionLocal()
    try:
        total_added = 0

        for page in range(1, pages + 1):
            print(f"\n[QUOTE SCRAPER] Fetch page {page}...")
            html = fetch_quote_list(page)

            parsed = parse_quotes(html)
            if not parsed:
                print(f"[QUOTE SCRAPER] Page {page}: No quotes found. STOP.")
                break

            added = save_quotes(db, parsed)
            total_added += added

            print(f"[QUOTE SCRAPER] Page {page}: {added} added")
            time.sleep(sleep_sec)

        print(f"\n[QUOTE SCRAPER] DONE. TOTAL ADDED = {total_added}")

    finally:
        db.close()


if __name__ == "__main__":
    scrape_quotes(pages=3)
