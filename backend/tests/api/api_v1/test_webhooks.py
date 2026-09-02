import pytest
import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.config import settings
from app.models import PaymentEvent, Payment, RecoveryCase, AuditLog, Merchant, Customer
import uuid
from app.database import get_db

@pytest.fixture
def client(db: Session):
    def _get_db():
        yield db
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def generate_signature(payload: str, secret: str) -> str:
    return hmac.new(
        key=secret.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

def test_missing_signature(client):
    response = client.post("/api/v1/webhooks/razorpay", json={"test": "data"})
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Missing signature"

def test_invalid_signature(client):
    response = client.post(
        "/api/v1/webhooks/razorpay",
        json={"test": "data"},
        headers={"X-Razorpay-Signature": "invalid_sig"}
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Invalid signature"

def test_malformed_json(client):
    secret = settings.RAZORPAY_WEBHOOK_SECRET = "test_secret"
    payload = "{invalid_json}"
    signature = generate_signature(payload, secret)
    response = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload,
        headers={"X-Razorpay-Signature": signature}
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Malformed JSON"

def test_missing_event_id(db: Session, client):
    secret = settings.RAZORPAY_WEBHOOK_SECRET = "test_secret"
    payload = json.dumps({"event": "payment.failed"})
    signature = generate_signature(payload, secret)
    response = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload,
        headers={"X-Razorpay-Signature": signature}
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Missing event ID or type"

def test_unsupported_event(db: Session, client):
    secret = settings.RAZORPAY_WEBHOOK_SECRET = "test_secret"
    payload = json.dumps({"id": "evt_test", "event": "order.paid"})
    signature = generate_signature(payload, secret)
    response = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload,
        headers={"X-Razorpay-Signature": signature}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "reason": "unsupported_event"}

def test_payment_failed_webhook(db: Session, client):
    # Setup mock data
    merchant = Merchant(name="Test Merchant")
    db.add(merchant)
    db.commit()
    customer = Customer(merchant_id=merchant.id, email="test@test.com")
    db.add(customer)
    db.commit()
    payment = Payment(
        merchant_id=merchant.id,
        customer_id=customer.id,
        razorpay_payment_id="pay_test_001",
        amount=100000,
        currency="INR",
        status="authorized"
    )
    db.add(payment)
    db.commit()
    
    with open("backend/tests/fixtures/razorpay/payment_failed.json", "r") as f:
        payload_dict = json.load(f)
    
    # ensure uniqueness
    payload_dict["id"] = str(uuid.uuid4())
    
    secret = settings.RAZORPAY_WEBHOOK_SECRET = "test_secret"
    payload = json.dumps(payload_dict)
    signature = generate_signature(payload, secret)
    
    response = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload,
        headers={"X-Razorpay-Signature": signature}
    )
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    
    db.refresh(payment)
    assert payment.status == "failed"
    assert payment.error_code == "BAD_REQUEST_ERROR"
    
    event = db.query(PaymentEvent).filter(PaymentEvent.razorpay_event_id == payload_dict["id"]).first()
    assert event is not None
    assert event.processing_status == "processed"
    
    case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment.id).first()
    assert case is not None
    assert case.status == "open"
    assert case.amount_at_risk == payment.amount
    
    log = db.query(AuditLog).filter(AuditLog.entity_id == event.id).first()
    assert log is not None
    assert log.action == "webhook_processed"

def test_duplicate_webhook(db: Session, client):
    merchant = Merchant(name="Test Merchant")
    db.add(merchant)
    db.commit()
    payment = Payment(merchant_id=merchant.id, razorpay_payment_id="pay_test_001", amount=100000, currency="INR", status="authorized")
    db.add(payment)
    db.commit()

    with open("backend/tests/fixtures/razorpay/payment_failed.json", "r") as f:
        payload_dict = json.load(f)
        
    payload_dict["id"] = str(uuid.uuid4())

    
    secret = settings.RAZORPAY_WEBHOOK_SECRET = "test_secret"
    payload = json.dumps(payload_dict)
    signature = generate_signature(payload, secret)
    
    # First request
    response1 = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload,
        headers={"X-Razorpay-Signature": signature}
    )
    assert response1.status_code == 200
    
    # Second request
    response2 = client.post(
        "/api/v1/webhooks/razorpay",
        content=payload,
        headers={"X-Razorpay-Signature": signature}
    )
    assert response2.status_code == 200
    assert response2.json() == {"status": "duplicate", "message": "Event already processed"}
    
    events = db.query(PaymentEvent).filter(PaymentEvent.razorpay_event_id == payload_dict["id"]).all()
    assert len(events) == 1
    
    # check that we didn't duplicate the recovery case
    payment = db.query(Payment).filter(Payment.razorpay_payment_id == "pay_test_001").first()
    cases = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment.id).all()
    assert len(cases) == 1

def test_payment_captured_webhook(db: Session, client):
    merchant = Merchant(name="Test Merchant")
    db.add(merchant)
    db.commit()
    payment = Payment(merchant_id=merchant.id, razorpay_payment_id="pay_test_001", amount=100000, currency="INR", status="authorized")
    db.add(payment)
    db.commit()
    
    with open("backend/tests/fixtures/razorpay/payment_captured.json", "r") as f:
        payload_dict = json.load(f)
    payload_dict["id"] = str(uuid.uuid4())
    secret = settings.RAZORPAY_WEBHOOK_SECRET = "test_secret"
    payload = json.dumps(payload_dict)
    signature = generate_signature(payload, secret)
    
    response = client.post("/api/v1/webhooks/razorpay", content=payload, headers={"X-Razorpay-Signature": signature})
    assert response.status_code == 200
    db.refresh(payment)
    assert payment.status == "captured"

def test_payment_authorized_webhook(db: Session, client):
    merchant = Merchant(name="Test Merchant")
    db.add(merchant)
    db.commit()
    payment = Payment(merchant_id=merchant.id, razorpay_payment_id="pay_test_001", amount=100000, currency="INR", status="created")
    db.add(payment)
    db.commit()
    
    with open("backend/tests/fixtures/razorpay/payment_authorized.json", "r") as f:
        payload_dict = json.load(f)
    payload_dict["id"] = str(uuid.uuid4())
    secret = settings.RAZORPAY_WEBHOOK_SECRET = "test_secret"
    payload = json.dumps(payload_dict)
    signature = generate_signature(payload, secret)
    
    response = client.post("/api/v1/webhooks/razorpay", content=payload, headers={"X-Razorpay-Signature": signature})
    assert response.status_code == 200
    db.refresh(payment)
    assert payment.status == "authorized"
