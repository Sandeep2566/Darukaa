from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    assert client.get("/health").json() == {"status": "ok"}


def test_registration_and_projects():
    response = client.post(
        "/auth/register",
        json={"email": f"maya-{uuid4().hex}@example.com", "password": "stable-pass-123"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post("/projects", json={"name": "Atlas Earth"}, headers=headers)
    assert created.status_code == 201
    assert client.get("/projects", headers=headers).json()[0]["name"] == "Atlas Earth"
    site = client.post(
        f"/projects/{created.json()['id']}/sites",
        json={
            "name": "Kutch Grasslands",
            "region": "Gujarat, India",
            "area_hectares": 125,
            "boundary_geojson": {
                "type": "Polygon",
                "coordinates": [[[68.5, 23.0], [68.6, 23.0], [68.6, 23.1], [68.5, 23.0]]],
            },
        },
        headers=headers,
    )
    assert site.status_code == 201
    assert site.json()["boundary_geojson"]["type"] == "Polygon"
