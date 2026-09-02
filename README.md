# RecoverAI v1.0.0

RecoverAI is an intelligent payment-recovery decision-support platform designed for the Razorpay AI Buildathon (Track 03). It transforms failed payments into simulated recovered revenue securely and intelligently.

> **CRITICAL SAFETY MODEL:**
> - **TEST MODE ONLY**: The system strictly enforces `RAZORPAY_MODE=test` at the execution boundary.
> - **No Real Financial Transactions**: Live execution fails safely.
> - **Human Approval Required**: AI is recommendation-only. It cannot execute payments.
> - **Predictions are NOT Revenue**: Expected Recovery Value is purely a statistical prediction, separate from actual recovered revenue.

## Project Overview & Problem Statement
Merchants can lose up to 15% of revenue to failed payments. Manual recovery is slow, subjective, and error-prone, while automated retry logic lacks contextual intelligence. RecoverAI solves this by utilizing Machine Learning (LightGBM) to predict recovery likelihood, and Generative AI to diagnose failure context and suggest deterministic recovery strategies.

## Features
- **Webhook Ingestion**: Securely verifies and ingests Razorpay webhooks (`payment.failed`, `payment.authorized`).
- **ML Probability**: Predicts the likelihood of recovery using a trained LightGBM model.
- **AI Recommendation**: Diagnoses failures and recommends recovery strategies (`PAYMENT_LINK`, `RETRY`, `NO_ACTION`).
- **Priority Engine**: Scores cases by Expected Value to prioritize merchant workflow.
- **Strategy Optimizer**: A rules-based engine optimizing execution strategy.
- **Policy Engine**: Validates decisions against core business and safety rules.
- **Human Approval**: Mandatory merchant dashboard for approving AI recommendations.
- **Execution Simulator**: Test-mode idempotency-safe execution environment.
- **Analytics & Experimentation**: Deterministic A/B testing and strategy analytics.

## Architecture & Technology Stack
- **Backend**: FastAPI (Python 3.11), SQLAlchemy, Alembic, Celery, Redis.
- **Frontend**: Next.js 14+ (App Router), TypeScript, TailwindCSS.
- **Database**: PostgreSQL (strict constraints, integer-based money fields).
- **ML**: LightGBM, scikit-learn.

## Quick Start (Docker Setup)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/chaitu1798/recover-ai.git
   cd recover-ai
   ```

2. **Environment Configuration:**
   Copy `.env.example` to `.env`. Ensure `RAZORPAY_MODE=test`. (No real secrets are required for the local demo).

3. **Start the Stack:**
   ```bash
   docker compose up -d --build
   ```

4. **Verify Health:**
   ```bash
   curl http://localhost:8000/api/v1/health
   curl http://localhost:8000/api/v1/ready
   ```

5. **Run the Demo Script:**
   Populates the database and triggers simulated webhook cases.
   ```bash
   docker compose exec backend python scripts/demo.py
   ```

6. **Open the Dashboard:**
   Navigate to `http://localhost:3000` to review and approve the cases.

## API Documentation
Once running, the interactive OpenAPI documentation is available at:
- `http://localhost:8000/docs`
- `http://localhost:8000/openapi.json`

## Testing
To run the full regression test suite (100% test pass rate required):
```bash
docker compose run -e PYTHONDONTWRITEBYTECODE=1 --rm backend pytest -v
```

## Troubleshooting
- **No data in dashboard**: Ensure `docker compose exec backend python scripts/demo.py` ran successfully.
- **Backend fails to start**: Check database logs (`docker compose logs postgres`) or run `docker compose exec backend alembic current` to verify migration state.
- **Build errors in frontend**: Run `npm run lint` and `npm run build` in the `frontend` directory.
