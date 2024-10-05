from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from .jwt_handler import SECRET_KEY, ALGORITHM, decode_access_token
from services.crud.userservice import UserService

# class OAuth2PasswordBearerWithCookie(OAuth2):
#     def __init__(self, tokenUrl: str, scheme_name: str = None, scopes: dict = None, auto_error: bool = True):
#         if not scopes:
#             scopes = {}
#         flows = {"password": {"tokenUrl": tokenUrl, "scopes": scopes}}
#         super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

#     async def __call__(self, request: Request) -> str:
#         token = request.cookies.get("token")
#         if not token:
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=401,
#                     detail="Not authenticated",
#                     headers={"WWW-Authenticate": "Bearer"},
#                 )
#             else:
#                 return None
#         return token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService()
    user = user_service.get_user_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user
