from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///./task.db'
engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False})

Base = declarative_base()

Session_local = sessionmaker(autocommit = False, autoflush=False , bind = engine)
