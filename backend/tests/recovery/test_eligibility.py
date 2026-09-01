from app.recovery.eligibility import check_eligibility
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from app.models.recovery_decision import RecoveryDecision
from app.models.policy import Policy

def test_eligibility_valid():
    payment = Payment(status="failed", amount=1000, attempt_number=1, method="card")
    case = RecoveryCase(status="open", eligible=True)
    decision = RecoveryDecision(recommended_action="RETRY", confidence=0.8)
    policy = Policy(min_confidence=0.5, max_attempts=3, enabled=True, max_auto_action_amount=5000)
    
    is_eligible, reasons = check_eligibility(payment, case, decision, policy)
    assert is_eligible is True
    assert len(reasons) == 0
    
def test_eligibility_unsupported_action():
    payment = Payment(status="failed", amount=1000, attempt_number=1, method="card")
    case = RecoveryCase(status="open", eligible=True)
    decision = RecoveryDecision(recommended_action="EXECUTE_PAYMENT", confidence=0.8)
    policy = Policy(min_confidence=0.5, max_attempts=3, enabled=True)
    
    is_eligible, reasons = check_eligibility(payment, case, decision, policy)
    assert is_eligible is False
    assert any("Unsupported action" in r for r in reasons)

def test_eligibility_policy_violations():
    payment = Payment(status="failed", amount=10000, attempt_number=4, method="card")
    case = RecoveryCase(status="open", eligible=True)
    decision = RecoveryDecision(recommended_action="RETRY", confidence=0.2)
    policy = Policy(min_confidence=0.5, max_attempts=3, enabled=True, max_auto_action_amount=5000)
    
    is_eligible, reasons = check_eligibility(payment, case, decision, policy)
    assert is_eligible is False
    assert any("exceeds policy maximum" in r for r in reasons) # amount
    assert any("exceeds policy maximum" in r for r in reasons) # attempts
    assert any("below policy minimum" in r for r in reasons) # confidence
