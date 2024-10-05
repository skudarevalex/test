import pytest
import requests

API_URL = "http://app:8080"

def test_get_balance():
    # Войдите и получите токен
    login_response = requests.post(f"{API_URL}/user/login", json={"username": "test_user", "password": "test_password"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/balance/1", headers=headers)
    assert response.status_code == 200
    assert "balance" in response.json()

def test_add_balance():
    login_response = requests.post(f"{API_URL}/user/login", json={"username": "test_user", "password": "test_password"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{API_URL}/balance/1/add", json={"amount": 100}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
