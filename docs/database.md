# RecoverAI Database Schema & Architecture

This document describes the database foundation of RecoverAI (Phase 2).

## Architecture

* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.x
* **Migrations:** Alembic

## Schema

### Tables
* **merchants**: Base entity.
* **customers**: Linked to merchants.
* **orders**: E-commerce orders linked to customers and merchants.
* **payments**: Payment attempts linked to orders.
* **payment_events**: Raw webhook payloads linked to payments.
* **recovery_cases**: Revenue recovery state machine linked to payments.
* **recovery_decisions**: ML decisions for a case.
* **recovery_actions**: Execution step linked to a decision.
* **action_results**: Outcomes of actions.
* **policies**: Rules for merchants.
* **audit_logs**: Observability.
* **experiments** / **experiment_results**: A/B testing frameworks.
* **notifications**: Async communications.

### Relationships
Standard star/snowflake relationships with `merchants` at the center, branching into `customers` -> `orders` -> `payments` -> `recovery_cases` -> `recovery_actions`.

### Constraints
* UUID primary keys globally.
* `BigInteger` for all money representations (e.g. ₹49.99 = 4999 paise). Floating point values are never used for money calculations or storage.
* `CheckConstraints` strictly enforce no negative amounts.
* Enums strictly enforce acceptable statuses (e.g. `RecoveryAction` explicitly permits only `RETRY`, `PAYMENT_LINK`, `REMINDER`, `ESCALATE`, `NO_ACTION`).

## Synthetic Data Generation

For initial development and ML training, `scripts/generate_data.py` generates 2,000 deterministic synthetic transactions representing failed payments.
The dataset is split strictly into:
- 1,200 Train
- 300 Validation
- 500 Test

A fixed seed (`SEED = 42`) is used for complete reproducibility.

### Ground Truth and Noise Methodology
The synthetic dataset assigns deterministic recovery probability based on a mixture of signals (e.g. `BANK_TIMEOUT` is highly favorable, whereas `PAYMENT_EXPIRED` is highly unfavorable). To prevent simplistic ML mappings, controlled random noise is added to the recovery probability before determining the absolute ground truth. The ground truth determines the exact action that would optimally resolve the failure.

## Leakage Prevention

### Split Strategy
To prevent ML leakage (where a customer's payment behavior from the test set influences the training set), a customer-aware split is used.

### Customer Overlap Analysis
Customers are assigned strictly to Train, Validation, or Test sets. The records inherit their parent customer's split assignment. Verification ensures zero train/test or validation/test overlap.

## Scripts & Operations

### Generating Data
```bash
python scripts/generate_data.py
python scripts/validate_dataset.py
```
*Output:* `data/synthetic/payments.csv` and split datasets in `data/evaluation/`.

### Migrations
Alembic is set up for migrations.
```bash
alembic upgrade head
```

### Idempotency (Seeding & Import)
The following scripts are designed to be run safely multiple times without creating duplicates:
* **Seed Behavior**: Checks if Demo Merchant and default Policy exist before creating.
* **Import Behavior**: Uses `payment_id` idempotency. It checks if a payment already exists before attempting to create related records (orders, payments, cases). No `DROP`, `TRUNCATE`, or `DELETE ALL` is used during import.
```bash
python scripts/seed_database.py
python scripts/import_synthetic_data.py
```

### Known Limitations
At present, the local PostgreSQL Docker container is unavailable (blocked by host Docker Engine missing or daemon down). Migrations and database writes cannot execute locally until an active PostgreSQL endpoint is bound to `DATABASE_URL`. PostgreSQL execution is BLOCKED.
