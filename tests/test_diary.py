from fastapi.testclient import TestClient


def get_token(client: TestClient) -> str:
    # 테스트용 유저 생성
    client.post(
        "/api/v1/auth/signup",
        json={"email": "diary@example.com", "password": "secret"},
    )
    resp_login = client.post(
        "/api/v1/auth/login",
        data={"username": "diary@example.com", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_data = resp_login.json()
    return token_data["access_token"]


def test_diary_crud(client: TestClient):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 생성
    resp_create = client.post(
        "/api/v1/diaries",
        json={"title": "오늘의 일기", "content": "테스트 내용"},
        headers=headers,
    )
    assert resp_create.status_code == 201
    diary = resp_create.json()
    diary_id = diary["id"]

    # 목록 조회
    resp_list = client.get("/api/v1/diaries", headers=headers)
    assert resp_list.status_code == 200
    list_data = resp_list.json()
    assert list_data["total"] >= 1

    # 단건 조회
    resp_get = client.get(f"/api/v1/diaries/{diary_id}", headers=headers)
    assert resp_get.status_code == 200

    # 수정
    resp_update = client.patch(
        f"/api/v1/diaries/{diary_id}",
        json={"title": "수정된 제목"},
        headers=headers,
    )
    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["title"] == "수정된 제목"

    # 삭제
    resp_delete = client.delete(f"/api/v1/diaries/{diary_id}", headers=headers)
    assert resp_delete.status_code == 204
