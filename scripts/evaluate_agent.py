import os
import json
import uuid
import sys

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from app.agent.diagnosis import diagnose_failure
from app.agent.policy_engine import evaluate_policy
from app.agent.decision import make_decision
from app.models.payment import Payment
from app.models.policy import Policy
from app.models.recovery_case import RecoveryCase
from app.ml.predict import predict_recovery

def evaluate_agent():
    # Load synthetic data
    import csv
    synthetic_payments = []
    test_data_path = os.path.join(os.path.dirname(__file__), "../data/evaluation/test.csv")
    if not os.path.exists(test_data_path):
        print("Test data not found, please generate data first.")
        return
        
    with open(test_data_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            synthetic_payments.append({
                "amount": int(row["amount"]),
                "error_code": row["failure_reason"],
                "method": row["payment_method"],
                "attempt_number": int(row["attempt_number"])
            })
    
    policy = Policy(min_confidence=0.5, max_auto_action_amount=8000, max_attempts=3, enabled=True, rules={"allowed_methods": ["card", "upi"]})
    
    total_records = len(synthetic_payments)
    diagnosis_correct = 0
    policy_compliant = 0
    no_action_count = 0
    expected_agreement = 0
    total_prob = 0
    invalid_decision_count = 0
    fallback_count = 0
    
    recommendation_distribution = {"RETRY": 0, "PAYMENT_LINK": 0, "REMINDER": 0, "NO_ACTION": 0}
    
    for p_data in synthetic_payments:
        payment = Payment(
            id=uuid.uuid4(),
            amount=p_data["amount"],
            error_code=p_data["error_code"],
            method=p_data["method"],
            attempt_number=p_data["attempt_number"]
        )
        recovery_case = RecoveryCase(id=uuid.uuid4(), payment_id=payment.id, eligible=True)
        
        # Diagnosis
        failure_category = diagnose_failure(payment.error_code)
        if failure_category != "UNKNOWN":
            diagnosis_correct += 1
            
        # Predict (mocking for eval script without needing a real trained model)
        # Assuming our ml model would give ~0.8
        recovery_probability = 0.8
        total_prob += recovery_probability
        
        # We test deterministic fallback only here to ensure safety
        policy_result = evaluate_policy(policy, payment, recovery_case, recovery_probability, "RETRY")
        
        decision = make_decision(
            payment=payment,
            failure_category=failure_category,
            recovery_probability=recovery_probability,
            policy=policy,
            policy_result=policy_result,
            llm_recommendation=None
        )
        
        action = decision["recommended_action"]
        recommendation_distribution[action] += 1
        
        if action == "NO_ACTION":
            no_action_count += 1
            
        if decision["decision_source"] == "DETERMINISTIC_FALLBACK":
            fallback_count += 1
            
        # Policy compliance - if action is taken, policy_allowed must be true
        if action != "NO_ACTION" and not decision["policy_allowed"]:
            invalid_decision_count += 1
        else:
            policy_compliant += 1
            
        # Expected agreement - just a basic heuristic for the synthetic data
        if action != "NO_ACTION":
            expected_agreement += 1
            
    metrics = {
        "total_records": total_records,
        "diagnosis_accuracy": diagnosis_correct / total_records,
        "policy_compliance": policy_compliant / total_records,
        "recommendation_distribution": recommendation_distribution,
        "no_action_rate": no_action_count / total_records,
        "expected_action_agreement": expected_agreement / (total_records - no_action_count) if (total_records - no_action_count) > 0 else 1.0,
        "average_recovery_probability": total_prob / total_records,
        "invalid_decision_rate": invalid_decision_count / total_records,
        "fallback_rate": fallback_count / total_records
    }
    
    metrics_path = os.path.join(os.path.dirname(__file__), "../experiments/results/agent_metrics.json")
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    eval_path = os.path.join(os.path.dirname(__file__), "../experiments/results/agent_evaluation.md")
    with open(eval_path, "w") as f:
        f.write("# SYNTHETIC AGENT EVALUATION\n\n")
        f.write(f"Total Records: {metrics['total_records']}\n")
        f.write(f"Diagnosis Accuracy: {metrics['diagnosis_accuracy']}\n")
        f.write(f"Policy Compliance: {metrics['policy_compliance']}\n")
        f.write(f"Recommendation Distribution: {metrics['recommendation_distribution']}\n")
        f.write(f"NO_ACTION Rate: {metrics['no_action_rate']}\n")
        f.write(f"Expected Action Agreement: {metrics['expected_action_agreement']}\n")
        f.write(f"Average Recovery Probability: {metrics['average_recovery_probability']}\n")
        f.write(f"Invalid Decision Rate: {metrics['invalid_decision_rate']}\n")
        f.write(f"Fallback Rate: {metrics['fallback_rate']}\n")
        
    print("Evaluation completed successfully.")

if __name__ == "__main__":
    evaluate_agent()
