from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from .jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    #Модель данных для хранения информации о токене.
    username: Optional[str] = None

def authenticate_user(token: str = Depends(oauth2_scheme)):
    #Функция для проверки подлинности пользователя по токену. Расшифровывает токен и проверяет его валидность.
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token_data
