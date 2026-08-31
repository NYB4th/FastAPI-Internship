def get_auth_header(client, email="taskuser@example.com", password="password123"):
    client.post("/auth/register", json={"email": email, "password": password})
    login_res = client.post(
        "/auth/token", data={"username": email, "password": password}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_complete_task_lifecycle(client):
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
    task_id = created_task["id"]

    get_res = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id

    update_payload = {"title": "Updated Task Title", "priority": 2}
    update_res = client.put(f"/tasks/{task_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Task Title"

    delete_res = client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_res.status_code == 204

    get_deleted_res = client.get(f"/tasks/{task_id}", headers=headers)
    assert get_deleted_res.status_code == 404


def test_create_task_unauthenticated(client):
    task_payload = {
        "title": "Unauthorized Task",
        "description": "Should fail without token",
        "priority": 1,
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


def test_get_all_tasks_paginated(client):
    headers = get_auth_header(client)
    for i in range(3):
        client.post(
            "/tasks",
            json={"title": f"Task {i}", "priority": 1},
            headers=headers,
        )

    response = client.get("/tasks?limit=2&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_create_duplicate_task_title(client):
    headers = get_auth_header(client)
    payload = {"title": "Unique Task", "priority": 1}

    res1 = client.post("/tasks", json=payload, headers=headers)
    assert res1.status_code == 201

    res2 = client.post("/tasks", json=payload, headers=headers)
    assert res2.status_code == 409


def test_unauthenticated_task_routes(client):
    assert client.get("/tasks").status_code == 401
    assert client.get("/tasks/1").status_code == 401
    assert client.put("/tasks/1", json={"title": "Test"}).status_code == 401
    assert client.delete("/tasks/1").status_code == 401
