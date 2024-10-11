import pytest
from services.crud.userservice import UserService

@pytest.fixture
def user_service():
    return UserService()

def test_register_user(user_service):
    result = user_service.register("new_test_user", "test_password")
    assert result["status"] == "success"
    assert "message" in result

def test_login_user(user_service):
    # First, register a user
    user_service.register("login_test_user", "test_password")
    
    # Now try to login
    result = user_service.login("login_test_user", "test_password")
    assert result["status"] == "success"
    assert "access_token" in result

def test_get_user_balance(user_service):
    # Register a user
    user = user_service.register("balance_test_user", "test_password")
    
    # Get the balance
    balance = user_service.get_user_balance(user["user_id"])
    assert balance["status"] == "success"
    assert "balance" in balance

def test_add_balance(user_service):
    # Register a user
    user = user_service.register("add_balance_test_user", "test_password")
    
    # Add balance
    user_service.add_balance(user["user_id"], 100)
    
    # Check the new balance
    balance = user_service.get_user_balance(user["user_id"])
    assert balance["status"] == "success"
    assert balance["balance"] == 100