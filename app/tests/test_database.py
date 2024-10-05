import pytest
from database.database import init_db, get_session
from models.user import User

def test_database_connection():
    with get_session() as session:
        assert session is not None

def test_user_model():
    with get_session() as session:
        new_user = User(username="test_user", password="test_password")
        session.add(new_user)
        session.commit()
        assert new_user.id is not None
