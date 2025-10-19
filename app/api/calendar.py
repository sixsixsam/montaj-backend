from fastapi import APIRouter, Depends
from ..db import SessionLocal
from .. import models, schemas
from ..deps import require_role
import datetime
router = APIRouter()
@router.get('/', response_model=schemas.CalendarOut, dependencies=[Depends(require_role('admin','manager','worker','viewer'))])
def get_calendar(from_date: str, to_date: str):
    start = datetime.date.fromisoformat(from_date)
    end = datetime.date.fromisoformat(to_date)
    dates = []
    cur = start
    while cur <= end:
        dates.append(cur.isoformat())
        cur += datetime.timedelta(days=1)
    dbs = SessionLocal()
    try:
        workers = dbs.query(models.Worker).order_by(models.Worker.id).all()
        assignments = dbs.query(models.Assignment).all()
        rows = []
        for w in workers:
            cells = {d: None for d in dates}
            for a in [x for x in assignments if x.worker_id == w.id]:
                cur = a.start_date
                while cur <= a.end_date:
                    iso = cur.isoformat()
                    if iso in cells:
                        proj_name = a.project.name if a.project else None
                        cells[iso] = schemas.CalendarCell(project=proj_name, work_type=a.work_type)
                    cur += datetime.timedelta(days=1)
            rows.append(schemas.CalendarRow(worker_id=w.id, worker_name=w.name, cells=cells))
        return schemas.CalendarOut(dates=dates, rows=rows)
    finally:
        dbs.close()
