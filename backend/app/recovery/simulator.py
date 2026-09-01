import random

SEED = 42

def simulate_execution(
    action: str,
    amount: int,
    recovery_probability: float,
    failure_reason: str,
    attempt_number: int,
    payment_method: str
) -> dict:
    """
    Deterministically simulates the execution of a recovery action.
    """
    if action == "NO_ACTION":
        return {
            "success": False,
            "action": action,
            "recovered_amount": 0,
            "provider_reference": f"sim_no_action_{random.randint(100000, 999999)}",
            "failure_reason": "NO_ACTION_TAKEN"
        }

    # Use a deterministic seed based on payment context so the same context always yields same result
    # We mix SEED with attributes to ensure determinism for a specific payment context
    state_str = f"{SEED}_{amount}_{recovery_probability}_{failure_reason}_{attempt_number}_{payment_method}_{action}"
    state_hash = hash(state_str)
    random.seed(state_hash)

    simulated_prob = float(recovery_probability)

    # Adjust simulated probability based on rules
    if action == "RETRY":
        if failure_reason in ["BANK_TIMEOUT", "NETWORK_ERROR"]:
            simulated_prob += 0.2
        elif failure_reason == "INSUFFICIENT_FUNDS":
            simulated_prob -= 0.3
            
        if attempt_number > 2:
            simulated_prob -= 0.15
            
    elif action == "PAYMENT_LINK":
        # Link generation is generally successful, but actual payment might not be.
        # Action result represents the ACTION success (generating link).
        return {
            "success": True,
            "action": action,
            "recovered_amount": 0, # Not immediately recovered
            "provider_reference": f"sim_link_{random.randint(100000, 999999)}",
            "failure_reason": None
        }
        
    elif action == "REMINDER":
        return {
            "success": True,
            "action": action,
            "recovered_amount": 0,
            "provider_reference": f"sim_reminder_{random.randint(100000, 999999)}",
            "failure_reason": None
        }

    # Determine success using the seeded RNG
    success = random.random() < simulated_prob

    if success:
        return {
            "success": True,
            "action": action,
            "recovered_amount": amount,
            "provider_reference": f"sim_{action.lower()}_{random.randint(100000, 999999)}",
            "failure_reason": None
        }
    else:
        return {
            "success": False,
            "action": action,
            "recovered_amount": 0,
            "provider_reference": f"sim_{action.lower()}_{random.randint(100000, 999999)}",
            "failure_reason": f"SIMULATED_{action}_FAILED"
        }
