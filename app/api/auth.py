from fastapi import APIRouter, HTTPException, Response, Cookie
from .. import crud, utils, models
from ..db import SessionLocal
from .. import schemas
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
router = APIRouter()
@router.post('/auth/login', response_model=schemas.Token)
def login(data: schemas.LoginIn, response: Response):
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, data.username)
        if not user or not utils.verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail='Неверные учетные данные')
        access_token = utils.create_access_token({'sub': user.username, 'role': user.role, 'user_id': user.id}, expires_delta=timedelta(minutes=utils.ACCESS_EXPIRE_MINUTES))
        refresh = utils.generate_refresh_token()
        r_hash = utils.hash_token(refresh)
        expires_at = datetime.utcnow() + timedelta(days=utils.REFRESH_EXPIRE_DAYS)
        rt = models.RefreshToken(token_hash=r_hash, user_id=user.id, expires_at=expires_at)
        db.add(rt); db.commit()
        response.set_cookie('refresh_token', refresh, httponly=True, secure=False, samesite='lax', max_age=utils.REFRESH_EXPIRE_DAYS*24*3600)
        return {'access_token': access_token, 'token_type': 'bearer'}
    finally:
        db.close()
@router.post('/auth/refresh', response_model=schemas.Token)
def refresh(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail='No refresh token')
    db = SessionLocal()
    try:
        token_hash = utils.hash_token(refresh_token)
        rt = db.query(models.RefreshToken).filter(models.RefreshToken.token_hash==token_hash, models.RefreshToken.revoked==False).first()
        if not rt or rt.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail='Invalid refresh token')
        user = db.query(models.User).get(rt.user_id)
        if not user:
            raise HTTPException(status_code=401, detail='User not found')
        access_token = utils.create_access_token({'sub': user.username, 'role': user.role, 'user_id': user.id}, expires_delta=timedelta(minutes=utils.ACCESS_EXPIRE_MINUTES))
        return {'access_token': access_token, 'token_type': 'bearer'}
    finally:
        db.close()
@router.post('/auth/logout')
def logout(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token:
        db = SessionLocal()
        try:
            token_hash = utils.hash_token(refresh_token)
            rt = db.query(models.RefreshToken).filter(models.RefreshToken.token_hash==token_hash).first()
            if rt:
                rt.revoked = True
                db.commit()
        finally:
            db.close()
    response.delete_cookie('refresh_token')
    return {'ok': True}
