import pytest
from fastapi.testclient import TestClient
from api import app
from services.crud.userservice import UserService
from webui.auth.jwt_handler import create_access_token
from sqlmodel import select
from database.database import get_session
from models.user import User

client = TestClient(app)
user_service = UserService()

@pytest.fixture
def test_user():
    # Удаляем существующего пользователя, если он есть
    with get_session() as session:
        existing_user = session.exec(select(User).where(User.username == "test_user")).first()
        if existing_user:
            session.delete(existing_user)
            session.commit()
    
    result = user_service.register("test_user", "test_password")
    if result["status"] == "fail":
        pytest.fail("Failed to create test user")
    return result

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(data={"sub": str(test_user["user_id"])})
    return {"Authorization": f"Bearer {access_token}"}

def test_get_balance(test_user, auth_headers):
    response = client.get(f"/balance/{test_user['user_id']}", headers=auth_headers)
    assert response.status_code == 200
    assert "balance" in response.json()

def test_add_balance(test_user, auth_headers):
    response = client.post(f"/balance/{test_user['user_id']}/add", json={"amount": 100}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Проверяем, что баланс действительно увеличился
    balance_response = client.get(f"/balance/{test_user['user_id']}", headers=auth_headers)
    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 100