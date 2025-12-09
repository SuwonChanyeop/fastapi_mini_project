import requests
from bs4 import BeautifulSoup

from app.db.session import SessionLocal
from app.models.quote import Quote

TARGET_URL = "https://namu.wiki/w/%EB%AA%85%EC%96%B8"


def contains_hangul(text: str) -> bool:
    return any("가" <= ch <= "힣" for ch in text)


def fetch_page() -> str:
    print(f"[QUOTE SCRAPER] Fetching from: {TARGET_URL}")
    resp = requests.get(TARGET_URL, timeout=10)
    resp.raise_for_status()
    return resp.text


def parse_quotes(html: str):
    """
    ✏ 핵심 변경점:
    - 예전처럼 article만 찾지 않고, 페이지 전체의 <li> 를 대상으로 스캔
    - 한글 포함 + 적당한 길이(6~120글자)만 명언 후보로 사용
    - '문장 - 작가', '문장 — 작가' 형태면 author 분리
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

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

        if "편집" in text:
            continue
        if "목차" in text:
            continue
        if "나무위키" in text:
            continue

        quote_text = text
        author = None

        for sep in [" — ", " - ", " – ", "―", "—", "-"]:
            if sep in text:
                parts = text.split(sep)
                if len(parts) >= 2:
                    quote_text = parts[0].strip(" -–—―")
                    author = parts[-1].strip(" -–—―")
                break

        results.append((quote_text, author))

    print(f"[QUOTE SCRAPER] Parsed {len(results)} Korean quotes.")
    return results


def save_quotes(quotes):
    db = SessionLocal()
    added = 0

    try:
        for q_text, q_author in quotes:
            exists = (
                db.query(Quote)
                .filter(Quote.text == q_text)
                .first()
            )
            if exists:
                continue

            q = Quote(text=q_text, author=q_author)
            db.add(q)
            added += 1

        if added > 0:
            db.commit()
    finally:
        db.close()

    print(f"[QUOTE SCRAPER] Saved {added} new quotes.")
    return added


def main():
    html = fetch_page()
    quotes = parse_quotes(html)

    if not quotes:
        print("[QUOTE SCRAPER] No quotes parsed. (0개)")
        return

    save_quotes(quotes)
    print("[QUOTE SCRAPER] Done.")


if __name__ == "__main__":
    main()
