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

def test_ready():
    response = client.get("/ready")
    assert response.status_code == 200

def test_live():
    response = client.get("/live")
    assert response.status_code == 200

def test_chat_without_auth():
    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 401

def test_features_without_auth():
    response = client.post("/api/features/study", json={"topic": "test"})
    assert response.status_code == 401

def test_rate_limiting():
    for _ in range(10):
        client.get("/health")
    response = client.get("/health")
    assert response.status_code == 200
