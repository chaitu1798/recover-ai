import os
import sys
import json

# Ensure backend can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ml.predict import predict_recovery

def main():
    # A sample payment features dictionary (simulating a failed payment)
    sample_features = {
        "amount": 150000,
        "currency": "INR",
        "payment_method": "UPI",
        "failure_reason": "NETWORK_ERROR",
        "attempt_number": 1,
        "previous_successes": 5,
        "previous_failures": 1,
        "customer_tenure_days": 365,
        "time_since_failure_minutes": 10,
        "historical_recovery_rate": 0.8
    }

    print("Running Prediction on Sample Payment Features:")
    print(json.dumps(sample_features, indent=2))
    print("-" * 40)
    
    try:
        prediction = predict_recovery(sample_features)
        print("RecoverAI Recovery Prediction")
        print(f"Probability: {prediction['recovery_probability']}")
        print(f"Threshold: {prediction['threshold']}")
        decision = "RECOVERABLE" if prediction['predicted_recoverable'] else "NO_ACTION"
        print(f"Decision: {decision}")
        print(f"Model: {prediction['model_name']}")
        print(f"Version: {prediction['model_version']}")
    except Exception as e:
        print(f"Prediction failed: {e}")

if __name__ == "__main__":
    main()
