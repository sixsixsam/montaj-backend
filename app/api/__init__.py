from fastapi import APIRouter
from . import auth, users, workers, projects, assignments, calendar, reports, admin
router = APIRouter()
router.include_router(auth.router, prefix='', tags=['auth'])
router.include_router(users.router, prefix='/users', tags=['users'])
router.include_router(workers.router, prefix='/workers', tags=['workers'])
router.include_router(projects.router, prefix='/projects', tags=['projects'])
router.include_router(assignments.router, prefix='/assignments', tags=['assignments'])
router.include_router(calendar.router, prefix='/calendar', tags=['calendar'])
router.include_router(reports.router, prefix='/reports', tags=['reports'])
router.include_router(admin.router, prefix='/admin', tags=['admin'])
