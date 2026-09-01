from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.agent.schemas import AgentAnalyzeRequest, AgentAnalyzeResponse
from app.agent.recovery_agent import analyze_recovery_case
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase

router = APIRouter()

@router.post("/analyze", response_model=AgentAnalyzeResponse)
def analyze_case(
    request: AgentAnalyzeRequest,
    db: Session = Depends(get_db)
):
    try:
        response = analyze_recovery_case(db, request.payment_id, request.recovery_case_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
