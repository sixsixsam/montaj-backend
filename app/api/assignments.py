from fastapi import APIRouter, Depends, HTTPException
from .. import schemas, crud, models
from ..db import SessionLocal
from ..deps import require_role, get_current_user
import datetime
router = APIRouter()
@router.post('/', response_model=schemas.AssignmentOut, dependencies=[Depends(require_role('admin'))])
def create_assignment(a: schemas.AssignmentCreate):
    dbs = SessionLocal()
    try:
        try:
            ass = crud.create_assignment(dbs, a.project_id, a.worker_id, a.start_date, a.end_date, a.work_type)
            return ass
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    finally:
        dbs.close()
@router.get('/', response_model=list[schemas.AssignmentOut], dependencies=[Depends(require_role('admin','manager','worker','viewer'))])
def list_assignments(from_date: str = None, to_date: str = None, worker_id: int = None):
    dbs = SessionLocal()
    try:
        fd = None if not from_date else datetime.date.fromisoformat(from_date)
        td = None if not to_date else datetime.date.fromisoformat(to_date)
        return crud.list_assignments(dbs, from_date=fd, to_date=td, worker_id=worker_id)
    finally:
        dbs.close()
@router.delete('/{assignment_id}', dependencies=[Depends(require_role('admin'))])
def delete_assignment(assignment_id: int):
    dbs = SessionLocal()
    try:
        a = dbs.query(models.Assignment).get(assignment_id)
        if not a:
            raise HTTPException(status_code=404, detail='Не найдено')
        today = datetime.date.today()
        if a.start_date <= today:
            actual_end = min(a.end_date, today)
            if actual_end >= a.start_date:
                days = (actual_end - a.start_date).days + 1
                hist = models.AssignmentHistory(assignment_id=a.id, worker_id=a.worker_id, project_id=a.project_id, start_date=a.start_date, end_date=actual_end, days=days, note='Запись при удалении/изменении')
                dbs.add(hist)
                dbs.commit()
        dbs.delete(a); dbs.commit()
        return {'ok': True}
    finally:
        dbs.close()
