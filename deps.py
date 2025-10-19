from fastapi import Depends, HTTPException
from .main import verify_firebase_token, require_role
def get_current_user(user = Depends(verify_firebase_token)):
    return user
