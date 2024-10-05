import pytest
from services.crud.mlservice import MLService
from models.mlmodelmanager import MLModelManager

@pytest.fixture
def ml_service():
    model_manager = MLModelManager()
    return MLService(model_manager)

def test_process_task(ml_service):
    user = ...  # Создайте или получите пользователя
    model_id = 1
    input_data = "1.0, 2.0, 3.0"
    result = ml_service.process_task(user, model_id, input_data)
    assert result["status"] == "success"
