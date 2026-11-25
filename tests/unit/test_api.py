from codepilot.api import create_app
from codepilot.config import Settings
from codepilot.demo import prepare_demo
from fastapi.testclient import TestClient


def test_local_auth_origin_and_run_lifecycle(tmp_path):
    settings = Settings(data_dir=tmp_path, GEMINI_API_KEY="", model="")
    prepare_demo(tmp_path)
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/runs").status_code == 401
        assert client.post("/api/session").status_code == 403
        assert (
            client.post("/api/session", headers={"origin": "https://evil.example"}).status_code
            == 403
        )
        client.headers["origin"] = "http://testserver"
        assert client.post("/api/session").status_code == 200
        body = {"repository_id": "boundary", "task": "Fix boundary"}
        assert (
            client.post("/api/runs", json={**body, "repository_id": "/tmp/other"}).status_code
            == 400
        )
        assert client.post("/api/runs", json={**body, "provider": "gemini"}).status_code == 400
        run = client.post("/api/runs", json=body).json()["id"]
        assert client.get(f"/api/runs/{run}").json()["run"]["state"] == "queued"
        assert client.get(f"/api/runs/{run}/artifacts/.env").status_code == 404
        assert client.post(f"/api/runs/{run}/cancel", json={}).status_code == 200
        retry = client.post(f"/api/runs/{run}/retry", json={}).json()["id"]
        assert retry != run
        assert (
            client.get(f"/api/runs/{retry}").json()["run"]["base_sha"]
            == client.get(f"/api/runs/{run}").json()["run"]["base_sha"]
        )
        assert client.get("/api/runs/unknown").status_code == 404


def test_live_submission_pins_model_without_exposing_key(tmp_path):
    settings = Settings(
        data_dir=tmp_path, GEMINI_API_KEY="synthetic-local-secret", model="gemini-test"
    )
    prepare_demo(tmp_path)
    with TestClient(create_app(settings)) as client:
        client.headers["origin"] = "http://testserver"
        client.post("/api/session")
        response = client.post(
            "/api/runs",
            json={"repository_id": "boundary", "task": "Fix boundary", "provider": "gemini"},
        )
        assert response.status_code == 201
        detail = client.get("/api/runs/" + response.json()["id"])
        assert "synthetic-local-secret" not in detail.text
        assert "gemini-test" in detail.json()["run"]["provider_json"]
        assert client.get("/api/capabilities").json()["live_generation_verified"] is False
