from fastapi import APIRouter, Depends, HTTPException
from .. import schemas, crud
from ..db import SessionLocal
from ..deps import require_role
router = APIRouter()
@router.post('/', response_model=schemas.WorkerOut, dependencies=[Depends(require_role('admin'))])
def create_worker(w: schemas.WorkerCreate):
    dbs = SessionLocal()
    try:
        return crud.create_worker(dbs, w.name, w.phone, w.active)
    finally:
        dbs.close()
@router.get('/', response_model=list[schemas.WorkerOut])
def list_workers():
    dbs = SessionLocal()
    try:
        return crud.list_workers(dbs)
    finally:
        dbs.close()
