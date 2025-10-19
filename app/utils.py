from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from io import BytesIO
import os, secrets, hashlib
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change_this_secret')
ALGORITHM = 'HS256'
ACCESS_EXPIRE_MINUTES = int(os.environ.get('ACCESS_EXPIRE_MINUTES', 15))
REFRESH_EXPIRE_DAYS = int(os.environ.get('REFRESH_EXPIRE_DAYS', 30))
def get_password_hash(pw: str) -> str:
    return pwd_context.hash(pw)
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def generate_refresh_token():
    return secrets.token_urlsafe(64)
def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()
def export_worker_report(assignments, worker_name):
    wb = Workbook(); ws = wb.active
    ws.append(['Проект','Дата начала','Дата окончания','Тип работы','Дни'])
    for a in assignments:
        proj = a.project.name if a.project else ''
        s = a.start_date.isoformat()
        e = a.end_date.isoformat()
        days = (a.end_date - a.start_date).days + 1
        ws.append([proj, s, e, a.work_type or '', days])
    bio = BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(content=bio, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition':f'attachment; filename=report_worker_{worker_name}.xlsx'})
def export_projects_report(projects):
    wb = Workbook(); ws = wb.active
    ws.append(['Проект','Клиент','Адрес','Дата начала','Дата окончания','Статус'])
    for p in projects:
        ws.append([p.name or '', p.client or '', p.address or '', p.start_date.isoformat() if p.start_date else '', p.end_date.isoformat() if p.end_date else '', p.status or ''])
    bio = BytesIO(); wb.save(bio); bio.seek(0)
    return StreamingResponse(content=bio, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition':'attachment; filename=report_projects.xlsx'})
