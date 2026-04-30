"""
    Módulo que se encarga de crear una db en memoria para las pruebas
"""
from fastapi.testclient import TestClient
from app.main import app

import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from app.db.base import Base  # here residdes declarative_base()
from app.db.sessions import get_db


# 1. Creates a test engine database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       'check_same_thread': False}, poolclass=StaticPool)


# 2.  SessionLocal for testing
TestingSessionLocal = sessionmaker(bind=engine)


# 3. Creates the tables before the tests
@pytest.fixture(scope="function")
def session():
    # Create stables
    Base.metadata.create_all(bind=engine)

    # Creates session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Delete al ltables after the testing
        Base.metadata.drop_all(bind=engine)


def get_db_override() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):

    app.dependency_overrides[get_db] = get_db_override

    return TestClient(app)
