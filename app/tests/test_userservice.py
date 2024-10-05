import pytest
from services.crud.userservice import UserService
from models.user import User
from database.database import get_session

@pytest.fixture
def user_service():
    return UserService()

def test_register_user(user_service):
    username = "test_user"
    password = "test_password"
    result = user_service.register(username, password)
    assert result["status"] == "success"

def test_login_user(user_service):
    username = "test_user"
    password = "test_password"
    result = user_service.login(username, password)
    assert result["status"] == "success"
    assert "access_token" in result
