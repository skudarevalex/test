import pandas as pd
import numpy as np
import joblib
from catboost import CatBoostRegressor
from typing import Optional
from models.user import User  # Импортируем User из user.py
from database.database import get_session

# Загрузка модели и других необходимых объектов
loaded_catboost = CatBoostRegressor()
loaded_catboost.load_model('/app/models/best_catboost_model.cbm')
loaded_target_encoder = joblib.load('/app/models/target_encoder.joblib')
loaded_scaler = joblib.load('/app/models/scaler.joblib')
loaded_tfidf = joblib.load('/app/models/tfidf_vectorizer.joblib')
feature_names = joblib.load('/app/models/feature_names.joblib')

def predict_salary(input_data):
    """
    Функция принимает новые данные и возвращает предсказанные зарплаты.
    
    Parameters:
    input_data (dict или pd.DataFrame): Новые данные для предсказания.
    
    Returns:
    pd.DataFrame: Предсказанные зарплаты.
    """
    # Если входные данные в формате словаря, преобразуем в DataFrame
    if isinstance(input_data, dict):
        input_df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.DataFrame):
        input_df = input_data.copy()
    else:
        raise ValueError("input_data должен быть словарём или DataFrame.")
    
    # Шаг 1: Обработка категориальных признаков (OHE и Target Encoding)
    
    # One-Hot Encoding для низкой кардинальности
    ohe_cols = ['experience_level', 'employment_type', 'company_size']
    input_ohe = pd.get_dummies(input_df[ohe_cols])
    
    # Корректировка имен столбцов для One-Hot Encoding
    expected_ohe_cols = [col for col in feature_names if any(col.startswith(prefix) for prefix in ohe_cols)]
    input_ohe = input_ohe.reindex(columns=expected_ohe_cols, fill_value=0)
    
    # Target Encoding для высококардинальных колонок
    target_enc_cols = ['job_category', 'company_location', 'employee_residence']
    input_target_enc = loaded_target_encoder.transform(input_df[target_enc_cols])
    input_target_enc = pd.DataFrame(input_target_enc, columns=target_enc_cols)
    
    # Шаг 2: Масштабирование числовых признаков
    numerical_cols = ['work_year', 'remote_ratio']
    input_scaled = loaded_scaler.transform(input_df[numerical_cols])
    input_scaled = pd.DataFrame(input_scaled, columns=numerical_cols)
    
    # Шаг 3: Обработка TF-IDF признаков
    if 'job_tags' in input_df.columns:
        job_tags_tfidf = loaded_tfidf.transform(input_df['job_tags']).toarray()
        job_tags_tfidf = pd.DataFrame(job_tags_tfidf, columns=loaded_tfidf.get_feature_names_out())
    else:
        job_tags_tfidf = pd.DataFrame(columns=loaded_tfidf.get_feature_names_out())
    
    # Добавление отсутствующих TF-IDF столбцов
    for col in loaded_tfidf.get_feature_names_out():
        if col not in job_tags_tfidf.columns:
            job_tags_tfidf[col] = 0
    
    # Шаг 4: Переименование TF-IDF признаков для соответствия обучающим данным
    job_tags_tfidf.rename(columns=lambda x: f"tfidf_{x}", inplace=True)
    
    # Шаг 5: Объединение всех признаков
    X_processed = pd.concat([
        input_scaled,
        input_ohe,
        input_target_enc,
        job_tags_tfidf
    ], axis=1)
    
    # Шаг 6: Убедимся, что все необходимые признаки присутствуют
    for col in feature_names:
        if col not in X_processed.columns:
            X_processed[col] = 0
    
    X_processed = X_processed[feature_names]

    # Шаг 7: Предсказание
    predicted_salary_log = loaded_catboost.predict(X_processed)
    
    # Обратная трансформация логарифмической целевой переменной, если применялась
    predicted_salary = np.expm1(predicted_salary_log)
    
    # Возвращаем предсказанные зарплаты
    return pd.DataFrame({
        'predicted_salary': predicted_salary
    })