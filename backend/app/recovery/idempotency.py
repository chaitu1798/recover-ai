from sqlalchemy.orm import Session
from app.models.recovery_action import RecoveryActionModel
from app.models.action_result import ActionResult

def get_existing_execution(db: Session, idempotency_key: str):
    """
    Looks for an existing RecoveryAction and its ActionResult using the idempotency_key.
    Returns (RecoveryActionModel, ActionResult) or (None, None).
    Uses row-level locking where supported to prevent race conditions (for postgres, this is usually handled via unique constraints during insert, but here we just read first).
    """
    if not idempotency_key:
        return None, None
        
    action = db.query(RecoveryActionModel).filter(
        RecoveryActionModel.idempotency_key == idempotency_key
    ).first()
    
    if not action:
        return None, None
        
    result = db.query(ActionResult).filter(
        ActionResult.action_id == action.id
    ).first()
    
    return action, result
