import pytest
from app.ml.predict import predict_recovery

# Note: this test requires a trained model to exist. We will mock the load_model if needed,
# but for our full e2e test pipeline, training runs before predictions.
def test_prediction_output():
    sample = {
        "amount": 1000,
        "currency": "INR",
        "payment_method": "UPI",
        "failure_reason": "NETWORK_ERROR",
        "attempt_number": 1,
        "previous_successes": 0,
        "previous_failures": 0,
        "customer_tenure_days": 10,
        "time_since_failure_minutes": 5,
        "historical_recovery_rate": 0.0
    }
    
    try:
        result = predict_recovery(sample)
    except FileNotFoundError:
        pytest.skip("Model not yet trained, skipping prediction test.")
        
    assert "recovery_probability" in result
    assert "predicted_recoverable" in result
    assert "model_name" in result
    assert "model_version" in result
    
    prob = result["recovery_probability"]
    assert 0.0 <= prob <= 1.0
    assert isinstance(result["predicted_recoverable"], bool)

def test_prediction_leakage_rejection():
    # Attempting to predict with a leaky column should throw ValueError
    sample = {
        "amount": 1000,
        "recoverable_ground_truth": "TRUE" # LEAKAGE!
    }
    
    try:
        from app.ml.predict import predict_recovery
        with pytest.raises(ValueError, match="contain leaky columns"):
            predict_recovery(sample)
    except FileNotFoundError:
        pytest.skip("Model not yet trained, skipping.")
