from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from typing import Dict, Any

def create_audit_log(
    db: Session,
    payment: Payment,
    recovery_case: RecoveryCase,
    agent_version: str,
    model_version: str,
    policy_version: str,
    recovery_probability: float,
    failure_category: str,
    recommended_action: str,
    confidence: float,
    policy_result: Dict[str, Any],
    decision_source: str,
    reasoning: str
) -> AuditLog:
    """
    Creates and persists an AuditLog for a decision.
    Never stores sensitive information.
    """
    after_state = {
        "agent_version": agent_version,
        "model_version": model_version,
        "policy_version": policy_version,
        "recovery_probability": float(recovery_probability),
        "failure_category": failure_category,
        "recommended_action": recommended_action,
        "confidence": float(confidence),
        "policy_result": policy_result,
        "decision_source": decision_source,
        "reasoning": reasoning,
    }
    
    audit_log = AuditLog(
        merchant_id=payment.merchant_id,
        entity_type="recovery_case",
        entity_id=recovery_case.id,
        actor_type="ai",
        action="agent_analysis",
        after_state=after_state,
        reason="AI Recovery Agent Analysis completed"
    )
    
    db.add(audit_log)
    db.flush()
    return audit_log
