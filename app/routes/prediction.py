from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pandas as pd
from models.ml_predictor_module import predict_salary
from services.crud.userservice import UserService
from webui.auth.dependencies import get_current_user

router = APIRouter()
user_service = UserService()

# Определение модели данных для запроса
class PredictionRequest(BaseModel):
    work_year: int
    experience_level: str
    employment_type: str
    job_category: str
    job_tags: str
    employee_residence: str
    remote_ratio: int
    company_location: str
    company_size: str

# Определение эндпойнта для предсказаний
@router.post("/predict_salary")
async def get_prediction(request: PredictionRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Проверка, достаточно ли средств на балансе
        user = user_service.get_user_by_id(current_user['id'])
        if not user or user.balance < 10:
            raise HTTPException(status_code=400, detail="Недостаточно средств для получения предсказания")

        # Преобразование входных данных в формат DataFrame
        input_data = pd.DataFrame([request.dict()])
        
        # Получение предсказания с помощью функции predict_salary
        prediction = predict_salary(input_data)
        
        # Извлечение предсказанного значения
        predicted_salary = prediction['predicted_salary'].iloc[0]
        
        # Списывание средств с баланса
        user_service.subtract_balance(user.id, 10)
        
        return {"predicted_salary": predicted_salary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
