import pytest
import requests

API_URL = "http://app:8080"

def test_predict():
    login_response = requests.post(f"{API_URL}/user/login", json={"username": "test_user", "password": "test_password"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{API_URL}/prediction", json={"model_id": 1, "input_data": "1.0, 2.0, 3.0"}, headers=headers)
    assert response.status_code == 200
    assert "prediction" in response.json()
