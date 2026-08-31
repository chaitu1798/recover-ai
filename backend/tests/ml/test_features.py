import pandas as pd
from app.ml.features import build_preprocessor

def test_feature_extraction():
    preprocessor = build_preprocessor()
    
    # Mock data with valid features
    data = pd.DataFrame([{
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
    }])
    
    # Preprocessor should transform the data without error
    transformed = preprocessor.fit_transform(data)
    
    # Basic check to ensure it returns a matrix of numerical values
    assert transformed.shape[0] == 1
    assert transformed.shape[1] > 0
