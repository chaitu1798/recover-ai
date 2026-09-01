from sqlalchemy.orm import Session
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment
from app.models.action_result import ActionResult
from app.models.recovery_action import RecoveryActionModel
from app.recovery.state_machine import transition_to_recovered, transition_to_failed, transition_to_open

def process_outcome(
    db: Session,
    recovery_case: RecoveryCase,
    payment: Payment,
    action_model: RecoveryActionModel,
    simulation_result: dict
) -> ActionResult:
    """
    Translates simulation result into an ActionResult and updates RecoveryCase.
    """
    success = simulation_result.get("success", False)
    recovered_amount = simulation_result.get("recovered_amount", 0)
    provider_reference = simulation_result.get("provider_reference")
    failure_reason = simulation_result.get("failure_reason")

    action_result = ActionResult(
        action_id=action_model.id,
        success=success,
        razorpay_reference=provider_reference,
        previous_payment_status=payment.status,
        final_payment_status="captured" if (success and action_model.action_type == "RETRY") else payment.status,
        recovered_amount=recovered_amount,
        error_code=failure_reason if not success else None,
        error_message=failure_reason if not success else None,
        response_payload=simulation_result
    )
    
    db.add(action_result)

    # State transitions
    # OPEN -> EXECUTING (done in executor before simulation) -> RECOVERED/FAILED/OPEN
    
    if success and action_model.action_type == "RETRY" and recovered_amount > 0:
        transition_to_recovered(db, recovery_case)
        payment.status = "captured"
    elif not success and action_model.action_type == "RETRY":
        # Check attempts
        # We don't mark FAILED immediately unless max attempts, but the requirements just say EXECUTING -> FAILED or something.
        # Let's say it goes back to OPEN or FAILED. We'll leave it OPEN if we want to retry later, or FAILED if we are done.
        # But for this simulation, we'll mark FAILED if RETRY fails.
        transition_to_failed(db, recovery_case)
    else:
        # PAYMENT_LINK, REMINDER, NO_ACTION: case remains OPEN or we can mark it whatever the logic desires.
        # "NO_ACTION" might close it. Let's just set it to FAILED if no action, or keep it OPEN.
        if action_model.action_type == "NO_ACTION":
            transition_to_failed(db, recovery_case)
        else:
            # Action succeeded but money not recovered immediately (e.g. PAYMENT_LINK)
            transition_to_open(db, recovery_case)
            
    return action_result
