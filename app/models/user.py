from typing import Optional
from database.database import get_session
from sqlmodel import SQLModel, Field, Session, select

# Класс сущности пользователя для представления пользователя в системе
class User(SQLModel, table=True):
    # Инициализация пользователя с id, именем пользователя, паролем и балансом
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    balance: int = Field(default=0)

    def check_password(self, password: str) -> bool:
        # Проверить, совпадает ли предоставленный пароль с паролем пользователя
        return self.password == password

    def add_balance(self, amount: int) -> None:
        # Добавить указанную сумму к балансу пользователя
        self.balance += amount

    def subtract_balance(self, amount: int) -> bool:
        # Вычесть указанную сумму с баланса пользователя, если достаточно средств
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    @classmethod
    def create(cls, username: str, password: str) -> 'User':
        # Создать нового пользователя в базе данных и вернуть экземпляр пользователя
        with get_session() as session:
            existing_user = session.exec(select(User).where(User.username == username)).first()
            if existing_user:
                raise ValueError("Пользователь с таким именем уже существует")
            new_user = User(username=username, password=password, balance=0)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user

    @classmethod
    def get(cls, username: str) -> Optional['User']:
        # Получить пользователя из базы данных по имени пользователя
        with get_session() as session:
            user = session.exec(select(User).where(User.username == username)).first()
            return user

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional['User']:
        # Аутентифицировать пользователя по имени и паролю
        user = cls.get(username)
        if user and user.check_password(password):
            return user
        return None
