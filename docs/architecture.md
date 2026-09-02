# RecoverAI Architecture

RecoverAI is an intelligent payment-recovery decision-support platform. The architecture is designed to securely capture failed payments, evaluate them using machine learning and AI, and orchestrate manual human approval before any test-mode recovery action is taken.

## System Overview

1. **Webhook Ingestion**: Razorpay webhooks for `payment.failed` and `payment.authorized` events are ingested.
2. **Machine Learning**: A pre-trained LightGBM model predicts the probability of successful recovery.
3. **AI Recommendation**: An LLM agent generates human-readable reasoning and categorizes the failure reason.
4. **Strategy Optimization**: A rule-based engine selects a recovery strategy (e.g., `PAYMENT_LINK`, `RETRY`, `NO_ACTION`).
5. **Prioritization**: Cases are scored based on `Expected Value * Probability` and assigned priority bands.
6. **Policy Engine**: Central safety checks validate actions, amounts, and eligibility.
7. **Human Approval**: Mandatory human intervention. Recovery requires manual state transition to `APPROVED`.
8. **Test-Mode Execution**: The system acts as a simulator; live financial transactions are strictly blocked.
9. **Analytics & Monitoring**: Track strategy performance, expected vs. actual values, and ML drift.

## Backend Architecture

- **Framework**: FastAPI (Python 3.11).
- **Database**: PostgreSQL (SQLAlchemy ORM + Alembic Migrations).
- **Caching & Background Tasks**: Redis + Celery/ARQ (or lightweight async).
- **Validation**: Pydantic schemas.
- **Safety**: `RAZORPAY_MODE=test` environment boundaries enforced at API and Execution layers.

## Frontend Architecture

- **Framework**: Next.js 14+ (App Router, React Server Components).
- **Language**: TypeScript.
- **Styling**: TailwindCSS.
- **Data Fetching**: Native `fetch` with component-level state via hooks.

## Key Data Models

- `PaymentEvent`: Raw webhook payloads.
- `RecoveryCase`: Core entity tracking the recovery lifecycle, assigned priorities, expected values, and ML probabilities.
- `RecoveryDecision`: AI reasoning, chosen strategy, and AB experimentation group.
- `RecoveryAction`: The simulated recovery attempt and final outcome.

## Safety & Security Model

- **TEST MODE ONLY**: Real execution is disabled. The system simulates outcomes.
- **Approval Mandatory**: AI is restricted to recommendation. Humans approve execution.
- **Idempotency**: Webhook signatures are verified; repeated events are rejected or deduplicated safely.
- **Integer Monetary Values**: All financial calculations use integer minor units (e.g., paise, cents) to prevent floating-point precision errors.
