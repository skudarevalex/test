from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from services.crud.userservice import UserService
from webui.auth.dependencies import get_current_user
import logging

router = APIRouter()
user_service = UserService()
logger = logging.getLogger(__name__)

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: UserCreate):
    result = user_service.register(user.username, user.password)
    if result["status"] == "fail":
        logger.error(f"Registration failed for user: {user.username}")
        raise HTTPException(status_code=400, detail=result["message"])
    logger.info(f"User registered successfully: {user.username}")
    return result

@router.post("/login")
def login(response: Response, user: UserLogin):
    result = user_service.login(user.username, user.password)
    if result["status"] == "fail":
        logger.error(f"Login failed for user: {user.username}")
        raise HTTPException(status_code=400, detail=result["message"])
    
    # Set cookie with the token
    response.set_cookie(
        key="token",
        value=f"{result['access_token']}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    
    logger.info(f"User logged in successfully: {user.username}")
    return {"access_token": result["access_token"], "token_type": "bearer"}
