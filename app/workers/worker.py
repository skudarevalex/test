# import sys
# from pathlib import Path

# # Добавляем корневую директорию проекта в sys.path
# current_dir = Path(__file__).resolve().parent
# root_dir = current_dir.parent.parent
# sys.path.append(str(root_dir))

# # Проверка текущих путей
# print("Current sys.path:", sys.path)

import os
import time
import pika
import json
from models.mlmodelmanager import MLModelManager
from database.database import get_session
from models.user import User
from models.mltask import MLTask

# Создание экземпляра менеджера моделей и загрузка моделей
model_manager = MLModelManager()
model_manager.load_models()

# Функция-обработчик для обработки сообщений из очереди
def callback(ch, method, properties, body):
    # Парсинг JSON сообщения
    task = json.loads(body)
    
    # Получение модели по ID
    model = model_manager.get_model(task["model_id"])

    if model:
        # Выполнение предсказания с использованием модели
        predictions = model.predict(task["input_data"])
        
        # Открытие сессии для работы с базой данных
        with get_session() as session:
            # Получение пользователя по ID
            user = session.get(User, task["user_id"])
            
            # Создание записи о задаче в базе данных
            ml_task = MLTask(
                user_id=task["user_id"],
                model_id=task["model_id"],
                input_data=','.join(map(str, task["input_data"])),
                output_data=','.join(map(str, predictions)),
                status="completed",
                cost=task["cost"]
            )
            
            # Добавление записи в сессию и сохранение изменений
            session.add(ml_task)
            session.commit()

# Установка соединения с RabbitMQ
def connect_to_rabbitmq():
    attempts = 10
    while attempts > 0:
        try:
            print("Attempting to connect to RabbitMQ, attempts left:", attempts)
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST'),
                port=int(os.getenv('RABBITMQ_PORT')),
                credentials=pika.PlainCredentials(os.getenv('RABBITMQ_USER'), os.getenv('RABBITMQ_PASS'))
            ))
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print("Connection to RabbitMQ failed:", e)
            attempts -= 1
            time.sleep(10)
            if attempts == 0:
                raise

connection = connect_to_rabbitmq()
channel = connection.channel()

# Объявление очереди 'ml_tasks' (если не существует, она будет создана)
channel.queue_declare(queue='ml_tasks')

# Настройка функции-обработчика для обработки сообщений из очереди 'ml_tasks'
channel.basic_consume(queue='ml_tasks', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')

# Запуск бесконечного цикла для обработки сообщений из очереди
channel.start_consuming()
