import os
import pika
import time
import json
from typing import Dict, Any
from models.user import User
from models.mltask import MLTask
from models.mlmodelmanager import MLModelManager

class MLService:
    def __init__(self, model_manager: MLModelManager):
        # Инициализация менеджера моделей и переменных для подключения к RabbitMQ
        self._model_manager = model_manager
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

    def process_task(self, user: User, model_id: int, input_data: str) -> Dict[str, Any]:
        # Парсинг входных данных
        input_values = input_data.split(',')
        valid_data, invalid_data = [], []

        # Валидация данных: разделение на валидные и невалидные данные
        for item in input_values:
            try:
                valid_data.append(float(item))
            except ValueError:
                invalid_data.append(item)

        # Проверка наличия валидных данных
        if not valid_data:
            return {"status": "fail", "message": "No valid data provided", "invalid_data": invalid_data}

        # Расчет стоимости выполнения задачи
        cost = len(valid_data) * 1  # Пример расчета стоимости
        # Проверка баланса пользователя
        if not user.subtract_balance(cost):
            return {"status": "fail", "message": "Insufficient balance"}

        # Формирование задачи для отправки в RabbitMQ
        task = {
            "user_id": user.id,
            "model_id": model_id,
            "input_data": valid_data,
            "invalid_data": invalid_data,
            "cost": cost
        }
        # Отправка задачи в очередь 'ml_tasks'
        self._channel.basic_publish(exchange='', routing_key='ml_tasks', body=json.dumps(task))
        return {"status": "success", "message": "Task submitted to ML service"}

    def close(self):
        # Закрытие соединения с RabbitMQ
        if self._connection:
            self._connection.close()