from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from app.models.recovery_decision import RecoveryDecision
from app.models.policy import Policy
from app.agent.policy_engine import evaluate_policy
from typing import Tuple, List

def check_eligibility(
    payment: Payment,
    recovery_case: RecoveryCase,
    decision: RecoveryDecision,
    policy: Policy
) -> Tuple[bool, List[str]]:
    """
    Checks if a recovery decision is eligible for execution.
    Returns (is_eligible, list_of_reasons).
    """
    reasons = []

    if not payment:
        reasons.append("Payment does not exist.")
    elif payment.status != "failed":
        reasons.append(f"Payment status is {payment.status}, expected 'failed'.")

    if not recovery_case:
        reasons.append("RecoveryCase does not exist.")
    elif not recovery_case.eligible:
        reasons.append("RecoveryCase is marked as ineligible.")
    elif recovery_case.status not in ["open", "approved", "executing", "EXECUTING"]:
        reasons.append(f"RecoveryCase status is {recovery_case.status}, expected 'open', 'approved' or 'executing'.")

    if not decision:
        reasons.append("RecoveryDecision does not exist.")

    if decision and decision.recommended_action not in ["RETRY", "PAYMENT_LINK", "REMINDER", "NO_ACTION"]:
        reasons.append(f"Unsupported action: {decision.recommended_action}")

    if not policy:
        reasons.append("Policy does not exist.")

    if not reasons and decision.recommended_action != "NO_ACTION":
        # Check against policy
        policy_eval = evaluate_policy(
            policy=policy,
            payment=payment,
            recovery_case=recovery_case,
            recovery_probability=float(decision.confidence),
            recommended_action=decision.recommended_action
        )
        if not policy_eval["allowed"]:
            reasons.extend(policy_eval["violations"])

    return len(reasons) == 0, reasons
