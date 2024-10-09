import os
import pika
import time
import json
from typing import Dict, Any
from models.user import User
from models.mltask import MLTask
from models.ml_predictor_module import predict_salary
from database.database import get_session

class MLService:
    def __init__(self):
        # Инициализация переменных для подключения к RabbitMQ
        self._connection = None
        self._channel = None
        self._connect_to_rabbitmq()

    def _connect_to_rabbitmq(self):
        # Попытка подключения к RabbitMQ с несколькими попытками и задержкой между ними
        attempts = 10
        while attempts > 0:
            try:
                print("Attempting to connect to RabbitMQ, attempts left:", attempts)
                self._connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST'),
                    port=int(os.getenv('RABBITMQ_PORT')),
                    credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USER'), os.getenv('RABBITMQ_PASS'))
                ))
                self._channel = self._connection.channel()
                # Объявление очереди 'ml_tasks' (если не существует, она будет создана)
                self._channel.queue_declare(queue='ml_tasks')
                break
            except pika.exceptions.AMQPConnectionError as e:
                print("Connection to RabbitMQ failed:", e)
                attempts -= 1
                time.sleep(10)
                if attempts == 0:
                    # Если все попытки исчерпаны, выбрасываем исключение
                    raise

    def process_task(self, user: User, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Проверка баланса пользователя
        cost = 10  # Стоимость предсказания
        if not user.subtract_balance(cost):
            return {"status": "fail", "message": "Insufficient balance"}

        # Получение предсказания зарплаты
        try:
            prediction = predict_salary(input_data)
            predicted_salary = prediction['predicted_salary'].iloc[0]
        except Exception as e:
            return {"status": "fail", "message": str(e)}

        # Создание записи о задаче в базе данных
        with get_session() as session:
            ml_task = MLTask.create(
                user_id=user.id,
                model_id=1,  # Замените на актуальный идентификатор модели, если необходимо
                input_data=json.dumps(input_data),
                output_data=str(predicted_salary),
                status="completed",
                cost=cost
            )
            session.add(ml_task)
            session.commit()

        return {"status": "success", "predicted_salary": predicted_salary}

    def close(self):
        # Закрытие соединения с RabbitMQ
        if self._connection:
            self._connection.close()