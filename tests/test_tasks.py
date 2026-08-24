def get_auth_header(client, email="taskuser@example.com", password="password123"):
    client.post("/auth/register", json={"email": email, "password": password})
    login_res = client.post(
        "/auth/token", data={"username": email, "password": password}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_task(client):
    headers = get_auth_header(client)
    task_payload = {
        "title": "Integration Test Task",
        "description": "Testing authenticated CRUD flow",
        "priority": 1,
    }

    create_res = client.post("/tasks", json=task_payload, headers=headers)
    assert create_res.status_code == 201
    created_task = create_res.json()
    assert created_task["title"] == task_payload["title"]
    assert created_task["description"] == task_payload["description"]
    assert "id" in created_task

    task_id = created_task["id"]

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 200
    fetched_task = get_res.json()
    assert fetched_task["id"] == task_id
    assert fetched_task["title"] == task_payload["title"]


def test_create_task_unauthenticated(client):
    task_payload = {
        "title": "Unauthorized Task",
        "description": "Should fail without token",
    }

    response = client.post("/tasks", json=task_payload)
    assert response.status_code == 401


def test_create_task_invalid_priority(client):
    headers = get_auth_header(client)

    invalid_payload = {
        "title": "Invalid Priority Task",
        "description": "Testing invalid priority boundary",
        "priority": 10,
    }
    response = client.post("/tasks", json=invalid_payload, headers=headers)
    assert response.status_code == 422


def test_create_task_missing_title(client):
    headers = get_auth_header(client)

    invalid_payload = {
        "description": "Task without a title",
        "priority": 1,
    }
    response = client.post("/tasks", json=invalid_payload, headers=headers)
    assert response.status_code == 422
