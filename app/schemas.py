from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date
class Token(BaseModel):
    access_token: str
    token_type: str
class LoginIn(BaseModel):
    username: str
    password: str
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str]
    role: str
    worker_id: Optional[int]
class UserOut(BaseModel):
    id: int; username: str; full_name: Optional[str]; role: str; worker_id: Optional[int]
    class Config: orm_mode = True
class WorkerCreate(BaseModel):
    name: str; phone: Optional[str]; active: bool = True
class WorkerOut(BaseModel):
    id: int; name: str; phone: Optional[str]; active: bool
    class Config: orm_mode = True
class ProjectCreate(BaseModel):
    name: str; client: Optional[str]; address: Optional[str]; start_date: Optional[date]; end_date: Optional[date]
class ProjectOut(BaseModel):
    id: int; name: str; client: Optional[str]; address: Optional[str]; start_date: Optional[date]; end_date: Optional[date]; status: Optional[str]
    class Config: orm_mode = True
class AssignmentCreate(BaseModel):
    project_id: int; worker_id: int; start_date: date; end_date: date; work_type: Optional[str]
class AssignmentOut(BaseModel):
    id: int; project_id: int; worker_id: int; start_date: date; end_date: date; work_type: Optional[str]
    class Config: orm_mode = True
class CalendarCell(BaseModel):
    project: Optional[str]; work_type: Optional[str]
class CalendarRow(BaseModel):
    worker_id: int; worker_name: str; cells: Dict[str, CalendarCell]
class CalendarOut(BaseModel):
    dates: List[str]; rows: List[CalendarRow]
