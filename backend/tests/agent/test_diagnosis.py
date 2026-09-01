import pytest
from app.agent.diagnosis import diagnose_failure

def test_diagnose_failure_temporary():
    assert diagnose_failure("BANK_TIMEOUT") == "TEMPORARY_FAILURE"
    assert diagnose_failure("NETWORK_ERROR") == "TEMPORARY_FAILURE"

def test_diagnose_failure_funds():
    assert diagnose_failure("INSUFFICIENT_FUNDS") == "FUNDS_PROBLEM"

def test_diagnose_failure_customer_action():
    assert diagnose_failure("PAYMENT_EXPIRED") == "CUSTOMER_ACTION_REQUIRED"

def test_diagnose_failure_payment_state():
    assert diagnose_failure("INVALID_PAYMENT_STATE") == "PAYMENT_STATE_PROBLEM"

def test_diagnose_failure_unknown():
    assert diagnose_failure("OTHER") == "UNKNOWN"
    assert diagnose_failure("SOME_RANDOM_ERROR") == "UNKNOWN"
    assert diagnose_failure(None) == "UNKNOWN"
