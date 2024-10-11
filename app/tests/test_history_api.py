import pytest
from fastapi.testclient import TestClient
from api import app
from services.crud.userservice import UserService
from services.crud.mlservice import MLService
from webui.auth.jwt_handler import create_access_token
from models.user import User
from database.database import get_session
from sqlmodel import select

client = TestClient(app)
user_service = UserService()
ml_service = MLService()

@pytest.fixture
def test_user():
    with get_session() as session:
        user = User(username="history_test_user", password="test_password", balance=100)
        session.add(user)
        session.commit()
        session.refresh(user)
        yield {"user_id": user.id, "username": user.username}
        # Очистка после теста
        session.delete(user)
        session.commit()

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(data={"sub": str(test_user["user_id"])})
    return {"Authorization": f"Bearer {access_token}"}

def test_get_history(test_user, auth_headers):
    with get_session() as session:
        user = session.exec(select(User).where(User.id == test_user['user_id'])).first()
        if not user:
            pytest.fail("User not found")

    # First, create a prediction task
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
    ml_service.create_task(user, input_data)

    # Now get the history
    response = client.get(f"/history/{user.id}", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) > 0