from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.crud.userservice import UserService
from webui.auth.dependencies import get_current_user
from models.user import User

router = APIRouter()
user_service = UserService()

class BalanceUpdate(BaseModel):
    amount: int

@router.get("/{user_id}")
def get_balance(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this balance")
    return user_service.get_user_balance(user_id)

@router.post("/{user_id}/add")
def add_balance(user_id: int, balance_update: BalanceUpdate, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add balance to this user")
    user_service.add_balance(user_id, balance_update.amount)
    return {"status": "success", "message": "Balance updated successfully"}
