from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pandas as pd
from services.crud.mlservice import MLService
from database.database import get_session
from models.user import User as UserModel
from webui.auth.dependencies import get_current_user

router = APIRouter()
ml_service = MLService()

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
async def get_prediction(request: PredictionRequest, current_user: UserModel = Depends(get_current_user)):
    try:
        # Преобразование входных данных в формат словаря
        input_data = request.dict()

        # Открытие сессии для работы с базой данных
        with get_session() as session:
            user = session.get(UserModel, current_user.id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Обработка задачи с использованием MLService
            result = ml_service.process_task(user, input_data)
            if result["status"] == "fail":
                raise HTTPException(status_code=400, detail=result["message"])
            
            # Сохранение изменений (например, обновленный баланс)
            session.commit()

        return {"predicted_salary": result["predicted_salary"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))