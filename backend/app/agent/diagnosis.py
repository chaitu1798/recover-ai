def diagnose_failure(failure_reason: str) -> str:
    """
    Deterministically maps a raw failure reason to a normalized failure category.
    """
    mapping = {
        "BANK_TIMEOUT": "TEMPORARY_FAILURE",
        "NETWORK_ERROR": "TEMPORARY_FAILURE",
        "INSUFFICIENT_FUNDS": "FUNDS_PROBLEM",
        "PAYMENT_EXPIRED": "CUSTOMER_ACTION_REQUIRED",
        "INVALID_PAYMENT_STATE": "PAYMENT_STATE_PROBLEM"
    }
    
    # Return UNKNOWN if the failure reason is not in the mapping, or if it is "OTHER"
    return mapping.get(failure_reason, "UNKNOWN")
