from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import BaseModel
import uuid
import logging
from app.agent.recovery_agent import analyze_recovery_case

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recovery", tags=["recovery"])

class AnalysisRequest(BaseModel):
    payment_id: str
    recovery_case_id: str

@router.post("/analyze")
def analyze_recovery_case(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyzes a failed payment and recommends a recovery action without executing it.
    """
    try:
        recovery_case_id = uuid.UUID(request.recovery_case_id)
        # Note: payment_id is used for payload validation or internal checks if needed.
        
        result = analyze_recovery_case(db, payment_id=uuid.UUID(request.payment_id), recovery_case_id=recovery_case_id)
        return result.model_dump()
        
    except ValueError as e:
        logger.error(f"Value error in agent analysis: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Internal error in agent analysis: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
