from fastapi import APIRouter, Depends, HTTPException
from .. import schemas, crud
from ..db import SessionLocal
from ..deps import require_role
router = APIRouter()
@router.post('/', response_model=schemas.UserOut, dependencies=[Depends(require_role('admin'))])
def create_user(user: schemas.UserCreate):
    dbs = SessionLocal()
    try:
        existing = crud.get_user_by_username(dbs, user.username)
        if existing:
            raise HTTPException(status_code=400, detail='Пользователь уже существует')
        u = crud.create_user(dbs, user.username, user.password, user.full_name, user.role, user.worker_id)
        return u
    finally:
        dbs.close()
@router.get('/', response_model=list[schemas.UserOut], dependencies=[Depends(require_role('admin'))])
def list_users():
    dbs = SessionLocal()
    try:
        users = dbs.query(__import__('app').models.User).all()
        return users
    finally:
        dbs.close()
