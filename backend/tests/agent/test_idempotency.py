import pytest
import uuid
from app.agent.recovery_agent import analyze_recovery_case
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from app.models.policy import Policy
from app.models.merchant import Merchant

def test_idempotency(db):
    # Setup test data
    merchant = Merchant(name="Test Merchant Idemp")
    db.add(merchant)
    db.commit()
    
    policy = Policy(merchant_id=merchant.id, policy_name="Test Policy", min_confidence=0.1, enabled=True)
    db.add(policy)
    db.commit()
    
    payment = Payment(
        merchant_id=merchant.id,
        amount=500000,
        currency="INR",
        status="failed",
        error_code="NETWORK_ERROR",
        razorpay_payment_id="pay_test123"
    )
    db.add(payment)
    db.commit()
    
    case = RecoveryCase(
        payment_id=payment.id,
        amount_at_risk=payment.amount,
        status="open"
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    # Run agent first time
    result1 = analyze_recovery_case(db, payment.id, case.id)
    assert result1.recommended_action == "RETRY" # based on deterministic fallback for NETWORK_ERROR with high enough probability
    
    # Run agent second time
    result2 = analyze_recovery_case(db, payment.id, case.id)
    
    # Verify idempotency
    assert result1.recommended_action == result2.recommended_action
    assert result1.agent_confidence == result2.agent_confidence
    assert result1.recovery_case_id == result2.recovery_case_id
