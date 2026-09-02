from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from app.database import get_db
from app.recovery.executor import execute_recovery
from app.recovery.safety import UnsafeExecutionModeError
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment
from app.models.customer import Customer
from app.models.order import Order
from app.models.recovery_decision import RecoveryDecision
from app.models.recovery_action import RecoveryActionModel
from app.models.audit_log import AuditLog
from sqlalchemy import desc

router = APIRouter(prefix="/recovery", tags=["recovery"])

class ExecuteRequest(BaseModel):
    recovery_case_id: str
    decision_id: str
    idempotency_key: str

class ExecuteResponse(BaseModel):
    recovery_case_id: str
    action: str
    status: str
    recovered_amount: int
    currency: str
    idempotency_key: str
    provider_reference: Optional[str] = None
    attempt_number: int
    idempotent_replay: bool

@router.post("/execute", response_model=ExecuteResponse)
def execute_case(
    request: ExecuteRequest,
    db: Session = Depends(get_db)
):
    try:
        result = execute_recovery(
            db=db,
            case_id=request.recovery_case_id,
            decision_id=request.decision_id,
            idempotency_key=request.idempotency_key
        )
        return result
    except UnsafeExecutionModeError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/cases")
def list_cases(
    db: Session = Depends(get_db), 
    page: int = 1, 
    page_size: int = 25,
    status: Optional[str] = None,
    approval_status: Optional[str] = None,
    failure_reason: Optional[str] = None
):
    if page < 1: page = 1
    if page_size > 100: page_size = 100
    if page_size < 1: page_size = 25

    query = db.query(RecoveryCase, Payment).join(Payment, RecoveryCase.payment_id == Payment.id)
    
    if status:
        query = query.filter(RecoveryCase.status == status)
    if approval_status:
        query = query.filter(RecoveryCase.approval_status == approval_status)
    if failure_reason:
        query = query.filter(Payment.error_code == failure_reason)
        
    total = query.count()
    cases = query.order_by(desc(RecoveryCase.opened_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for c, p in cases:
        result.append({
            "id": str(c.id),
            "payment_id": str(c.payment_id),
            "amount": p.amount, # integer minor units
            "currency": p.currency,
            "status": c.status,
            "approval_status": c.approval_status,
            "error_code": p.error_code,
            "recovery_probability": float(c.recovery_probability) if c.recovery_probability else None,
            "created_at": c.opened_at.isoformat() if c.opened_at else None
        })
        
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/cases/{case_id}")
def get_case_detail(case_id: UUID, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="CASE_NOT_FOUND")
        
    payment = case.payment
    decision = db.query(RecoveryDecision).filter(
        RecoveryDecision.recovery_case_id == case.id
    ).order_by(desc(RecoveryDecision.created_at)).first()
    
    # If case has no decision yet and is open, analyze it with recovery agent
    if not decision and case.status == "open" and payment:
        try:
            from app.agent.recovery_agent import analyze_recovery_case
            analyze_recovery_case(db, payment.id, case.id)
            db.refresh(case)
            decision = db.query(RecoveryDecision).filter(
                RecoveryDecision.recovery_case_id == case.id
            ).order_by(desc(RecoveryDecision.created_at)).first()
        except Exception:
            pass

    action = db.query(RecoveryActionModel).filter(
        RecoveryActionModel.recovery_case_id == case.id
    ).order_by(desc(RecoveryActionModel.created_at)).first()

    audit_logs = db.query(AuditLog).filter(
        AuditLog.entity_id == case.id
    ).order_by(desc(AuditLog.created_at)).all()

    reasoning_dict = decision.reasoning if (decision and isinstance(decision.reasoning, dict)) else {}

    # 1. Authoritative recovery probability
    recovery_prob = None
    if case.recovery_probability is not None:
        recovery_prob = float(case.recovery_probability)
    elif "recovery_probability" in reasoning_dict and reasoning_dict["recovery_probability"] is not None:
        recovery_prob = float(reasoning_dict["recovery_probability"])

    # 2. Authoritative expected recovery value (integer minor units)
    expected_val = None
    if case.expected_recovery_value is not None:
        expected_val = int(case.expected_recovery_value)
    elif "expected_recovery_value_minor" in reasoning_dict and reasoning_dict["expected_recovery_value_minor"] is not None:
        expected_val = int(reasoning_dict["expected_recovery_value_minor"])
    elif recovery_prob is not None and payment and payment.amount is not None:
        expected_val = int(payment.amount * recovery_prob)

    # 3. Authoritative priority level & score
    priority_lvl = case.priority_level or reasoning_dict.get("priority_level")
    if not priority_lvl and recovery_prob is not None and payment:
        from app.recovery.prioritization import calculate_priority
        _, priority_lvl, _ = calculate_priority(recovery_prob, payment.amount, payment.attempt_number)

    priority_scr = None
    if case.priority_score is not None:
        priority_scr = float(case.priority_score)
    elif decision and decision.priority_score is not None:
        priority_scr = float(decision.priority_score)

    # 4. Authoritative diagnosis
    diag = None
    if decision and decision.diagnosis:
        diag = decision.diagnosis
    elif "failure_category" in reasoning_dict:
        diag = reasoning_dict.get("failure_category")
    elif payment and payment.error_code:
        diag = payment.error_code
    else:
        diag = "UNKNOWN"

    return {
        "case": {
            "id": str(case.id),
            "status": case.status,
            "approval_status": case.approval_status,
            "recovery_probability": recovery_prob,
            "expected_recovery_value": expected_val,
            "priority_level": priority_lvl,
            "priority_score": priority_scr,
            "approved_by": case.approved_by,
            "opened_at": case.opened_at.isoformat() if case.opened_at else None,
            "rejected_by": case.rejected_by,
            "rejection_reason": case.rejection_reason
        },
        "payment": {
            "id": str(payment.id) if payment else None,
            "amount": payment.amount if payment else None,
            "currency": payment.currency if payment else "INR",
            "method": payment.method if payment else None,
            "error_code": payment.error_code or "UNKNOWN" if payment else "UNKNOWN"
        },
        "decision": {
            "id": str(decision.id) if decision else None,
            "recommended_action": decision.recommended_action if decision else None,
            "confidence": float(decision.confidence) if decision and decision.confidence is not None else None,
            "diagnosis": diag,
            "reasoning": decision.reasoning if decision else None,
            "strategy": reasoning_dict.get("decision_source") if reasoning_dict else None,
            "policy_checks": decision.policy_checks if decision else None
        },
        "action": {
            "action_type": action.action_type if action else None,
            "status": action.status if action else None
        },
        "audit_logs": [
            {
                "action": log.action,
                "actor": log.actor_type or "system",
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "before_state": log.before_state,
                "after_state": log.after_state,
                "reason": log.reason
            } for log in audit_logs
        ]
    }
