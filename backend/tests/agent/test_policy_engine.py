import pytest
from app.agent.policy_engine import evaluate_policy
from app.models.policy import Policy
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase

def test_evaluate_policy_allowed():
    policy = Policy(min_confidence=0.8, max_auto_action_amount=5000, max_attempts=3, enabled=True)
    payment = Payment(amount=1000, attempt_number=1, method="card", error_code="BANK_TIMEOUT")
    recovery_case = RecoveryCase(eligible=True)
    
    result = evaluate_policy(policy, payment, recovery_case, 0.9, "RETRY")
    assert result["allowed"] is True

def test_evaluate_policy_denied_low_probability():
    policy = Policy(min_confidence=0.8, max_auto_action_amount=5000, max_attempts=3, enabled=True)
    payment = Payment(amount=1000, attempt_number=1, method="card", error_code="BANK_TIMEOUT")
    recovery_case = RecoveryCase(eligible=True)
    
    result = evaluate_policy(policy, payment, recovery_case, 0.7, "RETRY")
    assert result["allowed"] is False
    assert any("below policy minimum" in v for v in result["violations"])

def test_evaluate_policy_denied_high_amount():
    policy = Policy(min_confidence=0.8, max_auto_action_amount=5000, max_attempts=3, enabled=True)
    payment = Payment(amount=10000, attempt_number=1, method="card", error_code="BANK_TIMEOUT")
    recovery_case = RecoveryCase(eligible=True)
    
    result = evaluate_policy(policy, payment, recovery_case, 0.9, "RETRY")
    assert result["allowed"] is False
    assert any("exceeds policy maximum" in v for v in result["violations"])

def test_evaluate_policy_denied_max_attempts():
    policy = Policy(min_confidence=0.8, max_auto_action_amount=5000, max_attempts=3, enabled=True)
    payment = Payment(amount=1000, attempt_number=4, method="card", error_code="BANK_TIMEOUT")
    recovery_case = RecoveryCase(eligible=True)
    
    result = evaluate_policy(policy, payment, recovery_case, 0.9, "RETRY")
    assert result["allowed"] is False

def test_evaluate_policy_denied_unsupported_method():
    policy = Policy(min_confidence=0.8, max_auto_action_amount=5000, max_attempts=3, enabled=True, rules={"allowed_methods": ["card"]})
    payment = Payment(amount=1000, attempt_number=1, method="upi", error_code="BANK_TIMEOUT")
    recovery_case = RecoveryCase(eligible=True)
    
    result = evaluate_policy(policy, payment, recovery_case, 0.9, "RETRY")
    assert result["allowed"] is False
    assert any("not in allowed methods" in v for v in result["violations"])

def test_evaluate_policy_denied_ineligible_case():
    policy = Policy(min_confidence=0.8, max_attempts=3, enabled=True)
    payment = Payment(amount=1000, attempt_number=1, method="card", error_code="BANK_TIMEOUT")
    recovery_case = RecoveryCase(eligible=False, eligibility_reason="Too old")
    
    result = evaluate_policy(policy, payment, recovery_case, 0.9, "RETRY")
    assert result["allowed"] is False
