from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.question import Question


def test_random_question(client: TestClient):
    db: Session = next(get_db())
    q = Question(text="테스트 질문입니다.", category="테스트")
    db.add(q)
    db.commit()
    db.refresh(q)

    resp = client.get("/api/v1/questions/random")
    assert resp.status_code == 200
    data = resp.json()
    assert data["text"] == "테스트 질문입니다."
