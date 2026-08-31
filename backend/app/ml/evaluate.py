import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    brier_score_loss, roc_curve, precision_recall_curve
)
from .dataset import load_data, TARGET_COLUMN
from .model_registry import load_model_metadata, save_model_metadata

INTERVENTION_COST_MINOR_UNITS = 5000  # ₹50 assumption

def evaluate_model(data_dir: str, output_dir: str, models_dir: str):
    """
    Evaluates the model on validation (for thresholding) and test data.
    Generates reports and charts.
    """
    model_path = os.path.join(models_dir, "recovery_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    model = joblib.load(model_path)
    metadata = load_model_metadata()
    
    val_path = os.path.join(data_dir, "evaluation", "validation.csv")
    test_path = os.path.join(data_dir, "evaluation", "test.csv")
    
    X_val, y_val = load_data(val_path)
    X_test, y_test = load_data(test_path)
    
    val_df_full = pd.read_csv(val_path)
    test_df_full = pd.read_csv(test_path)
    
    # 1. Evaluate thresholds on Validation Set
    val_probs = model.predict_proba(X_val)[:, 1]
    
    thresholds_to_test = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90]
    best_threshold = 0.50
    best_f1 = -1
    
    for t in thresholds_to_test:
        preds = (val_probs >= t).astype(int)
        f1 = f1_score(y_val, preds, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = t
            
    print(f"Selected threshold {best_threshold} based on validation F1-score {best_f1:.4f}")
    
    # Update metadata with selected threshold
    metadata["threshold"] = best_threshold
    save_model_metadata(metadata)
    
    # 2. Final Evaluation on Test Set
    test_probs = model.predict_proba(X_test)[:, 1]
    test_preds = (test_probs >= best_threshold).astype(int)
    
    # Classification Metrics
    precision = precision_score(y_test, test_preds, zero_division=0)
    recall = recall_score(y_test, test_preds, zero_division=0)
    f1 = f1_score(y_test, test_preds, zero_division=0)
    acc = accuracy_score(y_test, test_preds)
    roc_auc = roc_auc_score(y_test, test_probs)
    pr_auc = average_precision_score(y_test, test_probs)
    brier = brier_score_loss(y_test, test_probs)
    
    cm = confusion_matrix(y_test, test_preds)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    # Business Metrics (Test Set)
    revenue_at_risk = int(test_df_full["amount"].sum())
    
    # Recoverable revenue (Ground Truth)
    recoverable_revenue = int(test_df_full.loc[test_df_full[TARGET_COLUMN] == 'TRUE', "amount"].sum())
    
    # Predicted Recoverable Revenue (TP + FP amounts)
    predicted_positive_indices = (test_preds == 1)
    predicted_recoverable_revenue = int(test_df_full.loc[predicted_positive_indices, "amount"].sum())
    
    # True positive captured revenue
    true_positive_indices = (test_preds == 1) & (y_test == 1)
    revenue_captured = int(test_df_full.loc[true_positive_indices, "amount"].sum())
    
    false_positive_cost = fp * INTERVENTION_COST_MINOR_UNITS
    action_efficiency = tp / (tp + fp) if (tp + fp) > 0 else 0
    
    # Baseline comparison (Predict all eligible failed payments as recoverable = All 1s)
    baseline_preds = np.ones_like(y_test)
    b_precision = precision_score(y_test, baseline_preds, zero_division=0)
    b_recall = recall_score(y_test, baseline_preds, zero_division=0)
    b_f1 = f1_score(y_test, baseline_preds, zero_division=0)
    b_cm = confusion_matrix(y_test, baseline_preds)
    b_tn, b_fp, b_fn, b_tp = b_cm.ravel()
    b_fpr = b_fp / (b_fp + b_tn) if (b_fp + b_tn) > 0 else 0
    b_fp_cost = b_fp * INTERVENTION_COST_MINOR_UNITS
    b_revenue_captured = int(test_df_full.loc[y_test == 1, "amount"].sum()) # Captured all since we predict all 1
    
    # 3. Save Results
    os.makedirs(output_dir, exist_ok=True)
    
    metrics = {
        "classification": {
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
            "accuracy": round(float(acc), 4),
            "roc_auc": round(float(roc_auc), 4),
            "pr_auc": round(float(pr_auc), 4),
            "brier_score": round(float(brier), 4),
            "fpr": round(float(fpr), 4)
        },
        "confusion_matrix": {
            "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn)
        },
        "business": {
            "revenue_at_risk": int(revenue_at_risk),
            "recoverable_revenue_gt": int(recoverable_revenue),
            "predicted_recoverable_revenue": int(predicted_recoverable_revenue),
            "revenue_captured": int(revenue_captured),
            "false_positive_cost": int(false_positive_cost),
            "action_efficiency": round(float(action_efficiency), 4)
        },
        "baseline": {
            "precision": round(float(b_precision), 4),
            "recall": round(float(b_recall), 4),
            "f1": round(float(b_f1), 4),
            "fpr": round(float(b_fpr), 4),
            "revenue_captured": int(b_revenue_captured),
            "false_positive_cost": int(b_fp_cost)
        },
        "threshold": float(best_threshold)
    }
    
    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)
        
    # Generate charts
    # 1. Confusion Matrix
    plt.figure()
    plt.matshow(cm, cmap='Blues', alpha=0.8)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(x=j, y=i, s=cm[i, j], va='center', ha='center')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"))
    plt.close()
    
    # 2. ROC Curve
    fpr_curve, tpr_curve, _ = roc_curve(y_test, test_probs)
    plt.figure()
    plt.plot(fpr_curve, tpr_curve, label=f"ROC Curve (AUC = {roc_auc:.2f})")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.savefig(os.path.join(output_dir, "roc_curve.png"))
    plt.close()
    
    # 3. PR Curve
    prec_curve, rec_curve, _ = precision_recall_curve(y_test, test_probs)
    plt.figure()
    plt.plot(rec_curve, prec_curve, label=f"PR Curve (AUC = {pr_auc:.2f})")
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.savefig(os.path.join(output_dir, "precision_recall_curve.png"))
    plt.close()
    
    # Generate Markdown Report
    report = f"""# ML Evaluation Report

## Model 
Name: {metadata.get("model_name")}
Version: {metadata.get("model_version")}

## Dataset
Total: {metadata.get("train_records", 0) + metadata.get("validation_records", 0) + metadata.get("test_records", 0)}
Train: {metadata.get("train_records")}
Validation: {metadata.get("validation_records")}
Test: {metadata.get("test_records")}

## Threshold
Selected threshold: {best_threshold}
Reason: Selected based on maximizing F1-score on the validation set.

## Evaluation (Test Set)
Precision: {precision:.4f}
Recall: {recall:.4f}
F1: {f1:.4f}
ROC-AUC: {roc_auc:.4f}
PR-AUC: {pr_auc:.4f}
Brier score: {brier:.4f}
False Positive Rate: {fpr:.4f}

## Business metrics (Test Set - Synthetic/Simulated)
Revenue at risk: {revenue_at_risk}
Predicted recoverable revenue: {predicted_recoverable_revenue}
Revenue captured (True Positives): {revenue_captured}
False-positive intervention cost: {false_positive_cost}
Action efficiency: {action_efficiency:.4f}

## Baseline Comparison
Baseline strategy: Classify all eligible failed payments as recoverable (Predict 1).
Baseline Precision: {b_precision:.4f} vs ML: {precision:.4f}
Baseline Recall: {b_recall:.4f} vs ML: {recall:.4f}
Baseline F1: {b_f1:.4f} vs ML: {f1:.4f}
Baseline FPR: {b_fpr:.4f} vs ML: {fpr:.4f}
Baseline Cost: {b_fp_cost} vs ML: {false_positive_cost}
"""
    with open(os.path.join(output_dir, "evaluation_report.md"), "w") as f:
        f.write(report)
        
    print(f"Evaluation complete. Artifacts saved to {output_dir}")
