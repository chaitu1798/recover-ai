from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models.recovery_case import RecoveryCase
from app.models.enums import ApprovalStatus
from app.recovery.state_machine import transition_to_approved, transition_to_rejected, InvalidTransitionError

router = APIRouter()

class ApproveRequest(BaseModel):
    approved_by: str
    reason: str

class RejectRequest(BaseModel):
    rejected_by: str
    reason: str

@router.post("/{case_id}/approve")
def approve_recovery_case(
    case_id: UUID,
    request: ApproveRequest,
    db: Session = Depends(get_db)
):
    case = db.query(RecoveryCase).with_for_update().filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.approval_status == ApprovalStatus.APPROVED.value:
        return {"status": "success", "message": "Already approved"}
        
    if case.approval_status == ApprovalStatus.REJECTED.value:
        raise HTTPException(status_code=409, detail="Case already rejected")
        
    try:
        transition_to_approved(db, case, request.approved_by, request.reason)
        db.commit()
        return {"status": "success", "message": "Approval granted"}
    except InvalidTransitionError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{case_id}/reject")
def reject_recovery_case(
    case_id: UUID,
    request: RejectRequest,
    db: Session = Depends(get_db)
):
    case = db.query(RecoveryCase).with_for_update().filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.approval_status == ApprovalStatus.REJECTED.value:
        return {"status": "success", "message": "Already rejected"}
        
    if case.approval_status == ApprovalStatus.APPROVED.value:
        raise HTTPException(status_code=409, detail="Case already approved")
        
    try:
        transition_to_rejected(db, case, request.rejected_by, request.reason)
        db.commit()
        return {"status": "success", "message": "Approval rejected"}
    except InvalidTransitionError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
