from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from database.database import get_session


# Класс задачи ML для представления ML задачи в системе
class MLTask(SQLModel, table=True):
    # Инициализация задачи ML с id, user_id, model_id, входными данными, выходными данными, статусом, временем создания и стоимостью
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    model_id: int = Field(index=True)
    input_data: str
    output_data: Optional[str]
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cost: int

    class Config:
        protected_namespaces = ()  # Устранение предупреждения о конфликте

        
    
    @classmethod
    def create(cls, user_id: int, model_id: int, input_data: str, output_data: Optional[str], status: str, cost: int) -> 'MLTask':
        # Создать новую задачу ML в базе данных и вернуть экземпляр задачи
        with get_session() as session:
            ml_task = MLTask(
                user_id=user_id,
                model_id=model_id,
                input_data=input_data,
                output_data=output_data,
                status=status,
                cost=cost
            )
            session.add(ml_task)
            session.commit()
            session.refresh(ml_task)
            return ml_task

    @classmethod
    def get_user_tasks(cls, user_id: int) -> List['MLTask']:
        # Получить все задачи ML для заданного пользователя из базы данных
        with get_session() as session:
            tasks = session.query(MLTask).filter_by(user_id=user_id).all()
            return tasks
    

