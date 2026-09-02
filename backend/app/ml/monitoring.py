from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.recovery_case import RecoveryCase
from app.models.recovery_action import RecoveryActionModel

def get_ml_monitoring_metrics(db: Session) -> Dict[str, Any]:
    """
    Step 11 & 12: ML Monitoring & Prediction vs Actual
    """
    metrics = {
        "buckets": [],
        "overall_precision": None,
        "overall_recall": None,
        "overall_brier_score": None,
        "message": ""
    }
    
    # We only look at closed cases to compare prediction vs actual
    # Actual recovery = action with status 'success' related to the case
    
    # Fetch all closed cases
    cases = db.query(RecoveryCase).filter(RecoveryCase.status == 'closed').all()
    
    if len(cases) < 10: # Minimum data threshold
        metrics["message"] = "INSUFFICIENT_DATA"
        return metrics
        
    buckets = {
        "0-20%": {"count": 0, "sum_prob": 0.0, "successes": 0},
        "20-40%": {"count": 0, "sum_prob": 0.0, "successes": 0},
        "40-60%": {"count": 0, "sum_prob": 0.0, "successes": 0},
        "60-80%": {"count": 0, "sum_prob": 0.0, "successes": 0},
        "80-100%": {"count": 0, "sum_prob": 0.0, "successes": 0},
    }
    
    total_brier = 0.0
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    for case in cases:
        prob = float(case.recovery_probability or 0.0)
        
        # Check actual outcome
        # A case is a success if it has at least one successful action
        success = any(action.status == 'success' for action in case.actions)
        actual_val = 1.0 if success else 0.0
        
        # Brier score component
        total_brier += (prob - actual_val) ** 2
        
        # Confusion matrix stats (using 0.5 threshold)
        pred_positive = prob >= 0.5
        if pred_positive and success:
            true_positives += 1
        elif pred_positive and not success:
            false_positives += 1
        elif not pred_positive and success:
            false_negatives += 1
            
        # Buckets
        bucket_key = ""
        if prob < 0.2: bucket_key = "0-20%"
        elif prob < 0.4: bucket_key = "20-40%"
        elif prob < 0.6: bucket_key = "40-60%"
        elif prob < 0.8: bucket_key = "60-80%"
        else: bucket_key = "80-100%"
        
        buckets[bucket_key]["count"] += 1
        buckets[bucket_key]["sum_prob"] += prob
        if success:
            buckets[bucket_key]["successes"] += 1
            
    # Calculate bucket metrics
    for k, v in buckets.items():
        count = v["count"]
        avg_prob = (v["sum_prob"] / count) if count > 0 else 0.0
        actual_rate = (v["successes"] / count) if count > 0 else 0.0
        calibration_gap = avg_prob - actual_rate if count > 0 else 0.0
        
        metrics["buckets"].append({
            "bucket": k,
            "prediction_count": count,
            "average_predicted_probability": round(avg_prob, 4),
            "actual_recovery_rate": round(actual_rate, 4),
            "calibration_gap": round(calibration_gap, 4)
        })
        
    metrics["overall_brier_score"] = round(total_brier / len(cases), 4)
    if (true_positives + false_positives) > 0:
        metrics["overall_precision"] = round(true_positives / (true_positives + false_positives), 4)
    if (true_positives + false_negatives) > 0:
        metrics["overall_recall"] = round(true_positives / (true_positives + false_negatives), 4)
        
    return metrics
