from fastapi import APIRouter, Depends, Query
from ..db import SessionLocal
from .. import models, utils
from ..deps import require_role
import datetime
router = APIRouter()
@router.get('/worker', dependencies=[Depends(require_role('admin','manager'))])
def worker_report(worker_id: int = Query(...), from_date: str = Query(...), to_date: str = Query(...)):
    dbs = SessionLocal()
    try:
        fd = datetime.date.fromisoformat(from_date)
        td = datetime.date.fromisoformat(to_date)
        items = dbs.query(models.Assignment).filter(models.Assignment.worker_id == worker_id).all()
        rows = [i for i in items if not (i.end_date < fd or i.start_date > td)]
        worker = dbs.query(models.Worker).get(worker_id)
        return utils.export_worker_report(rows, worker.name if worker else f'worker_{worker_id}')
    finally:
        dbs.close()
@router.get('/projects', dependencies=[Depends(require_role('admin','manager'))])
def projects_report(from_date: str = Query(...), to_date: str = Query(...)):
    dbs = SessionLocal()
    try:
        fd = datetime.date.fromisoformat(from_date)
        td = datetime.date.fromisoformat(to_date)
        items = dbs.query(models.Project).all()
        rows = [p for p in items if not (p.end_date and p.end_date < fd or p.start_date and p.start_date > td)]
        return utils.export_projects_report(rows)
    finally:
        dbs.close()
