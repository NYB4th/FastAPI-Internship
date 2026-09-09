from unittest.mock import patch


def get_auth_header(client, email="taskuser@example.com", password="password123"):
    client.post("/auth/register", json={"email": email, "password": password})
    login_res = client.post(
        "/auth/token", data={"username": email, "password": password}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_admin_user(
    client, email="admin@example.com", password="adminpassword123", db_session=None
):
    """Registers a user and promotes them to admin directly in the database."""
    reg_res = client.post("/auth/register", json={"email": email, "password": password})
    user_id = reg_res.json()["id"]

    if db_session:
        from models.user import User

        user = db_session.query(User).filter(User.id == user_id).first()
        if user:
            user.role = "admin"
            db_session.commit()

    login_res = client.post(
        "/auth/token", data={"username": email, "password": password}
    )
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


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


def test_task_includes_user_id(client):
    headers = get_auth_header(client, email="ownercheck@example.com")
    task_payload = {"title": "Check User ID Field", "priority": 1}

    response = client.post("/tasks", json=task_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert isinstance(data["user_id"], int)


def test_user_cannot_access_other_user_task(client):
    user_a_headers = get_auth_header(client, email="usera@example.com")
    user_b_headers = get_auth_header(client, email="userb@example.com")

    create_res = client.post(
        "/tasks",
        json={"title": "User A Private Task", "priority": 1},
        headers=user_a_headers,
    )
    task_id = create_res.json()["id"]

    get_res = client.get(f"/tasks/{task_id}", headers=user_b_headers)
    assert get_res.status_code == 404

    put_res = client.put(
        f"/tasks/{task_id}", json={"title": "Hacked Title"}, headers=user_b_headers
    )
    assert put_res.status_code == 404

    delete_res = client.delete(f"/tasks/{task_id}", headers=user_b_headers)
    assert delete_res.status_code == 404


def test_get_all_tasks_filters_by_logged_in_user(client):
    headers_a = get_auth_header(client, email="filter_a@example.com")
    headers_b = get_auth_header(client, email="filter_b@example.com")

    client.post(
        "/tasks", json={"title": "Task User A", "priority": 1}, headers=headers_a
    )
    client.post(
        "/tasks", json={"title": "Task User B", "priority": 1}, headers=headers_b
    )

    response_a = client.get("/tasks", headers=headers_a)
    assert response_a.status_code == 200
    tasks_a = response_a.json()
    assert len(tasks_a) == 1
    assert tasks_a[0]["title"] == "Task User A"


def test_different_users_can_have_same_task_title(client):
    headers_a = get_auth_header(client, email="same_title_a@example.com")
    headers_b = get_auth_header(client, email="same_title_b@example.com")

    payload = {"title": "Shared Task Title", "priority": 1}

    res_a = client.post("/tasks", json=payload, headers=headers_a)
    assert res_a.status_code == 201

    res_b = client.post("/tasks", json=payload, headers=headers_b)
    assert res_b.status_code == 201


def test_regular_user_cannot_update_roles(client):
    headers = get_auth_header(client, email="regular@example.com")
    response = client.patch("/users/1/role", json={"role": "admin"}, headers=headers)
    assert response.status_code == 403


def test_admin_can_update_user_role_and_manage_tasks(client, db_session):

    user_headers = get_auth_header(client, email="standard_user@example.com")
    admin_headers, admin_id = create_admin_user(
        client,
        email="admin_user@example.com",
        db_session=db_session,  # pyright: ignore[reportCallIssue]
    )

    create_res = client.post(
        "/tasks", json={"title": "Standard Task", "priority": 1}, headers=user_headers
    )
    task_id = create_res.json()["id"]

    get_res = client.get(f"/tasks/{task_id}", headers=admin_headers)
    assert get_res.status_code == 200

    put_res = client.put(
        f"/tasks/{task_id}",
        json={"title": "Admin Modified Task"},
        headers=admin_headers,
    )
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "Admin Modified Task"

    role_res = client.patch(
        "/users/1/role", json={"role": "admin"}, headers=admin_headers
    )
    assert role_res.status_code == 200
    assert role_res.json()["role"] == "admin"


def test_create_task_triggers_background_audit_log(client):
    headers = get_auth_header(client, email="audit_trigger@example.com")
    payload = {"title": "Task with Background Audit", "priority": 1}

    with patch("routers.task_router.log_task_event") as mock_audit:
        response = client.post("/tasks", json=payload, headers=headers)
        assert response.status_code == 201
        created_task = response.json()

        mock_audit.assert_called_once_with(
            task_id=created_task["id"],
            user_id=created_task["user_id"],
            event_type="TASK_CREATED",
        )


def test_failed_task_creation_does_not_schedule_background_audit(client):
    headers = get_auth_header(client, email="audit_fail@example.com")

    with patch("routers.task_router.log_task_event") as mock_audit:
        # Case 1: Validation error (missing required title)
        invalid_res = client.post(
            "/tasks", json={"description": "No title", "priority": 1}, headers=headers
        )
        assert invalid_res.status_code == 422
        mock_audit.assert_not_called()

        # Case 2: Successful first creation
        valid_payload = {"title": "Unique Audit Task", "priority": 2}
        first_res = client.post("/tasks", json=valid_payload, headers=headers)
        assert first_res.status_code == 201
        assert mock_audit.call_count == 1

        # Case 3: Duplicate title conflict (409 Conflict)
        mock_audit.reset_mock()
        dup_res = client.post("/tasks", json=valid_payload, headers=headers)
        assert dup_res.status_code == 409
        mock_audit.assert_not_called()


def test_background_audit_failure_does_not_affect_task_creation(client):
    headers = get_auth_header(client, email="audit_resilience@example.com")
    payload = {"title": "Resilient Audit Task", "priority": 3}

    def fail_on_audit(msg, *args, **kwargs):
        if "[AUDIT]" in str(msg):
            raise RuntimeError("Logging stream failed")

    with patch("services.audit.logger.info", side_effect=fail_on_audit), patch(
        "services.audit.logger.error"
    ) as mock_err:
        response = client.post("/tasks", json=payload, headers=headers)

        # The client response must still succeed with 201 Created
        assert response.status_code == 201
        assert response.json()["title"] == payload["title"]

        # The background exception must be safely caught and logged
        mock_err.assert_called_once()
        assert "Logging stream failed" in mock_err.call_args[0][0]
