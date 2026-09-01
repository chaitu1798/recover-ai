from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings
import redis

router = APIRouter()

@router.get("/health", summary="Liveness Check", description="Basic liveness probe. Always returns ok if the API is responding.")
def health_check():
    return {"status": "ok"}

@router.get("/ready", summary="Readiness Check", description="Checks if all required dependencies (DB, Redis) are available.")
def ready_check(db: Session = Depends(get_db)):
    from fastapi import HTTPException
    
    status = {"status": "ok", "components": {}}
    is_ready = True
    
    # Check DB
    try:
        db.execute(text("SELECT 1"))
        status["components"]["database"] = "ok"
    except Exception as e:
        print("DB HEALTH CHECK FAILED:", repr(e))
        status["components"]["database"] = "unhealthy"
        is_ready = False

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        status["components"]["redis"] = "ok"
    except Exception as e:
        status["components"]["redis"] = "unhealthy"
        is_ready = False
        
    if not is_ready:
        raise HTTPException(status_code=503, detail=status)
        
    return status
