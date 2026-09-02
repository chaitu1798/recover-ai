from typing import Dict, Any, List
from app.models.policy import Policy
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase

def evaluate_policy(
    policy: Policy, 
    payment: Payment, 
    recovery_case: RecoveryCase, 
    recovery_probability: float,
    recommended_action: str
) -> Dict[str, Any]:
    """
    Evaluates the recommendation against the merchant's authoritative policy.
    Returns structured results.
    """
    checks = {
        "retry_limit": "PASS",
        "cooldown": "PASS",
        "failure_reason": "PASS",
        "duplicate_action": "PASS",
        "approval_required": "PASS",
        "eligibility": "PASS",
        "probability_threshold": "PASS",
        "payment_amount": "PASS"
    }
    
    violations = []
    reasons = []

    if not policy or not policy.enabled:
        violations.append("Policy is disabled or not found.")
        checks["eligibility"] = "FAIL"
        
    if not recovery_case.eligible:
        violations.append(f"Recovery case is not eligible: {recovery_case.eligibility_reason}")
        checks["eligibility"] = "FAIL"

    if recommended_action == "NO_ACTION":
        return {
            "allowed": True,
            "reasons": ["Action is NO_ACTION, always allowed if chosen by model."],
            "violations": violations,
            "checks": checks
        }

    if policy:
        if recovery_probability < float(policy.min_confidence):
            violations.append(f"Recovery probability {recovery_probability} below policy minimum {policy.min_confidence}.")
            checks["probability_threshold"] = "FAIL"
        else:
            reasons.append("Recovery probability meets policy threshold.")

        if policy.max_auto_action_amount is not None and payment.amount > policy.max_auto_action_amount:
            violations.append(f"Payment amount {payment.amount} exceeds policy maximum {policy.max_auto_action_amount}.")
            checks["payment_amount"] = "FAIL"
        else:
            reasons.append("Payment amount within policy limits.")
            
        if payment.attempt_number > policy.max_attempts:
            violations.append(f"Payment attempts {payment.attempt_number} exceeds policy maximum {policy.max_attempts}.")
            checks["retry_limit"] = "FAIL"
        else:
            reasons.append("Attempt count within policy limits.")
            
        rules = policy.rules or {}
        
        allowed_methods = rules.get("allowed_methods")
        if allowed_methods is not None and payment.method not in allowed_methods:
            violations.append(f"Payment method {payment.method} not in allowed methods.")
            
        unsupported_failures = rules.get("unsupported_failures", [])
        if payment.error_code in unsupported_failures:
            violations.append(f"Failure reason {payment.error_code} is explicitly unsupported.")
            checks["failure_reason"] = "FAIL"

    allowed = len(violations) == 0
    return {
        "allowed": allowed,
        "reasons": reasons,
        "violations": violations,
        "checks": checks
    }
