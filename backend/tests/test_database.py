import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Merchant, Customer, Order, Payment, PaymentEvent, RecoveryCase
from app.models.enums import PaymentStatus, RecoveryAction
from sqlalchemy.exc import IntegrityError

# Use an in-memory SQLite database for testing schema/constraints if Postgres isn't available
# Wait, PostgreSQL specific types like UUID and JSONB are used.
# Let's import the actual database configuration to test against the real DB, 
# or use a test postgres db. If postgres is down, tests will fail to connect.
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_merchant_creation(db):
    try:
        merchant = Merchant(name="Test Merchant", currency="INR")
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        assert merchant.id is not None
        assert merchant.name == "Test Merchant"
    except Exception as e:
        pytest.fail(f"Test failed: {e}")

def test_customer_creation(db):
    try:
        merchant = Merchant(name="Test Merchant", currency="INR")
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        
        customer = Customer(merchant_id=merchant.id, name="Test Customer", total_spend=50000)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        assert customer.id is not None
        assert customer.merchant_id == merchant.id
        
        # Test money constraint (integer minor units)
        assert customer.total_spend == 50000
    except Exception as e:
        pytest.fail(f"Test failed: {e}")

def test_payment_and_case(db):
    try:
        merchant = Merchant(name="Test Merchant", currency="INR")
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        
        customer = Customer(merchant_id=merchant.id, name="Test Customer", total_spend=50000)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        # Test money storage
        payment = Payment(
            merchant_id=merchant.id,
            customer_id=customer.id,
            razorpay_payment_id=f"pay_{uuid.uuid4().hex[:14]}",
            amount=499900,  # ₹4,999.00 -> 499900 paise
            currency="INR",
            status=PaymentStatus.failed
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        assert payment.amount == 499900
        assert type(payment.amount) == int
        
        # Test recovery case relationship
        rc = RecoveryCase(
            payment_id=payment.id,
            amount_at_risk=payment.amount,
            status="open"
        )
        db.add(rc)
        db.commit()
        
        assert len(payment.recovery_cases) > 0
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
