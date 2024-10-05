import pytest
import requests

API_URL = "http://app:8080"

def test_register_user():
    response = requests.post(f"{API_URL}/user/register", json={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_login_user():
    response = requests.post(f"{API_URL}/user/login", json={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert "access_token" in response.json()
