from config import settings


def test_cors_allowed_origin(client):
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    )


def test_cors_disallowed_origin(client):
    response = client.get(
        "/health",
        headers={"Origin": "http://unauthorized-domain.com"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_settings_defaults():
    assert settings.ENVIRONMENT == "development"
    assert isinstance(settings.ALLOWED_CORS_ORIGINS, list)
    assert "http://localhost:3000" in settings.ALLOWED_CORS_ORIGINS
