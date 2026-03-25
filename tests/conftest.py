"""
    Módulo que se encarga de crear una db en memoria para las pruebas
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base  # here residdes declarative_base()


# 1. Creates a test engine database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL)


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
