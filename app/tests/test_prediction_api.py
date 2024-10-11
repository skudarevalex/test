import pytest
from fastapi.testclient import TestClient
from api import app
from services.crud.userservice import UserService
from webui.auth.jwt_handler import create_access_token

client = TestClient(app)
user_service = UserService()

@pytest.fixture
def test_user():
    user = user_service.register("test_user", "test_password")
    return user

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(data={"sub": str(test_user["user_id"])})
    return {"Authorization": f"Bearer {access_token}"}

def test_create_prediction_task(test_user, auth_headers):
    prediction_data = {
        "work_year": 2024,
        "experience_level": "SE",
        "employment_type": "FT",
        "job_category": "Data Science",
        "job_tags": "python,machine learning",
        "employee_residence": "US",
        "remote_ratio": 100,
        "company_location": "US",
        "company_size": "L"
    }
    response = client.post("/prediction/predict_salary", json=prediction_data, headers=auth_headers)
    assert response.status_code == 200
    assert "task_id" in response.json()