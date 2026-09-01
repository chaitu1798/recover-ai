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
    monkeypatch.setattr(settings, "RAZORPAY_MODE", "invalid")
    with pytest.raises(UnsafeExecutionModeError):
        assert_test_mode()
