import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.database import get_db
from app.models import PaymentEvent, Payment, RecoveryCase, AuditLog
from app.integrations.razorpay import verify_webhook_signature, SignatureVerificationError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    if not x_razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    raw_body = await request.body()

    try:
        verify_webhook_signature(raw_body, x_razorpay_signature)
    except SignatureVerificationError as e:
        logger.warning(f"Webhook signature verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Malformed JSON")

    event_id = payload.get("id")
    event_type = payload.get("event")

    if not event_id or not event_type:
        raise HTTPException(status_code=400, detail="Missing event ID or type")

    # We only care about payment events in Phase 3
    if not event_type.startswith("payment."):
        return {"status": "ignored", "reason": "unsupported_event"}

    # Extract payment data
    payload_payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_payment_id = payload_payment.get("id")
    
    if not razorpay_payment_id:
        raise HTTPException(status_code=400, detail="Missing payment ID")

    # Start transaction processing
    try:
        # Check idempotency via PaymentEvent unique constraint on razorpay_event_id
        existing_event = db.query(PaymentEvent).filter(PaymentEvent.razorpay_event_id == event_id).first()
        if existing_event:
            return {"status": "duplicate", "message": "Event already processed"}

        # Create PaymentEvent
        payment_event = PaymentEvent(
            event_type=event_type,
            razorpay_event_id=event_id,
            payload=payload,
            processing_status='processing'
        )
        db.add(payment_event)
        
        # Flush to catch IntegrityError early
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            return {"status": "duplicate", "message": "Event already processed"}

        # Update or create Payment
        payment = db.query(Payment).filter(Payment.razorpay_payment_id == razorpay_payment_id).first()
        
        # Map status
        status_map = {
            "payment.failed": "failed",
            "payment.captured": "captured",
            "payment.authorized": "authorized"
        }
        mapped_status = status_map.get(event_type)

        if payment:
            if mapped_status:
                payment.status = mapped_status
            if event_type == "payment.failed":
                payment.failed_at = datetime.now(timezone.utc)
                payment.error_code = payload_payment.get("error_code")
                payment.error_description = payload_payment.get("error_description")
            elif event_type == "payment.captured":
                payment.captured_at = datetime.now(timezone.utc)
            elif event_type == "payment.authorized":
                payment.authorized_at = datetime.now(timezone.utc)
        else:
            # We can't safely create the payment without merchant_id, so we just log and skip for now unless required.
            pass # In a real system, we'd need merchant resolution logic here.

        # Recovery Case for failed payments
        if event_type == "payment.failed" and payment:
            # Eligibility check (simplified for phase 3, assume all are eligible if not already recovered)
            existing_case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment.id).first()
            if not existing_case:
                recovery_case = RecoveryCase(
                    payment_id=payment.id,
                    status='open',
                    amount_at_risk=payment.amount,
                    recovery_probability=0.5,
                    priority_score=0.5,
                    eligible=True,
                    eligibility_reason="Payment failed webhook received"
                )
                db.add(recovery_case)

        # Update event status
        payment_event.processing_status = 'processed'
        payment_event.processed_at = datetime.now(timezone.utc)

        # Audit Log
        audit_log = AuditLog(
            action="webhook_processed",
            actor_type="system",
            entity_type="payment_events",
            entity_id=payment_event.id,
            after_state={"event_id": event_id, "event_type": event_type, "status": "success"}
        )
        db.add(audit_log)

        db.commit()
        return {"status": "success"}

    except Exception as e:
        db.rollback()
        # Log failure audit
        try:
            audit_log = AuditLog(
                action="webhook_failed",
                actor_type="system",
                entity_type="event",
                after_state={"event_id": event_id, "event_type": event_type, "error": str(e)}
            )
            db.add(audit_log)
            db.commit()
        except Exception:
            db.rollback()
            
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error")
