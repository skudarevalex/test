from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from database.database import get_session

# Класс транзакции для представления транзакции в системе
class Transaction(SQLModel, table=True):
    # Инициализация транзакции с id, user_id, суммой, временной меткой и описанием
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str

    class Config:
        arbitrary_types_allowed = True


    @classmethod
    def create(cls, user_id: int, amount: int, description: str) -> 'Transaction':
        # Создать новую транзакцию в базе данных и вернуть экземпляр транзакции
        with get_session() as session:
            new_transaction = Transaction(user_id=user_id, amount=amount, description=description)
            session.add(new_transaction)
            session.commit()
            session.refresh(new_transaction)
            return new_transaction

    @classmethod
    def get_user_transactions(cls, user_id: int) -> List['Transaction']:
        # Получить все транзакции для заданного пользователя из базы данных
        with get_session() as session:
            transactions = session.query(Transaction).filter_by(user_id=user_id).all()
            return transactions
