from fastapi import APIRouter, Depends
from .. import schemas, crud
from ..db import SessionLocal
from ..deps import require_role, get_current_user
router = APIRouter()
@router.post('/', response_model=schemas.ProjectOut, dependencies=[Depends(require_role('admin','manager'))])
def create_project(p: schemas.ProjectCreate, current=Depends(get_current_user)):
    dbs = SessionLocal()
    try:
        mgr_id = current.get('user_id')
        return crud.create_project(dbs, p.name, p.client, p.address, p.start_date, p.end_date, mgr_id)
    finally:
        dbs.close()
@router.get('/', response_model=list[schemas.ProjectOut])
def list_projects():
    dbs = SessionLocal()
    try:
        return crud.list_projects(dbs)
    finally:
        dbs.close()
