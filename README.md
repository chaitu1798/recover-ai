# RecoverAI

RecoverAI is an AI-powered revenue recovery platform for the Razorpay AI Buildathon (Track 03).

## Phases
- **Phase 1**: Database schema, models, and core repository setup.
- **Phase 2**: Core backend service with FastAPI, PostgreSQL, and basic models.
- **Phase 3**: Razorpay Webhook Integration (Payment Failure & Success flows).
- **Phase 4**: Recovery Intelligence & ML Evaluation pipeline (Probability scoring, evaluation).
- **Phase 5**: AI Recovery Agent
  - **RECOMMENDATION ONLY**: No real financial operations are performed. The agent safely evaluates policies and bounded strategies without making Razorpay API calls.

## Phase 2: Database & Data Foundation
- **Database Schema**: Fully implemented via 14 SQLAlchemy models mapping `03_Database_Schema.sql`. Constraints ensure no floating-point money values and enforce rigid enum boundaries on ML actions.
- **Migrations**: Alembic environment configured.
- **Synthetic Data**: Script (`scripts/generate_data.py`) produces 2,000 deterministic records simulating recovery cases with a ground-truth probability distribution mapped to real-world heuristics (e.g. `BANK_TIMEOUT` is highly recoverable, whereas `PAYMENT_EXPIRED` is not). Noise is included to prevent simplistic ML mappings.
- **Split Strategy**: A customer-aware splitting algorithm guarantees zero data leakage between Train (1200), Validation (300), and Test (500) sets.
- **Idempotency**: Seed and import scripts can be run multiple times safely.

### Commands
Generate data:
```bash
python scripts/generate_data.py
python scripts/validate_dataset.py
```

Seed Database (when PostgreSQL is online):
```bash
alembic upgrade head
python scripts/seed_database.py
python scripts/import_synthetic_data.py
```

### Limitations
Local Docker environment is missing a Docker daemon, rendering native PostgreSQL bindings blocked. Migrations and seed scripts rely on the presence of a database running on `DATABASE_URL`.
