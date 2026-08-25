from unittest.mock import AsyncMock, patch
from exceptions.external_exceptions import UpstreamNotFoundError, UpstreamTimeoutError
from schemas.external import PostResponse


def test_get_external_post_success(client):
    mock_post = PostResponse(userId=1, id=1, title="Test Title", body="Test Body")
    with patch(
        "routers.external.get_external_post", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = mock_post
        response = client.get("/external/posts/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["userId"] == 1
    assert data["title"] == "Test Title"


def test_get_external_post_not_found(client):
    with patch(
        "routers.external.get_external_post", new_callable=AsyncMock
    ) as mock_get:
        mock_get.side_effect = UpstreamNotFoundError()
        response = client.get("/external/posts/999999")

    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "UPSTREAM_NOT_FOUND"


def test_get_external_post_timeout(client):
    with patch(
        "routers.external.get_external_post", new_callable=AsyncMock
    ) as mock_get:
        mock_get.side_effect = UpstreamTimeoutError()
        response = client.get("/external/posts/1")

    assert response.status_code == 504
    data = response.json()
    assert data["error_code"] == "UPSTREAM_TIMEOUT"
