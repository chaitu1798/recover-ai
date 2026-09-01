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

@pytest.fixture
def sample_payment(db):
    from app.models.merchant import Merchant
    from app.models.payment import Payment
    import uuid
    merchant = Merchant(name="Test Merchant")
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    
    payment = Payment(
        merchant_id=merchant.id,
        amount=1000,
        currency="INR",
        method="card",
        status="failed",
        error_code="BAD_REQUEST",
        error_description="Test error",
        razorpay_payment_id=f"pay_{uuid.uuid4().hex[:14]}"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
