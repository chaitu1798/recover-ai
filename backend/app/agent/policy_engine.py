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
    """
    reasons = []
    violations = []
    
    # Base checks
    if not policy or not policy.enabled:
        violations.append("Policy is disabled or not found.")
        
    if not recovery_case.eligible:
        violations.append(f"Recovery case is not eligible: {recovery_case.eligibility_reason}")

    if recommended_action == "NO_ACTION":
        return {
            "allowed": True,
            "reasons": ["Action is NO_ACTION, always allowed if chosen by model."],
            "violations": violations
        }

    # Policy threshold checks
    if policy:
        if recovery_probability < float(policy.min_confidence):
            violations.append(f"Recovery probability {recovery_probability} below policy minimum {policy.min_confidence}.")
        else:
            reasons.append("Recovery probability meets policy threshold.")

        if policy.max_auto_action_amount is not None and payment.amount > policy.max_auto_action_amount:
            violations.append(f"Payment amount {payment.amount} exceeds policy maximum {policy.max_auto_action_amount}.")
        else:
            reasons.append("Payment amount within policy limits.")
            
        if payment.attempt_number > policy.max_attempts:
            violations.append(f"Payment attempts {payment.attempt_number} exceeds policy maximum {policy.max_attempts}.")
        else:
            reasons.append("Attempt count within policy limits.")
            
        # Optional rules from JSONB
        rules = policy.rules or {}
        
        allowed_methods = rules.get("allowed_methods")
        if allowed_methods is not None and payment.method not in allowed_methods:
            violations.append(f"Payment method {payment.method} not in allowed methods.")
            
        unsupported_failures = rules.get("unsupported_failures", [])
        if payment.error_code in unsupported_failures:
            violations.append(f"Failure reason {payment.error_code} is explicitly unsupported.")

    allowed = len(violations) == 0
    return {
        "allowed": allowed,
        "reasons": reasons,
        "violations": violations
    }
