# RecoverAI Buildathon Demo Guide

This guide is designed for anyone presenting RecoverAI during a buildathon or demonstration. It guarantees a deterministic and polished showcase of the core capabilities.

## Prerequisites
- Docker and Docker Compose installed.
- No live financial credentials configured.
- (Optional) A local browser for the dashboard.

## Startup
To start the entire stack cleanly:
```bash
docker compose up -d --build
```

Verify backend health and readiness:
- **Health:** `curl http://localhost:8000/api/v1/health`
- **Readiness:** `curl http://localhost:8000/api/v1/ready`

## The Demo Sequence

Run the built-in deterministic demo script:
```bash
docker compose exec backend python scripts/demo.py
```

### What You Will See (The Flow)

1. **FAILED PAYMENT**: The script simulates incoming Razorpay `payment.failed` webhooks for various scenarios.
2. **WEBHOOK**: The webhook signature is verified, ensuring secure ingestion.
3. **RECOVERY CASE**: The payload creates a standard `RecoveryCase` in the database.
4. **ML PREDICTION**: The ML model predicts recovery probability.
5. **AI RECOMMENDATION**: The AI agent writes human-readable reasoning and diagnoses the failure (e.g., INSUFFICIENT_FUNDS).
6. **EXPECTED VALUE**: The case computes `amount * probability`.
7. **PRIORITY**: The priority engine classifies it as `HIGH`, `MEDIUM`, or `LOW`.
8. **STRATEGY**: The optimizer chooses a strategy like `PAYMENT_LINK` or `RETRY`.
9. **POLICY**: The policy engine blocks out-of-policy items (e.g., amounts > 10,000 are flagged).
10. **PENDING APPROVAL**: The case halts and awaits human intervention.

### Dashboard Walkthrough (http://localhost:3000)

Open the frontend dashboard.
- Show the **Recovery Overview** with cases ordered by Priority and Expected Value.
- Show the **Model Insights** displaying predictions and strategy distribution.
- Emphasize the clear distinction between **PREDICTED** and **ACTUAL** values.

### Action Demonstrations

- **Approval**: Click a `PENDING_APPROVAL` case, review the AI reasoning, and click **Approve**. The status transitions to `APPROVED` and the simulated recovery execution occurs safely in test-mode.
- **Rejection**: Reject a case and show that the backend simulator blocks execution.
- **Idempotency**: Run the demo script twice. It gracefully skips processing duplicate webhooks and assigns the same deterministic experiment grouping to cases.
- **Live-mode blocking**: The system strictly prevents any action if `RAZORPAY_MODE=live`. Real financial transactions are impossible.

## Safety Guarantees
- RecoverAI does not perform real financial transactions.
- Execution operates purely in `TEST MODE`.
- Human approval is mandatory. AI is strictly recommendation-only.
