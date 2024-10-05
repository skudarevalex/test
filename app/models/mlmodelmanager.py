from abc import ABC
from typing import Dict, Optional
from models.simplemlmodel import SimpleMLModel
from models.mlmodel import MLModel
from models.ml_predictor_module import loaded_catboost, loaded_target_encoder, loaded_scaler, loaded_tfidf, feature_names, predict_salary  # Импортируем необходимые объекты и функции

# Менеджер классов для управления загрузкой и получением ML моделей
class MLModelManager:
    def __init__(self):
        # Инициализация с экземпляром базы данных
        self._models: Dict[int, MLModel] = {}
        self.load_models()

    def load_models(self):
        # Загрузка моделей из источника (например, базы данных, файла)
        self._models[1] = SimpleMLModel()
        # Добавляем загрузку кастомной модели
        self._models[2] = loaded_catboost

    def get_model(self, model_id: int) -> Optional[MLModel]:
        # Получение модели по её ID
        return self._models.get(model_id)