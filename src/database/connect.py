import configparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

conf = configparser.ConfigParser()
conf.read('settings.ini')

db = conf.get('postgres', 'db')
user = conf.get('postgres', 'user')
password = conf.get('postgres', 'password')
host = conf.get('postgres', 'host')
port = conf.get('postgres', 'port')

POSTGRES_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(POSTGRES_URL)
DBsession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = DBsession()
    try:
        yield db
    finally:
        db.close()