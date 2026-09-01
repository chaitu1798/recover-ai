import pytest
import uuid
import os
from app.recovery.executor import execute_recovery
from app.recovery.safety import UnsafeExecutionModeError
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from app.models.recovery_decision import RecoveryDecision
from app.models.policy import Policy
from app.models.recovery_action import RecoveryActionModel
from app.models.action_result import ActionResult

@pytest.fixture
def setup_test_data(db):
    merchant = Merchant(name="Test Merchant")
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    merchant_id = merchant.id
    
    policy = Policy(merchant_id=merchant_id, policy_name="Test Policy", min_confidence=0.5, max_attempts=3, enabled=True)
    db.add(policy)
    
    payment = Payment(
        merchant_id=merchant_id,
        amount=1000,
        currency="INR",
        status="failed",
        error_code="NETWORK_ERROR",
        attempt_number=1,
        method="card",
        razorpay_payment_id="mock_pay_123"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    case = RecoveryCase(
        payment_id=payment.id,
        status="open",
        amount_at_risk=payment.amount,
        eligible=True
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    decision = RecoveryDecision(
        recovery_case_id=case.id,
        recommended_action="RETRY",
        confidence=0.8,
        model_version="1.0"
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    
    return {
        "merchant_id": merchant_id,
        "payment": payment,
        "case": case,
        "decision": decision,
        "policy": policy
    }

def test_executor_successful(db, setup_test_data, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "test")
    
    case_id = setup_test_data["case"].id
    decision_id = setup_test_data["decision"].id
    idempotency_key = f"exec_test_{uuid.uuid4()}"
    
    result = execute_recovery(db, case_id, decision_id, idempotency_key)
    
    assert result["status"] in ["SUCCESS", "FAILED"] # Simulator might fail or succeed deterministically
    assert result["action"] == "RETRY"
    assert result["idempotency_key"] == idempotency_key
    assert result["idempotent_replay"] is False
    
    # Check db states
    db.expire_all()
    action = db.query(RecoveryActionModel).filter_by(idempotency_key=idempotency_key).first()
    assert action is not None
    
    action_result = db.query(ActionResult).filter_by(action_id=action.id).first()
    assert action_result is not None
    
def test_executor_idempotency_replay(db, setup_test_data, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "test")
    
    case_id = setup_test_data["case"].id
    decision_id = setup_test_data["decision"].id
    idempotency_key = f"idem_test_{uuid.uuid4()}"
    
    # First execution
    res1 = execute_recovery(db, case_id, decision_id, idempotency_key)
    assert res1["idempotent_replay"] is False
    
    # Second execution
    res2 = execute_recovery(db, case_id, decision_id, idempotency_key)
    assert res2["idempotent_replay"] is True
    
    # Check count is 1
    actions = db.query(RecoveryActionModel).filter_by(idempotency_key=idempotency_key).all()
    assert len(actions) == 1
    
def test_executor_safety_blocks(db, setup_test_data, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "live")
    
    with pytest.raises(UnsafeExecutionModeError):
        execute_recovery(
            db, 
            setup_test_data["case"].id, 
            setup_test_data["decision"].id, 
            "some_key"
        )
