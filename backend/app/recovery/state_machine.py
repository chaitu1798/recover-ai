from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.recovery_case import RecoveryCase
from app.models.enums import ApprovalStatus
from app.models.audit_log import AuditLog

class InvalidTransitionError(Exception):
    pass

def _create_audit(
    db: Session,
    recovery_case: RecoveryCase,
    action: str,
    before_status: str,
    after_status: str,
    actor_type: str = "system",
    actor: str = "system",
    reason: Optional[str] = None,
    decision_id: Optional[str] = None
):
    audit_log = AuditLog(
        merchant_id=recovery_case.payment.merchant_id if recovery_case.payment else None,
        entity_type="RecoveryCase",
        entity_id=recovery_case.id,
        actor_type=actor_type,
        action=action,
        before_state={"status": before_status},
        after_state={"status": after_status},
        reason=reason,
        correlation_id=decision_id
    )
    db.add(audit_log)

def transition_to_analyzed(db: Session, recovery_case: RecoveryCase, decision_id: str):
    if recovery_case.status != "open":
        raise InvalidTransitionError(f"Cannot transition to ANALYZED from {recovery_case.status}")
    before_status = recovery_case.status
    recovery_case.status = "analyzed"
    _create_audit(db, recovery_case, "AI_DECISION_CREATED", before_status, recovery_case.status, actor_type="ai", actor="recovery_agent", decision_id=decision_id)

def transition_to_pending_approval(db: Session, recovery_case: RecoveryCase, decision_id: str):
    if recovery_case.status not in ["open", "analyzed"]:
        raise InvalidTransitionError(f"Cannot transition to PENDING_APPROVAL from {recovery_case.status}")
    before_status = recovery_case.status
    recovery_case.status = "pending_approval"
    recovery_case.approval_status = ApprovalStatus.PENDING_APPROVAL.value
    _create_audit(db, recovery_case, "AI_DECISION_CREATED", before_status, recovery_case.status, actor_type="ai", actor="recovery_agent", decision_id=decision_id)

def transition_to_approved(db: Session, recovery_case: RecoveryCase, approved_by: str, reason: str):
    if recovery_case.status != "pending_approval":
        raise InvalidTransitionError(f"Cannot transition to APPROVED from {recovery_case.status}")
    if recovery_case.approval_status != ApprovalStatus.PENDING_APPROVAL.value:
        raise InvalidTransitionError(f"Cannot approve when approval_status is {recovery_case.approval_status}")
    
    before_status = recovery_case.status
    recovery_case.status = "approved"
    recovery_case.approval_status = ApprovalStatus.APPROVED.value
    recovery_case.approved_by = approved_by
    recovery_case.approved_at = datetime.now(timezone.utc)
    _create_audit(db, recovery_case, "APPROVAL_GRANTED", before_status, recovery_case.status, actor_type="human", actor=approved_by, reason=reason)

def transition_to_rejected(db: Session, recovery_case: RecoveryCase, rejected_by: str, reason: str):
    if recovery_case.status != "pending_approval":
        raise InvalidTransitionError(f"Cannot transition to REJECTED from {recovery_case.status}")
    if recovery_case.approval_status != ApprovalStatus.PENDING_APPROVAL.value:
        raise InvalidTransitionError(f"Cannot reject when approval_status is {recovery_case.approval_status}")
    
    before_status = recovery_case.status
    recovery_case.status = "rejected"
    recovery_case.approval_status = ApprovalStatus.REJECTED.value
    recovery_case.rejected_by = rejected_by
    recovery_case.rejected_at = datetime.now(timezone.utc)
    recovery_case.rejection_reason = reason
    _create_audit(db, recovery_case, "APPROVAL_REJECTED", before_status, recovery_case.status, actor_type="human", actor=rejected_by, reason=reason)

def transition_to_open(db: Session, recovery_case: RecoveryCase):
    """
    Transition a case from EXECUTING to OPEN.
    Used when an action completes but doesn't immediately recover money (e.g. PAYMENT_LINK).
    """
    if recovery_case.status != "executing":
        raise InvalidTransitionError(f"Cannot transition to OPEN from {recovery_case.status}")
    
    recovery_case.status = "open"
    db.add(recovery_case)

def transition_to_executing(db: Session, recovery_case: RecoveryCase):
    if recovery_case.status != "approved" or recovery_case.approval_status != ApprovalStatus.APPROVED.value:
        raise InvalidTransitionError(f"Cannot transition to EXECUTING. Case must be APPROVED, current status: {recovery_case.status}, approval_status: {recovery_case.approval_status}")
    
    before_status = recovery_case.status
    recovery_case.status = "executing"
    _create_audit(db, recovery_case, "EXECUTION_STARTED", before_status, recovery_case.status, actor_type="system")

def transition_to_recovered(db: Session, recovery_case: RecoveryCase):
    if recovery_case.status != "executing":
        raise InvalidTransitionError(f"Cannot transition to RECOVERED from {recovery_case.status}")
    
    before_status = recovery_case.status
    recovery_case.status = "recovered"
    recovery_case.closed_at = datetime.now(timezone.utc)
    _create_audit(db, recovery_case, "EXECUTION_SUCCEEDED", before_status, recovery_case.status, actor_type="system")

def transition_to_failed(db: Session, recovery_case: RecoveryCase):
    if recovery_case.status != "executing":
        raise InvalidTransitionError(f"Cannot transition to FAILED from {recovery_case.status}")
    
    before_status = recovery_case.status
    recovery_case.status = "failed"
    recovery_case.closed_at = datetime.now(timezone.utc)
    _create_audit(db, recovery_case, "EXECUTION_FAILED", before_status, recovery_case.status, actor_type="system")
