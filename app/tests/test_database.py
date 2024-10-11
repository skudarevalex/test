import pytest
from sqlmodel import Session, select
from database.database import init_db, get_session
from models.user import User

@pytest.fixture(scope="module")
def init_test_db():
    init_db()

def test_database_connection(init_test_db):
    with get_session() as session:
        assert isinstance(session, Session)

def test_create_and_retrieve_user(init_test_db):
    with get_session() as session:
        new_user = User(username="testuser", password="testpass")
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        retrieved_user = session.exec(select(User).where(User.username == "testuser")).first()
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"

        # Очистка после теста
        session.delete(retrieved_user)
        session.commit()