import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_database():
    try:
        Base.metadata.create_all(bind=engine)
        yield
    finally:
        # Base.metadata.drop_all(bind=engine) # Dropping all might interfere with other parallel runs, but since it's a test db, okay
        pass

@pytest.fixture
def db(setup_database):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
