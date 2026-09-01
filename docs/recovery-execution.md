# Phase 6: Recovery Execution Simulator

## Overview
Phase 6 implements a Recovery Execution Simulator and Evaluation engine for RecoverAI. It acts as a safety barrier between the AI Recovery Agent (Phase 5) and live financial transactions. This simulator evaluates bounded recovery recommendations (e.g., `RETRY`, `PAYMENT_LINK`, `REMINDER`) and produces realistic outcomes based on deterministic rules and historical data, without performing actual payment captures or refunds.

## Key Components

1. **Simulator Engine (`app/recovery/simulator.py`)**
   - **Purpose**: Generates deterministic outcomes for recovery recommendations.
   - **Mechanism**: Utilizes a seeded random number generator (seed=42) or deterministic hashing of the `razorpay_payment_id` to compute a simulated outcome.
   - **Outcomes**: Returns a simulated result including status (`SUCCESS`, `FAILURE`, etc.), simulated recovered amount, and transaction ID.

2. **Recovery Executor (`app/recovery/executor.py`)**
   - **Purpose**: Orchestrates the evaluation pipeline.
   - **Workflow**:
     1. Validates `RAZORPAY_MODE=test`. Hard blocks execution otherwise.
     2. Verifies eligibility rules via `EligibilityEngine`.
     3. Checks idempotency using `IdempotencyHandler` to prevent duplicate actions.
     4. Invokes the `Simulator` instead of real Razorpay API.
     5. Processes outcomes via `OutcomeProcessor`.

3. **Evaluation Script (`scripts/evaluate_recovery.py`)**
   - **Purpose**: Evaluates the recovery pipeline over a batch of test data.
   - **Mechanism**: Mocks merchant, policy, payment, and recovery cases, and processes them through the `RecoveryAgent` and `RecoveryExecutor`.
   - **Output**: Generates `recovery_metrics.json` and `recovery_evaluation.md` located in `experiments/results/`.

## Idempotency
Idempotency is strictly enforced to prevent double-execution:
- An `idempotency_key` is generated (e.g., `eval_{case.id}`).
- The `IdempotencyHandler` checks for existing `RecoveryAction` records.
- If a duplicate request is detected, the executor returns the previous result without invoking the simulator, flagging `idempotent_replay=True`.

## Safety Enforcement
- **No Live Operations**: Any attempt to execute without `RAZORPAY_MODE=test` raises a `RuntimeError`.
- **Policy Compliance**: Evaluates all decisions against merchant policy thresholds. Policy constraints always take precedence over AI recommendations.
