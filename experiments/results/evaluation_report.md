# ML Evaluation Report

## Model 
Name: logistic_regression
Version: 1.0.0

## Dataset
Total: 2000
Train: 1200
Validation: 300
Test: 500

## Threshold
Selected threshold: 0.5
Reason: Selected based on maximizing F1-score on the validation set.

## Evaluation (Test Set)
Precision: 0.9251
Recall: 0.9073
F1: 0.9161
ROC-AUC: 0.9642
PR-AUC: 0.9804
Brier score: 0.0753
False Positive Rate: 0.1230

## Business metrics (Test Set - Synthetic/Simulated)
Revenue at risk: 1251532000
Predicted recoverable revenue: 756376800
Revenue captured (True Positives): 701576000
False-positive intervention cost: 115000
Action efficiency: 0.9251

## Baseline Comparison
Baseline strategy: Classify all eligible failed payments as recoverable (Predict 1).
Baseline Precision: 0.6260 vs ML: 0.9251
Baseline Recall: 1.0000 vs ML: 0.9073
Baseline F1: 0.7700 vs ML: 0.9161
Baseline FPR: 1.0000 vs ML: 0.1230
Baseline Cost: 935000 vs ML: 115000
