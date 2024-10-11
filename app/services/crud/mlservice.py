import os
import pika
import time
import json
from typing import Dict, Any
from models.user import User
from models.mltask import MLTask
from database.database import get_session
from sqlmodel import Session

class MLService:
    def __init__(self):
        self._connection = None
        self._channel = None
        self._connect_to_rabbitmq()

    def _connect_to_rabbitmq(self):
        attempts = 10
        while attempts > 0:
            try:
                print("Attempting to connect to RabbitMQ, attempts left:", attempts)
                parameters = pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST'),
                    port=int(os.getenv('RABBITMQ_PORT')),
                    credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USER'), os.getenv('RABBITMQ_PASS')),
                    heartbeat=300,  # Устанавливаем heartbeat на 300 секунд
                    blocked_connection_timeout=150  # Таймаут для блокированных соединений
                )
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                self._channel.queue_declare(queue='ml_tasks')
                print("Connected to RabbitMQ successfully")
                break
            except pika.exceptions.AMQPConnectionError as e:
                print("Connection to RabbitMQ failed:", e)
                attempts -= 1
                time.sleep(10)
                if attempts == 0:
                    raise

    def create_task(self, user: User, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self._connection or self._connection.is_closed:
            self._connect_to_rabbitmq()
        cost = 10
        if not user.subtract_balance(cost):
            return {"status": "fail", "message": "Insufficient balance"}

        with get_session() as session:
            task = MLTask(
                user_id=user.id,
                model_id=1,
                input_data=json.dumps(input_data),
                status="pending",
                cost=cost
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            try:
                self._channel.basic_publish(
                    exchange='',
                    routing_key='ml_tasks',
                    body=json.dumps({
                        "task_id": task.id,
                        "user_id": user.id,
                        "model_id": 1,
                        "input_data": input_data,
                        "cost": cost
                    })
                )
                print(f"Task {task.id} sent to 'ml_tasks' queue")
                return {"status": "success", "task_id": task.id}
            except Exception as e:
                print(f"Error sending task to queue: {e}")
                session.delete(task)
                session.commit()
                return {"status": "fail", "message": "Failed to send task to queue"}

    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        with get_session() as session:
            task = session.get(MLTask, task_id)
            if not task:
                return {"status": "fail", "message": "Task not found"}
            return {
                "status": task.status,
                "predicted_salary": task.output_data if task.status == "completed" else None
            }

    def close(self):
        if self._connection:
            self._connection.close()
            print("RabbitMQ connection closed")