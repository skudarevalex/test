from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pandas as pd
from services.crud.mlservice import MLService
from database.database import get_session
from models.user import User as UserModel
from models.mltask import MLTask
from webui.auth.dependencies import get_current_user

router = APIRouter()
ml_service = MLService()

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

@router.post("/predict_salary")
async def create_prediction_task(request: PredictionRequest, current_user: UserModel = Depends(get_current_user)):
    try:
        input_data = request.dict()
        with get_session() as session:
            user = session.get(UserModel, current_user.id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            result = ml_service.create_task(user, input_data)
            if result["status"] == "fail":
                raise HTTPException(status_code=400, detail=result["message"])
            
            session.commit()
        
        return {"task_id": result["task_id"], "message": "Prediction task created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prediction_status/{task_id}")
async def get_prediction_status(task_id: int, current_user: UserModel = Depends(get_current_user)):
    try:
        with get_session() as session:
            task = session.get(MLTask, task_id)
            if not task or task.user_id != current_user.id:
                raise HTTPException(status_code=404, detail="Task not found")
            
            if task.status == "completed":
                return {"status": "completed", "predicted_salary": task.output_data}
            else:
                return {"status": task.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))