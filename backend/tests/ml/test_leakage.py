import pandas as pd
import os
import tempfile
from app.ml.dataset import load_data

def test_no_target_leakage():
    # Create a temporary CSV with all leaky columns + valid features
    mock_data = pd.DataFrame([{
        "payment_id": "123",
        "customer_id": "abc",
        "amount": 1000,
        "currency": "INR",
        "payment_method": "UPI",
        "payment_status": "failed",
        "failure_reason": "NETWORK_ERROR",
        "attempt_number": 1,
        "previous_successes": 0,
        "previous_failures": 0,
        "customer_tenure_days": 10,
        "time_since_failure_minutes": 5,
        "historical_recovery_rate": 0.0,
        "recoverable_ground_truth": "TRUE",
        "expected_recovery_action": "RETRY",
        "simulated_recovery_outcome": "SUCCESS",
        "simulated_recovered_amount": 1000,
        "created_at": "2026-01-01T00:00:00"
    }])
    
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        mock_data.to_csv(f.name, index=False)
        temp_path = f.name
        
    try:
        X, y = load_data(temp_path)
        
        # Verify y contains target
        assert y is not None
        assert y.iloc[0] == 1
        
        # Verify X does not contain ANY leaky columns
        leaky_columns = [
            "recoverable_ground_truth",
            "expected_recovery_action",
            "simulated_recovery_outcome",
            "simulated_recovered_amount",
            "payment_id",
            "customer_id",
            "created_at",
            "payment_status"
        ]
        for col in leaky_columns:
            assert col not in X.columns, f"Leakage detected: {col} is in features!"
            
    finally:
        os.remove(temp_path)
