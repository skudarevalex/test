import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_register_user():
    response = client.post("/user/register", json={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_login_user():
    response = client.post("/user/login", json={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert "access_token" in response.json()