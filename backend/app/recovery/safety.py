from app.config import settings

class UnsafeExecutionModeError(Exception):
    """Exception raised when execution mode is not safely configured for testing/simulation."""
    pass

def assert_test_mode():
    """
    Asserts that the system is running in test mode.
    Raises UnsafeExecutionModeError if RAZORPAY_MODE is not exactly 'test'.
    """
    mode = getattr(settings, "RAZORPAY_MODE", None)
    if mode != "test":
        raise UnsafeExecutionModeError(f"Execution is hard-blocked. RAZORPAY_MODE must be 'test', got '{mode}'")

