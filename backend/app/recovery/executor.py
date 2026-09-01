import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.recovery.safety import assert_test_mode
from app.recovery.eligibility import check_eligibility
from app.recovery.idempotency import get_existing_execution
from app.recovery.simulator import simulate_execution
from app.recovery.outcome import process_outcome
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment
from app.models.recovery_decision import RecoveryDecision
from app.models.policy import Policy
from app.models.recovery_action import RecoveryActionModel
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

def execute_recovery(db: Session, case_id: str, decision_id: str, idempotency_key: str):
    """
    Executes a recovery decision deterministically in simulation mode.
    """
    # 1. Validate test mode
    assert_test_mode()

    try:
        # Start transaction (implicitly managed by session, but we will lock rows)
        
        # 2, 3, 4. Load models with FOR UPDATE to lock them during execution
        recovery_case = db.query(RecoveryCase).with_for_update().filter(RecoveryCase.id == case_id).first()
        if not recovery_case:
            raise ValueError("RecoveryCase not found.")
            
        payment = db.query(Payment).with_for_update().filter(Payment.id == recovery_case.payment_id).first()
        if not payment:
            raise ValueError("Payment not found.")
            
        decision = db.query(RecoveryDecision).filter(RecoveryDecision.id == decision_id).first()
        if not decision:
            raise ValueError("RecoveryDecision not found.")
            
        policy = db.query(Policy).filter(Policy.merchant_id == payment.merchant_id).first()
        
        # 7. Check idempotency first before eligibility (since previous execution might have mutated state)
        existing_action, existing_result = get_existing_execution(db, idempotency_key)
        if existing_action and existing_result:
            return {
                "recovery_case_id": str(case_id),
                "action": existing_action.action_type,
                "status": "SUCCESS" if existing_result.success else "FAILED",
                "recovered_amount": existing_result.recovered_amount,
                "currency": payment.currency,
                "idempotency_key": idempotency_key,
                "provider_reference": existing_result.razorpay_reference,
                "attempt_number": existing_action.attempt_number,
                "idempotent_replay": True
            }
            
        # 5, 6. Validate policy and action
        is_eligible, reasons = check_eligibility(payment, recovery_case, decision, policy)
        if not is_eligible:
            raise ValueError(f"Not eligible for execution: {', '.join(reasons)}")
            


        # 9. Transition case to EXECUTING
        recovery_case.status = "EXECUTING"
        db.flush()

        # 10. Run deterministic simulator
        sim_result = simulate_execution(
            action=decision.recommended_action,
            amount=payment.amount,
            recovery_probability=float(decision.confidence),
            failure_reason=payment.error_code or "UNKNOWN",
            attempt_number=payment.attempt_number,
            payment_method=payment.method or "UNKNOWN"
        )
        
        # 11. Create RecoveryAction
        action_model = RecoveryActionModel(
            recovery_case_id=recovery_case.id,
            decision_id=decision.id,
            action_type=decision.recommended_action,
            status="completed" if sim_result["success"] else "failed",
            idempotency_key=idempotency_key,
            attempt_number=payment.attempt_number,
            approved_by_policy=True
        )
        db.add(action_model)
        db.flush() # To get action_model.id
        
        if decision.recommended_action == "RETRY":
            payment.attempt_number += 1

        # 12, 13. Create ActionResult & Update RecoveryCase
        action_result = process_outcome(db, recovery_case, payment, action_model, sim_result)
        db.flush()

        # 14. Create AuditLog
        audit_log = AuditLog(
            merchant_id=payment.merchant_id,
            entity_type="RecoveryCase",
            entity_id=recovery_case.id,
            actor_type="system",
            action="execute_recovery",
            before_state={"status": "open", "attempt_number": payment.attempt_number - (1 if decision.recommended_action == "RETRY" else 0)},
            after_state={
                "status": recovery_case.status, 
                "attempt_number": payment.attempt_number,
                "recovered_amount": action_result.recovered_amount
            },
            reason="Simulated execution",
            correlation_id=idempotency_key
        )
        db.add(audit_log)
        
        # 15. Commit atomically
        db.commit()

        # 16. Return structured result
        return {
            "recovery_case_id": str(case_id),
            "action": action_model.action_type,
            "status": "SUCCESS" if action_result.success else "FAILED",
            "recovered_amount": action_result.recovered_amount,
            "currency": payment.currency,
            "idempotency_key": idempotency_key,
            "provider_reference": action_result.razorpay_reference,
            "attempt_number": action_model.attempt_number,
            "idempotent_replay": False
        }

    except Exception as e:
        db.rollback()
        raise e
