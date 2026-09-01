from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.recovery.executor import execute_recovery
from app.recovery.safety import UnsafeExecutionModeError
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment

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
def list_cases(db: Session = Depends(get_db), limit: int = 50):
    cases = db.query(RecoveryCase, Payment).join(Payment, RecoveryCase.payment_id == Payment.id).limit(limit).all()
    result = []
    for c, p in cases:
        result.append({
            "id": str(c.id),
            "payment_id": str(c.payment_id),
            "amount": float(p.amount) / 100, # Mock formatting
            "currency": p.currency,
            "status": c.status,
            "error_code": p.error_code,
            "created_at": c.created_at.isoformat() if c.created_at else None
        })
    return result
