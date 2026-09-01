import pytest
from app.recovery.safety import assert_test_mode, UnsafeExecutionModeError
from app.config import settings

def test_test_mode_allowed(monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "test")
    assert_test_mode() # Should not raise

def test_live_mode_blocked(monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "live")
    with pytest.raises(UnsafeExecutionModeError):
        assert_test_mode()
        
def test_production_mode_blocked(monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "production")
    with pytest.raises(UnsafeExecutionModeError):
        assert_test_mode()

def test_missing_mode_blocked(monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_MODE", None)
    with pytest.raises(UnsafeExecutionModeError):
        assert_test_mode()

def test_invalid_mode_blocked(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "invalid_mode")
    with pytest.raises(UnsafeExecutionModeError, match="must be 'test'"):
        assert_test_mode()

def test_live_key_blocked(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "test")
    monkeypatch.setattr(settings, "RAZORPAY_KEY_ID", "rzp_live_abc123")
    with pytest.raises(UnsafeExecutionModeError, match="Live Razorpay key detected"):
        assert_test_mode()
