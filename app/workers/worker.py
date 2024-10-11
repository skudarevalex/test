import time
import pika
import json
from models.mltask import MLTask
from models.user import User
from database.database import get_session
from models.ml_predictor_module import predict_salary
import os
import sys

# Добавление корневой директории проекта в sys.path для корректного импорта модулей
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

print("Начало выполнения worker")

# Функция-обработчик для обработки сообщений из очереди
def callback(ch, method, properties, body):
    print("Получено сообщение из очереди ml_tasks")
    task_data = json.loads(body)
    
    try:
        prediction = predict_salary(task_data["input_data"])
        predicted_salary = prediction['predicted_salary'].iloc[0]
        print(f"Предсказанная зарплата: {predicted_salary}")
    except Exception as e:
        print(f"Ошибка при предсказании: {e}")
        predicted_salary = None

    with get_session() as session:
        task = session.get(MLTask, task_data["task_id"])
        if not task:
            print(f"Задача с ID {task_data['task_id']} не найдена")
            return

        task.output_data = str(predicted_salary) if predicted_salary is not None else "Error occurred"
        task.status = "completed" if predicted_salary is not None else "failed"
        session.commit()
        print(f"Задача {task.id} обновлена в базе данных")

# Установка соединения с RabbitMQ
def connect_to_rabbitmq():
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
            connection = pika.BlockingConnection(parameters)
            print("Соединение с RabbitMQ установлено")
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
print("Очередь 'ml_tasks' объявлена")

# Настройка функции-обработчика для обработки сообщений из очереди 'ml_tasks'
channel.basic_consume(queue='ml_tasks', on_message_callback=callback, auto_ack=True)
print("Worker подписан на очередь 'ml_tasks' и готов принимать сообщения")

print('Waiting for messages. To exit press CTRL+C')

# Запуск бесконечного цикла для обработки сообщений из очереди
channel.start_consuming()
