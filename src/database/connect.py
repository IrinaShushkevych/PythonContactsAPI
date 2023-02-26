from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings


POSTGRES_URL = settings.sqlalchemy_url
engine = create_engine(POSTGRES_URL)
DBsession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = DBsession()
    try:
        yield db
    finally:
        db.close()