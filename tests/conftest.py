from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi_limiter.depends import RateLimiter

from src.database.models import Base
from src.database.connect import get_db
from main import app

SQLALCHEMY_DB_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app.dependency_overrides[RateLimiter] = {}

@pytest.fixture(scope='module')
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope='module')
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db


    yield TestClient(app)


@pytest.fixture(scope='module')
def user():
    return {'username': 'Irina', 'email': 'IraOlijnyk@gmail.com', 'password': 'qwert-11'}


@pytest.fixture(scope='module')
def wrong_user():
    return {'username': 'Guest', 'email': 'QQQ@gmail.com', 'password': 'qwert-11'}

