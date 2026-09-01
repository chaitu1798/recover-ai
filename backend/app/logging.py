import logging
import json
from datetime import datetime, timezone
import contextvars

# Context variables for request correlation
request_id_ctx_var = contextvars.ContextVar("request_id", default=None)

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "recover-ai-backend",
            "event": record.getMessage(),
        }
        
        request_id = request_id_ctx_var.get()
        if request_id:
            log_record["request_id"] = request_id

        # Add any extra attributes added to the log record
        if hasattr(record, "case_id"):
            log_record["case_id"] = record.case_id
        if hasattr(record, "payment_id"):
            log_record["payment_id"] = record.payment_id
        if hasattr(record, "decision_id"):
            log_record["decision_id"] = record.decision_id
        if hasattr(record, "action_id"):
            log_record["action_id"] = record.action_id
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
            
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove all existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    
    # Set levels for some noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
