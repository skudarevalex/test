from abc import ABC, abstractmethod
from typing import List


# Абстрактный базовый класс для ML моделей
class MLModel(ABC):
    @abstractmethod
    def predict(self, data: List[float]) -> List[float]:
        # Абстрактный метод для выполнения предсказаний, который должен быть реализован подклассами
        pass