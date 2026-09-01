from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment
from app.models.enums import ApprovalStatus

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_cases = db.query(func.count(RecoveryCase.id)).scalar() or 0
    open_cases = db.query(func.count(RecoveryCase.id)).filter(RecoveryCase.status == 'open').scalar() or 0
    pending_approval = db.query(func.count(RecoveryCase.id)).filter(RecoveryCase.approval_status == ApprovalStatus.PENDING_APPROVAL.value).scalar() or 0
    approved_cases = db.query(func.count(RecoveryCase.id)).filter(RecoveryCase.approval_status == ApprovalStatus.APPROVED.value).scalar() or 0
    rejected_cases = db.query(func.count(RecoveryCase.id)).filter(RecoveryCase.approval_status == ApprovalStatus.REJECTED.value).scalar() or 0
    executing_cases = db.query(func.count(RecoveryCase.id)).filter(RecoveryCase.status == 'executing').scalar() or 0
    recovered_cases = db.query(func.count(RecoveryCase.id)).filter(RecoveryCase.status == 'recovered').scalar() or 0
    failed_cases = db.query(func.count(RecoveryCase.id)).filter(RecoveryCase.status == 'failed').scalar() or 0

    # Revenue metrics (integer minor units)
    revenue_at_risk = db.query(func.sum(Payment.amount)).join(RecoveryCase, RecoveryCase.payment_id == Payment.id).scalar() or 0
    
    # Calculate predicted recoverable revenue based on cases that are pending or approved
    predicted_revenue = db.query(
        func.sum(RecoveryCase.amount_at_risk * RecoveryCase.recovery_probability)
    ).filter(
        RecoveryCase.approval_status.in_([ApprovalStatus.PENDING_APPROVAL.value, ApprovalStatus.APPROVED.value]),
        RecoveryCase.status.in_(['pending_approval', 'approved', 'analyzed', 'open'])
    ).scalar() or 0
    
    # Calculate average probability
    avg_probability = db.query(func.avg(RecoveryCase.recovery_probability)).scalar() or 0
    
    recovered_revenue = db.query(func.sum(Payment.amount)).join(RecoveryCase, RecoveryCase.payment_id == Payment.id).filter(RecoveryCase.status == 'recovered').scalar() or 0

    recovery_rate = (recovered_cases / total_cases) if total_cases > 0 else 0
    approval_rate = (approved_cases / (approved_cases + rejected_cases)) if (approved_cases + rejected_cases) > 0 else 0
    execution_success_rate = (recovered_cases / (recovered_cases + failed_cases)) if (recovered_cases + failed_cases) > 0 else 0

    return {
        "total_cases": total_cases,
        "open_cases": open_cases,
        "pending_approval": pending_approval,
        "approved_cases": approved_cases,
        "rejected_cases": rejected_cases,
        "executing_cases": executing_cases,
        "recovered_cases": recovered_cases,
        "failed_cases": failed_cases,
        
        "revenue_at_risk": int(revenue_at_risk),
        "predicted_recoverable_revenue": int(predicted_revenue),
        "recovered_revenue": int(recovered_revenue),
        
        "recovery_rate": float(recovery_rate),
        "average_recovery_probability": float(avg_probability),
        
        "policy_block_rate": 0, # Placeholder
        "approval_rate": float(approval_rate),
        "execution_success_rate": float(execution_success_rate)
    }
