from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data.db')
DATABASE_URL = os.environ.get('DATABASE_URL', f"sqlite:///{DB_FILE}")
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
