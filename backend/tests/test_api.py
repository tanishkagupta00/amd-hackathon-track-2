import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_config_endpoint():
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    assert "project_name" in response.json()
    assert response.json()["database"] == "SQLite"

def test_evaluation_endpoint():
    payload = {
        "caption": "A domestic feline is playing with a ball of yarn.",
        "style": "formal",
        "entities": ["cat", "yarn"]
    }
    response = client.post("/api/v1/evaluations", json=payload)
    assert response.status_code == 200
    assert response.json()["accuracy_score"] > 0.0
    assert response.json()["style_score"] > 0.0
    assert response.json()["hallucination_detected"] is False
