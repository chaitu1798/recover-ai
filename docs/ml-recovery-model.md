# Recovery Intelligence ML Model (Phase 4)

## Problem Definition
The objective is to predict the probability that a failed payment is recoverable before taking any action. This allows the system to prioritize interventions (such as sending a payment link, retrying, or sending a reminder) efficiently and avoid wasting resources on non-recoverable payments.

## Dataset
- **Total records:** 2000 synthetic payment failure records.
- **Train split:** 1200 records (used for fitting preprocessor and model)
- **Validation split:** 300 records (used for evaluating models and thresholds)
- **Test split:** 500 records (strictly held out for final evaluation)

## Target
The target variable is `recoverable_ground_truth` (TRUE / FALSE), representing whether the failed payment is ultimately recoverable if an optimal action is taken.

## Feature List
Features engineered before prediction:
- **Numerical:** `amount`, `attempt_number`, `previous_successes`, `previous_failures`, `customer_tenure_days`, `time_since_failure_minutes`, `historical_recovery_rate`
- **Categorical:** `currency`, `payment_method`, `failure_reason`

### Excluded Features (Leakage Prevention)
To strictly prevent target leakage, the following variables were excluded from the model's feature set:
- `recoverable_ground_truth`
- `expected_recovery_action`
- `simulated_recovery_outcome`
- `simulated_recovered_amount`
- `created_at`, `payment_id`, `customer_id`
- `payment_status` (Excluded because it is a constant value of 'failed' across the population of failed payments, lacking predictive variance).

## Model Choice & Preprocessing
- **Baseline Model:** Logistic Regression (`class_weight=None`).
- **Preprocessing:** 
    - Numerical features are imputed with the median and scaled using `StandardScaler`.
    - Categorical features are imputed with 'missing' and encoded using `OneHotEncoder`.
    - Preprocessing pipelines are fit *strictly* on the training set to prevent leakage.

## Threshold Selection
The threshold was selected dynamically by testing `[0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90]` on the **validation set**. 
The optimal threshold chosen based on maximizing F1-score is **0.50**.

## Calibration
No extensive calibration techniques were required beyond Logistic Regression's native probability outputs, which returned a well-calibrated Brier score of 0.0753.

## Business Metrics
Evaluated on the synthetic test set using a synthetic assumption of ₹50 (`5000` minor units) cost per intervention:
- **Revenue at Risk:** 1251532000 minor units
- **Predicted Recoverable Revenue:** 756376800 minor units
- **False-positive intervention cost:** 115000 minor units
- **Action efficiency:** 92.51%

## Baseline Comparison
- **Baseline approach:** Classify all eligible failed payments as recoverable (Predict 1).
- **Baseline Precision:** 0.6260 vs **ML Precision:** 0.9251
- **Baseline Recall:** 1.0000 vs **ML Recall:** 0.9073
- **Baseline F1:** 0.7700 vs **ML F1:** 0.9161
- **Baseline False Positive Cost:** 935000 vs **ML Cost:** 115000

## Limitations
- **Synthetic dataset:** The dataset is synthetically generated and may not reflect real-world distributions.
- **Simulated recovery outcomes:** Ground truth and simulated outcomes are based on heuristic logic.
- **No production financial claim:** These models are not acting on live customer data or causing actual money movement.
- **Limited historical features:** Customer behavior history is heavily abstracted.
- **No real intervention feedback:** The model cannot learn from actual user behavior post-intervention.
- **No live recovery execution:** The Phase 4 model does not execute any recovery API calls.
- **Intervention cost:** The ₹50 intervention cost is an evaluation assumption and not a Razorpay-defined metric.

## Reproducibility
The pipeline is deterministic (`random_state=42`) and reproduces exact metrics when run on the exact same dataset across train/eval/test splits.
