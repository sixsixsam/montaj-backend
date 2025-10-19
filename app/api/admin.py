from fastapi import APIRouter, Depends, HTTPException
from ..db import SessionLocal
from .. import models, utils
from ..deps import require_role
router = APIRouter()
@router.post('/reset-password', dependencies=[Depends(require_role('admin'))])
def reset_password(user_id: int, new_password: str):
    dbs = SessionLocal()
    try:
        u = dbs.query(models.User).get(user_id)
        if not u:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
        u.hashed_password = utils.get_password_hash(new_password)
        dbs.commit()
        return {'ok': True}
    finally:
        dbs.close()
@router.post('/set-role', dependencies=[Depends(require_role('admin'))])
def set_role(user_id: int, role: str):
    dbs = SessionLocal()
    try:
        u = dbs.query(models.User).get(user_id)
        if not u:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
        u.role = role
        dbs.commit()
        return {'ok': True}
    finally:
        dbs.close()
