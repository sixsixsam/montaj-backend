from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .db import Base
import datetime
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default='viewer')
    worker_id = Column(Integer, ForeignKey('workers.id'), nullable=True)
    worker = relationship('Worker', back_populates='user')
class Worker(Base):
    __tablename__ = 'workers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    user = relationship('User', uselist=False, back_populates='worker')
    assignments = relationship('Assignment', back_populates='worker')
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client = Column(String, nullable=True)
    address = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String, default='planned')
    assignments = relationship('Assignment', back_populates='project', cascade='all, delete-orphan')
class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    worker_id = Column(Integer, ForeignKey('workers.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    work_type = Column(String, nullable=True)
    project = relationship('Project', back_populates='assignments')
    worker = relationship('Worker', back_populates='assignments')
class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
class AssignmentHistory(Base):
    __tablename__ = 'assignment_history'
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, nullable=True)
    worker_id = Column(Integer, ForeignKey('workers.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    note = Column(String, nullable=True)
