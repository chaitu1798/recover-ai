# Razorpay Test Mode Integration

## Architecture
This document details Phase 3 of the RecoverAI architecture, enabling ingestion of Razorpay Webhooks. 
The system receives test mode webhooks, verifies their cryptographic signatures securely, prevents processing identical webhooks via database-level constraints (`PaymentEvent.razorpay_event_id`), upserts the corresponding payment, and instantiates a `RecoveryCase` for eligible failed payments.

## Test Mode Configuration
Ensure your `.env` contains test credentials only:
```env
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxx
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
```
Never use production credentials during this phase.

## Webhook Endpoint
The endpoint is available at `POST /api/v1/webhooks/razorpay`.
It requires the `X-Razorpay-Signature` header for all requests. The signature is matched against `hmac(webhook_body, secret)`.

## Supported Events
- `payment.failed`: Evaluated for recovery eligibility. Marks `Payment` as failed. Creates `RecoveryCase`.
- `payment.captured`: Marks `Payment` as captured.
- `payment.authorized`: Marks `Payment` as authorized.
All other events are ignored safely.

## Database Transaction & Idempotency
- Uses `BEGIN` and SQLAlchemy session handling.
- Tries inserting `PaymentEvent`.
- If an `IntegrityError` arises (due to unique `razorpay_event_id`), it rolls back the transaction and returns a safe "duplicate" response.
- Creates `AuditLog` of successes and failures securely (without saving the secrets).

## Recovery Case Eligibility
A `RecoveryCase` is only generated for `payment.failed`. During Phase 3, this is mocked as simply creating a `RecoveryCase` using default policy assumptions to prove out the DB schema constraint.

## Local Testing
Use the local test script:
```bash
python scripts/send_razorpay_webhook.py backend/tests/fixtures/razorpay/payment_failed.json --secret test_secret
```
