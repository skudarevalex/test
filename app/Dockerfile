FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app/

# Устанавливаем переменную окружения PYTHONPATH
ENV PYTHONPATH=/app

# Копирование модели и связанных файлов в контейнер
COPY ./models/best_catboost_model.cbm /app/models/
COPY ./models/target_encoder.joblib /app/models/
COPY ./models/scaler.joblib /app/models/
COPY ./models/tfidf_vectorizer.joblib /app/models/
COPY ./models/feature_names.joblib /app/models/

# Проверка содержимого директории моделей
RUN ls -al /app/models/

EXPOSE 8080

CMD ["python", "api.py"]