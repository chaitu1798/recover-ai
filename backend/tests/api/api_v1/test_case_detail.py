import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.main import app
from app.database import get_db
from app.models import Merchant, Customer, Payment, RecoveryCase, RecoveryDecision, Policy, AuditLog
from app.models.enums import ApprovalStatus
from app.agent.recovery_agent import analyze_recovery_case

@pytest.fixture
def client(db: Session):
    def _get_db():
        yield db
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_case_detail_returns_authoritative_intelligence(db: Session, client):
    merchant = Merchant(name="Detail Test Merchant")
    db.add(merchant)
    db.flush()

    policy = Policy(
        merchant_id=merchant.id,
        policy_name="Test Policy",
        min_confidence=0.5,
        max_attempts=3,
        max_auto_action_amount=10000000,
        enabled=True,
        rules={"rule": "default"}
    )
    db.add(policy)
    db.flush()

    payment = Payment(
        id=uuid.uuid4(),
        merchant_id=merchant.id,
        razorpay_payment_id=f"pay_det_{uuid.uuid4().hex[:8]}",
        amount=800000,
        currency="INR",
        method="upi",
        status="failed",
        error_code="NETWORK_ERROR",
        attempt_number=1,
        failed_at=datetime.now(timezone.utc)
    )
    db.add(payment)
    db.flush()

    case = RecoveryCase(
        id=uuid.uuid4(),
        payment_id=payment.id,
        status="open",
        amount_at_risk=payment.amount,
        eligible=True,
        opened_at=datetime.now(timezone.utc)
    )
    db.add(case)
    db.flush()

    case_id_str = str(case.id)
    payment_id_str = str(payment.id)

    # Analyze case
    analyze_recovery_case(db, uuid.UUID(payment_id_str), uuid.UUID(case_id_str))

    response = client.get(f"/api/v1/recovery/cases/{case_id_str}")
    assert response.status_code == 200
    data = response.json()

    # Verify payment info
    assert data["payment"]["amount"] == 800000
    assert data["payment"]["currency"] == "INR"
    assert data["payment"]["error_code"] == "NETWORK_ERROR"

    # Verify AI analysis & case intelligence
    assert data["case"]["recovery_probability"] is not None
    assert 0.0 <= data["case"]["recovery_probability"] <= 1.0
    assert data["case"]["expected_recovery_value"] is not None
    assert isinstance(data["case"]["expected_recovery_value"], int)
    assert data["case"]["priority_level"] in ["HIGH", "MEDIUM", "LOW"]
    assert data["decision"]["recommended_action"] == "RETRY"
    assert data["decision"]["diagnosis"] == "TEMPORARY_FAILURE"
    assert data["decision"]["confidence"] is not None
    assert data["decision"]["strategy"] == "STRATEGY_OPTIMIZER"

    # Verify approval state
    assert data["case"]["status"] == "pending_approval"
    assert data["case"]["approval_status"] == ApprovalStatus.PENDING_APPROVAL.value

    # Verify audit logs
    assert len(data["audit_logs"]) >= 1

def test_case_detail_fallback_reasoning_consistency(db: Session, client):
    merchant = Merchant(name="Fallback Test Merchant")
    db.add(merchant)
    db.flush()

    payment = Payment(
        id=uuid.uuid4(),
        merchant_id=merchant.id,
        razorpay_payment_id=f"pay_fb_{uuid.uuid4().hex[:8]}",
        amount=500000,
        currency="INR",
        method="card",
        status="failed",
        error_code="UNKNOWN",
        attempt_number=1,
        failed_at=datetime.now(timezone.utc)
    )
    db.add(payment)
    db.flush()

    case = RecoveryCase(
        id=uuid.uuid4(),
        payment_id=payment.id,
        status="analyzed",
        amount_at_risk=payment.amount,
        eligible=True,
        opened_at=datetime.now(timezone.utc)
    )
    db.add(case)
    db.flush()

    # Create decision with reasoning containing intelligence values
    decision = RecoveryDecision(
        id=uuid.uuid4(),
        recovery_case_id=case.id,
        model_name="fallback_model",
        model_version="1.0.0",
        diagnosis="UNKNOWN",
        recommended_action="NO_ACTION",
        confidence=1.0,
        reasoning={
          "decision_source": "DETERMINISTIC_FALLBACK",
          "failure_category": "UNKNOWN",
          "recovery_probability": 0.75,
          "expected_recovery_value_minor": 375000,
          "priority_level": "HIGH",
          "policy_allowed": True
        }
    )
    db.add(decision)
    db.flush()

    case_id_str = str(case.id)

    response = client.get(f"/api/v1/recovery/cases/{case_id_str}")
    assert response.status_code == 200
    data = response.json()

    assert data["case"]["recovery_probability"] == 0.75
    assert data["case"]["expected_recovery_value"] == 375000
    assert data["case"]["priority_level"] == "HIGH"
    assert data["decision"]["recommended_action"] == "NO_ACTION"
    assert data["decision"]["diagnosis"] == "UNKNOWN"

def test_approval_and_execution_flow(db: Session, client):
    merchant = Merchant(name="Approval Test Merchant")
    db.add(merchant)
    db.flush()

    policy = Policy(
        merchant_id=merchant.id,
        policy_name="Test Policy",
        min_confidence=0.5,
        max_attempts=3,
        max_auto_action_amount=10000000,
        enabled=True,
        rules={"rule": "default"}
    )
    db.add(policy)
    db.flush()

    payment = Payment(
        id=uuid.uuid4(),
        merchant_id=merchant.id,
        razorpay_payment_id=f"pay_app_{uuid.uuid4().hex[:8]}",
        amount=100000,
        currency="INR",
        method="upi",
        status="failed",
        error_code="NETWORK_ERROR",
        attempt_number=1,
        failed_at=datetime.now(timezone.utc)
    )
    db.add(payment)
    db.flush()

    case = RecoveryCase(
        id=uuid.uuid4(),
        payment_id=payment.id,
        status="open",
        amount_at_risk=payment.amount,
        eligible=True,
        opened_at=datetime.now(timezone.utc)
    )
    db.add(case)
    db.flush()

    case_id_str = str(case.id)
    payment_id_str = str(payment.id)

    # 1. Analyze case -> pending_approval
    analyze_recovery_case(db, uuid.UUID(payment_id_str), uuid.UUID(case_id_str))
    
    # Query decision_id
    detail_pre = client.get(f"/api/v1/recovery/cases/{case_id_str}").json()
    assert "decision" in detail_pre
    decision_id_str = detail_pre["decision"]["id"]

    # 2. Approve case
    app_resp = client.post(f"/api/v1/recovery/{case_id_str}/approve", json={
        "approved_by": "operator_test",
        "reason": "Test approval"
    })
    assert app_resp.status_code == 200
    assert app_resp.json()["status"] == "success"

    # 3. Execute approved case (simulator in test mode)
    exec_resp_2 = client.post("/api/v1/recovery/execute", json={
        "recovery_case_id": case_id_str,
        "decision_id": decision_id_str,
        "idempotency_key": f"key_{uuid.uuid4().hex[:8]}"
    })
    assert exec_resp_2.status_code == 200
    assert exec_resp_2.json()["status"] in ["SUCCESS", "FAILED"]

    # 4. Check detail endpoint shows updated state and audit logs
    detail_resp = client.get(f"/api/v1/recovery/cases/{case_id_str}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["case"]["approval_status"] == ApprovalStatus.APPROVED.value
    assert detail_data["case"]["approved_by"] == "operator_test"
    assert len(detail_data["audit_logs"]) >= 2

def test_unapproved_execution_blocked(db: Session, client):
    merchant = Merchant(name="Unapproved Merchant")
    db.add(merchant)
    db.flush()

    policy = Policy(
        merchant_id=merchant.id,
        policy_name="Test Policy",
        min_confidence=0.5,
        max_attempts=3,
        max_auto_action_amount=10000000,
        enabled=True,
        rules={"rule": "default"}
    )
    db.add(policy)
    db.flush()

    payment = Payment(
        id=uuid.uuid4(),
        merchant_id=merchant.id,
        razorpay_payment_id=f"pay_unapp_{uuid.uuid4().hex[:8]}",
        amount=100000,
        currency="INR",
        method="upi",
        status="failed",
        error_code="NETWORK_ERROR",
        attempt_number=1,
        failed_at=datetime.now(timezone.utc)
    )
    db.add(payment)
    db.flush()

    case = RecoveryCase(
        id=uuid.uuid4(),
        payment_id=payment.id,
        status="open",
        amount_at_risk=payment.amount,
        eligible=True,
        opened_at=datetime.now(timezone.utc)
    )
    db.add(case)
    db.flush()

    case_id_str = str(case.id)
    payment_id_str = str(payment.id)

    analyze_recovery_case(db, uuid.UUID(payment_id_str), uuid.UUID(case_id_str))

    detail_pre = client.get(f"/api/v1/recovery/cases/{case_id_str}").json()
    decision_id_str = detail_pre["decision"]["id"]

    exec_resp = client.post("/api/v1/recovery/execute", json={
        "recovery_case_id": case_id_str,
        "decision_id": decision_id_str,
        "idempotency_key": f"key_{uuid.uuid4().hex[:8]}"
    })
    assert exec_resp.status_code in [400, 403]
