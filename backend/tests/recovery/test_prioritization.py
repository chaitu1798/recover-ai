import pytest
from app.recovery.prioritization import calculate_priority

def test_priority_explanation_minor_units_conversion_regression():
    """
    Regression Test:
    Ensures expected recovery value in minor units (e.g. 19278 paise)
    is accurately formatted as ₹192.78 in the priority explanation,
    and never erroneously displayed as ₹1,927.80 (a 10x mismatch).
    """
    amount_at_risk = 45000  # ₹450.00 in minor units
    recovery_probability = 0.4284
    attempt_number = 3

    priority_score, priority_level, explanation = calculate_priority(
        recovery_probability=recovery_probability,
        amount_at_risk=amount_at_risk,
        attempt_number=attempt_number
    )

    # 45000 * 0.4284 = 19278 minor units
    expected_minor = int(amount_at_risk * recovery_probability)
    assert expected_minor == 19278

    # Must accurately state ₹192.78
    assert "₹192.78" in explanation
    assert "19278 minor units" in explanation

    # Must strictly NOT state 1927.80 or ₹1,927.80
    assert "1,927.80" not in explanation
    assert "1927.80" not in explanation
    assert "1927.8" not in explanation
    assert "₹1,927.80" not in explanation

    # Attempt multiplier for attempt 3 should be 0.6
    assert "0.6" in explanation
    assert priority_level == "MEDIUM"

def test_priority_levels_and_thresholds():
    """Verify priority score calculations and level thresholds."""
    # High Priority: score > 50000 and prob > 0.5
    score, level, exp = calculate_priority(0.9, 100000, 1)
    assert level == "HIGH"
    assert "₹900.00" in exp
    assert score == 90000.0

    # Medium Priority: score > 10000 and <= 50000
    score, level, exp = calculate_priority(0.4, 50000, 1)
    assert level == "MEDIUM"
    assert "₹200.00" in exp
    assert score == 20000.0

    # Low Priority: score <= 10000
    score, level, exp = calculate_priority(0.1, 20000, 1)
    assert level == "LOW"
    assert "₹20.00" in exp
    assert score == 2000.0
