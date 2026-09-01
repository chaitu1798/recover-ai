import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment
from app.models.enums import ApprovalStatus
from app.models.recovery_decision import RecoveryDecision

from app.database import get_db

client = TestClient(app)

def test_approve_case(db: Session, sample_payment: Payment):
    app.dependency_overrides[get_db] = lambda: db

    # Setup test data
    case = RecoveryCase(
        payment_id=sample_payment.id, 
        amount_at_risk=1000,
        status="pending_approval",
        approval_status=ApprovalStatus.PENDING_APPROVAL.value
    )
    db.add(case)
    db.commit()

    decision = RecoveryDecision(
        recovery_case_id=case.id,
        model_name="test_model",
        model_version="v1",
        diagnosis="TEST",
        recommended_action="RETRY",
        confidence=0.9,
        reasoning={}
    )
    db.add(decision)
    db.commit()

    response = client.post(
        f"/api/v1/recovery/{case.id}/approve",
        json={"approved_by": "test_operator", "reason": "Looks good"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    db.refresh(case)
    assert case.status == "approved"
    assert case.approval_status == ApprovalStatus.APPROVED.value
    assert case.approved_by == "test_operator"

def test_reject_case(db: Session, sample_payment: Payment):
    app.dependency_overrides[get_db] = lambda: db
    case = RecoveryCase(
        payment_id=sample_payment.id, 
        amount_at_risk=1000,
        status="pending_approval",
        approval_status=ApprovalStatus.PENDING_APPROVAL.value
    )
    db.add(case)
    db.commit()

    response = client.post(
        f"/api/v1/recovery/{case.id}/reject",
        json={"rejected_by": "test_operator", "reason": "Not right now"}
    )
    
    assert response.status_code == 200
    
    db.refresh(case)
    assert case.status == "rejected"
    assert case.approval_status == ApprovalStatus.REJECTED.value
    assert case.rejected_by == "test_operator"
    assert case.rejection_reason == "Not right now"

def test_approve_already_approved(db: Session, sample_payment: Payment):
    app.dependency_overrides[get_db] = lambda: db
    case = RecoveryCase(
        payment_id=sample_payment.id, 
        amount_at_risk=1000,
        status="approved",
        approval_status=ApprovalStatus.APPROVED.value
    )
    db.add(case)
    db.commit()

    response = client.post(
        f"/api/v1/recovery/{case.id}/approve",
        json={"approved_by": "test_operator", "reason": "Looks good"}
    )
    
    # Should be idempotent
    assert response.status_code == 200
    assert response.json()["message"] == "Already approved"

def test_approve_rejected_case(db: Session, sample_payment: Payment):
    app.dependency_overrides[get_db] = lambda: db
    case = RecoveryCase(
        payment_id=sample_payment.id, 
        amount_at_risk=1000,
        status="rejected",
        approval_status=ApprovalStatus.REJECTED.value
    )
    db.add(case)
    db.commit()

    response = client.post(
        f"/api/v1/recovery/{case.id}/approve",
        json={"approved_by": "test_operator", "reason": "Looks good"}
    )
    
    assert response.status_code == 409
