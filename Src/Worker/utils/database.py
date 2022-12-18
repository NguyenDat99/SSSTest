# from flask import Flask
from sqlalchemy import create_engine, MetaData, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import CONFIG
from sqlalchemy import Column, Integer, DateTime

# app = Flask(__name__)
engine = create_engine(CONFIG['database']['url'])

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class Log(Base):
    __tablename__ = 'logs'
    id = Column('id', Integer(), index=True, primary_key=True)
    time = Column('time', DateTime(), index=True, nullable=False)
    url = Column('url', VARCHAR(500), index=True, nullable=False)


Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
