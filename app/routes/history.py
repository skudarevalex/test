from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from database.database import get_session
from models.mltask import MLTask as MLTaskModel
from webui.auth.dependencies import get_current_user
from models.user import User

router = APIRouter()

@router.get("/{user_id}")
def get_history(user_id: int, current_user: User = Depends(get_current_user)) -> List[Dict[str, Any]]:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this history")
    with get_session() as session:
        tasks = session.query(MLTaskModel).filter_by(user_id=user_id).order_by(MLTaskModel.created_at.desc()).all()
        return [
            {
                "id": task.id,
                "model_id": task.model_id,
                "input_data": task.input_data,
                "output_data": task.output_data,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "cost": task.cost
            } for task in tasks
        ]