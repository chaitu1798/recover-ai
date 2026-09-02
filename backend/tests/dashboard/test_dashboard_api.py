import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment
from app.models.enums import ApprovalStatus

from app.database import get_db

client = TestClient(app)

def test_get_dashboard_metrics(db: Session, sample_payment: Payment):
    app.dependency_overrides[get_db] = lambda: db
    # Add a pending case
    case1 = RecoveryCase(
        payment_id=sample_payment.id, 
        amount_at_risk=1000,
        status="pending_approval",
        approval_status=ApprovalStatus.PENDING_APPROVAL.value,
        recovery_probability=0.8
    )
    # Add an approved case
    case2 = RecoveryCase(
        payment_id=sample_payment.id, 
        amount_at_risk=2000,
        status="approved",
        approval_status=ApprovalStatus.APPROVED.value,
        recovery_probability=0.5
    )
    
    db.add(case1)
    db.add(case2)
    db.commit()

    response = client.get("/api/v1/dashboard/metrics")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_cases"] >= 2
    assert data["pending_approval"] >= 1
    assert data["approved_cases"] >= 1
    
    # Calculate predicted revenue: (1000 * 0.8) + (2000 * 0.5) = 800 + 1000 = 1800
    assert data["predicted_recoverable_revenue"] >= 1800
