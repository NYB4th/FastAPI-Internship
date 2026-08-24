def test_read_root(client):
    reponse = client.get("/")
    assert reponse.status_code == 200


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
