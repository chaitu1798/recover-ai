from app.recovery.idempotency import get_existing_execution
from app.models.recovery_action import RecoveryActionModel
from app.models.action_result import ActionResult

import uuid
from app.models.policy import Policy
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from app.models.recovery_decision import RecoveryDecision

def test_idempotency_not_found(db):
    action, result = get_existing_execution(db, "non_existent_key")
    assert action is None
    assert result is None

def test_idempotency_found(db):
    merchant = Merchant(name="Test Merchant")
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    merchant_id = merchant.id
    payment = Payment(merchant_id=merchant_id, amount=1000, currency="INR", status="failed", attempt_number=1, method="card", razorpay_payment_id="mock_pay_123")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    case = RecoveryCase(payment_id=payment.id, status="open", amount_at_risk=1000, eligible=True)
    db.add(case)
    db.commit()
    db.refresh(case)
    
    decision = RecoveryDecision(recovery_case_id=case.id, recommended_action="RETRY", confidence=0.8, model_version="1.0")
    db.add(decision)
    db.commit()
    db.refresh(decision)

    action_model = RecoveryActionModel(
        recovery_case_id=case.id,
        decision_id=decision.id,
        action_type="RETRY",
        status="completed",
        idempotency_key="test_idem_key_123",
        attempt_number=1,
        approved_by_policy=True
    )
    db.add(action_model)
    db.commit()
    db.refresh(action_model)
    
    result_model = ActionResult(
        action_id=action_model.id,
        success=True,
        recovered_amount=1000,
        final_payment_status="captured",
        previous_payment_status="failed"
    )
    db.add(result_model)
    db.commit()
    
    action, result = get_existing_execution(db, "test_idem_key_123")
    assert action is not None
    assert action.idempotency_key == "test_idem_key_123"
    assert result is not None
    assert result.success is True

