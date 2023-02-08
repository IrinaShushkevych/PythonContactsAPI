from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

from src.database import engine

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(150), nullable=False)
    lastname = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    born_date = Column(Date, nullable=True)
    notes = Column(String(500), nullable=True)

