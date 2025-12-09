from app.db.session import SessionLocal
from app.models.quote import Quote

db = SessionLocal()

quotes = [
    ("지금 하는 선택이 내 미래를 만든다.", "알려지지 않음"),
    ("작은 변화가 큰 성장을 만든다.", "알려지지 않음"),
    ("오늘의 나를 이기는 것이 가장 큰 승리다.", "알려지지 않음"),
    ("꾸준함은 결국 모든 것을 이긴다.", "알려지지 않음"),
]

for text, author in quotes:
    db.add(Quote(text=text, author=author))

db.commit()
print("Done.")
