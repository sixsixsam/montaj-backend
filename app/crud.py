from . import models, utils, db
from sqlalchemy.orm import Session
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
def create_user(db: Session, username: str, password: str, full_name: str, role: str, worker_id=None):
    hashed = utils.get_password_hash(password)
    u = models.User(username=username, full_name=full_name, hashed_password=hashed, role=role, worker_id=worker_id)
    db.add(u); db.commit(); db.refresh(u); return u
def list_workers(db: Session):
    return db.query(models.Worker).order_by(models.Worker.id).all()
def create_worker(db: Session, name: str, phone: str, active: bool=True):
    w = models.Worker(name=name, phone=phone, active=active)
    db.add(w); db.commit(); db.refresh(w); return w
def create_project(db: Session, name: str, client=None, address=None, start_date=None, end_date=None, manager_id=None):
    p = models.Project(name=name, client=client, address=address, start_date=start_date, end_date=end_date, manager_id=manager_id)
    db.add(p); db.commit(); db.refresh(p); return p
def list_projects(db: Session):
    return db.query(models.Project).order_by(models.Project.id).all()
def create_assignment(db: Session, project_id:int, worker_id:int, start_date, end_date, work_type=None):
    w = db.query(models.Worker).get(worker_id)
    if not w or not w.active:
        raise ValueError('Worker not available or inactive')
    a = models.Assignment(project_id=project_id, worker_id=worker_id, start_date=start_date, end_date=end_date, work_type=work_type)
    db.add(a); db.commit(); db.refresh(a); return a
def list_assignments(db: Session, from_date=None, to_date=None, worker_id=None):
    q = db.query(models.Assignment)
    if worker_id:
        q = q.filter(models.Assignment.worker_id == worker_id)
    items = q.all()
    if from_date or to_date:
        res = []
        for a in items:
            if from_date and a.end_date < from_date: continue
            if to_date and a.start_date > to_date: continue
            res.append(a)
        return res
    return items
def delete_assignment(db: Session, assignment_id:int):
    a = db.query(models.Assignment).get(assignment_id)
    if a:
        db.delete(a); db.commit()
        return True
    return False
