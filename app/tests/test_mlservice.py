import pytest
from services.crud.mlservice import MLService
from models.user import User

@pytest.fixture
def ml_service():
    return MLService()

@pytest.fixture
def test_user():
    return User(id=1, username="test_user", password="test_password", balance=100)

def test_create_task(ml_service, test_user):
    input_data = {
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
    result = ml_service.create_task(test_user, input_data)
    assert result["status"] == "success"
    assert "task_id" in result