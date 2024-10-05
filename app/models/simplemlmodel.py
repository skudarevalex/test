from typing import List
from models.mlmodel import MLModel

# Конкретная реализация простой ML модели
class SimpleMLModel(MLModel):
    def predict(self, data: List[float]) -> List[float]:
        # Метод предсказания, который умножает каждый входной элемент на 2 как простое предсказание
        return [x * 2 for x in data]