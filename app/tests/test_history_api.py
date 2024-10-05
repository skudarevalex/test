import pytest
import requests

API_URL = "http://app:8080"

def test_get_history():
    login_response = requests.post(f"{API_URL}/user/login", json={"username": "test_user", "password": "test_password"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/history/1", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
