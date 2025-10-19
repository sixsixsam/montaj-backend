from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import os
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change_this_secret')
ALGORITHM = 'HS256'
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
def require_role(*roles):
    def checker(current=Depends(get_current_user)):
        if current.get('role') not in roles:
            raise HTTPException(status_code=403, detail='Нет доступа')
        return current
    return checker
