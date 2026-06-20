import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_login_missing_fields():
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422

def test_features_study_no_auth():
    response = client.post("/api/features/study", json={"topic": "test"})
    assert response.status_code == 401
