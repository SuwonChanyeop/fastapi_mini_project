from fastapi.testclient import TestClient


def test_signup_and_login(client: TestClient):
    # 회원가입
    resp = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "secret",
            "nickname": "tester",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

    # 로그인
    resp_login = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "secret",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp_login.status_code == 200
    token_data = resp_login.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # /me 조회
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    resp_me = client.get("/api/v1/auth/me", headers=headers)
    assert resp_me.status_code == 200
    me = resp_me.json()
    assert me["email"] == "test@example.com"
