from typing import Dict, Any, Optional
from sqlmodel import Session, select
from database.database import get_session
from models.user import User
from models.transaction import Transaction
from webui.auth.hash_password import hash_password, verify_password
from webui.auth.jwt_handler import create_access_token
import logging

logger = logging.getLogger(__name__)

class UserService:
    def register(self, username: str, password: str) -> Dict[str, Any]:
        # Регистрация нового пользователя в системе
        with get_session() as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if user:
                logger.warning(f"User already exists: {username}")
                return {"status": "fail", "message": "User already exists"}
            hashed_password = hash_password(password)
            new_user = User(username=username, password=hashed_password)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            logger.info(f"User registered: {username}")
            return {"status": "success", "message": "User registered successfully"}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        # Вход пользователя в систему
        with get_session() as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if user and verify_password(password, user.password):
                access_token = create_access_token(data={"sub": str(user.id)})
                logger.info(f"User authenticated: {username}")
                return {"status": "success", "access_token": access_token, "user_id": user.id}
            logger.warning(f"Invalid credentials for user: {username}")
            return {"status": "fail", "message": "Invalid username or password"}

    def add_balance(self, user_id: int, amount: int) -> None:
        # Добавление баланса на счет пользователя
        with get_session() as session:
            user = session.get(User, user_id)
            if user:
                user.balance += amount
                transaction = Transaction(user_id=user_id, amount=amount, description="Balance top-up")
                session.add(user)
                session.add(transaction)
                session.commit()
                logger.info(f"Balance added: {amount} to user: {user_id}")

    def get_user_balance(self, user_id: int) -> Dict[str, Any]:
        # Получение баланса счета пользователя
        with get_session() as session:
            user = session.get(User, user_id)
            if user:
                logger.info(f"Balance retrieved for user: {user_id}")
                return {"status": "success", "balance": user.balance}
            logger.warning(f"User not found: {user_id}")
            return {"status": "fail", "message": "User not found"}

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        # Получение пользователя по ID
        with get_session() as session:
            user = session.get(User, user_id)
            session.expunge_all()
            if user:
                logger.info(f"User found by ID: {user_id}")
                return user
            logger.warning(f"User not found by ID: {user_id}")
            return None
