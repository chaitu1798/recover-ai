# AI Recovery Agent (Phase 5)

## Overview
The AI Recovery Agent is a safe, **recommendation-only** system designed to diagnose failed payments and suggest the optimal recovery strategy. It strictly adheres to merchant policies and does not perform any automated financial executions.

## Architecture & Workflow
1. **Trigger**: A failed payment enters a `RecoveryCase`.
2. **Prediction**: The Phase 4 ML model predicts the recovery probability.
3. **Diagnosis**: Deterministic logic maps the raw error code to a `failure_category` (e.g., `TEMPORARY_FAILURE`).
4. **Policy Engine**: The system evaluates authoritative merchant constraints (e.g., amount limits, attempt limits, minimum probability thresholds).
5. **Recommendation**: An optional LLM can suggest a strategy based on the available evidence.
6. **Safety Validation**: The recommendation must be one of `RETRY`, `PAYMENT_LINK`, `REMINDER`, or `NO_ACTION`. The LLM cannot override the policy engine.
7. **Persistence**: The decision is saved to `RecoveryDecision` and logged via `AuditLog`.

## Economic Decision Logic
The expected recovery value is calculated internally in integer minor units:
`expected_recovery_value = recovery_probability * payment_amount_minor_units`

## Fallback Mechanism
If the LLM is unavailable, times out, or suggests an invalid/unsupported action, the agent safely falls back to a deterministic recommendation. If a policy violation occurs, the action is forcefully set to `NO_ACTION`.

## Idempotency
The API endpoint `/api/v1/recovery/analyze` guarantees idempotency. If an active decision already exists for a recovery case, it will simply be returned rather than duplicated.

## Limitations
- The LLM is strictly constrained and any prompt injection attempts to trigger financial actions are blocked by the Pydantic schema validation and deterministic safety boundaries.
- No Razorpay APIs are ever invoked by the Phase 5 Agent.
