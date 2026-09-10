def test_register_user(client):
    payload = {"email": "testuser@example.com", "password": "securepassword123"}
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "user"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_email(client):
    payload = {"email": "duplicate@example.com", "password": "securepassword123"}
    response1 = client.post("/auth/register", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/auth/register", json=payload)
    assert response2.status_code == 409


def test_login_for_access_token(client):
    email = "loginuser@example.com"
    password = "securepassword123"
    client.post("/auth/register", json={"email": email, "password": password})

    login_data = {"username": email, "password": password}
    response = client.post("/auth/token", data=login_data)

    assert response.status_code == 200
    token_payload = response.json()
    assert "access_token" in token_payload
    assert token_payload["token_type"] == "bearer"


def test_login_rate_limiting(client):
    email = "ratelimit_user@example.com"
    password = "password123"
    client.post("/auth/register", json={"email": email, "password": password})

    for _ in range(5):
        res = client.post("/auth/token", data={"username": email, "password": password})
        assert res.status_code == 200

    blocked_res = client.post(
        "/auth/token", data={"username": email, "password": password}
    )
    assert blocked_res.status_code == 429
    assert "Too many login attempts" in blocked_res.json()["detail"]
