from typing import Dict, Any, Tuple, List

def select_strategy(
    recovery_probability: float,
    failure_reason: str,
    attempt_number: int,
    customer_history_success_rate: float
) -> Tuple[str, float, List[str], str]:
    """
    Deterministic Strategy Optimizer.
    Never executes, just recommends.
    """
    reason_codes = []
    
    if attempt_number >= 3:
        reason_codes.append("MULTIPLE_FAILED_ATTEMPTS")
        return "NO_ACTION", 1.0, reason_codes, "Max attempts reached, no action recommended."
        
    if recovery_probability < 0.2:
        reason_codes.append("LOW_RECOVERY_PROBABILITY")
        return "NO_ACTION", 1.0, reason_codes, "Recovery probability is too low."
        
    if failure_reason in ["TEMPORARY_FAILURE", "NETWORK_ERROR", "TIMEOUT"]:
        reason_codes.append("RETRY_ELIGIBLE")
        if recovery_probability > 0.7:
            reason_codes.append("HIGH_RECOVERY_PROBABILITY")
            return "RETRY", 0.9, reason_codes, "High probability temporary failure, direct retry."
        else:
            return "RETRY", 0.7, reason_codes, "Temporary failure, retry recommended."
            
    if failure_reason in ["CUSTOMER_ACTION_REQUIRED", "AUTHENTICATION_FAILED"]:
        reason_codes.append("PAYMENT_LINK_PREFERRED")
        return "PAYMENT_LINK", 0.85, reason_codes, "Requires customer input, send payment link."
        
    if failure_reason in ["INSUFFICIENT_FUNDS"]:
        reason_codes.append("FUNDS_PROBLEM")
        if customer_history_success_rate > 0.5:
            reason_codes.append("CUSTOMER_HISTORY_SUPPORTS_RECOVERY")
            return "REMINDER", 0.8, reason_codes, "Good customer history, send reminder to fund account."
        else:
            return "PAYMENT_LINK", 0.7, reason_codes, "Provide alternative payment method via link."
            
    # Default fallback
    reason_codes.append("DEFAULT_STRATEGY")
    return "PAYMENT_LINK", 0.6, reason_codes, "Default recommendation."
