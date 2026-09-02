from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, webhooks, agent, recovery
from app.api.api_v1.endpoints import approval, dashboard
from app.logging import setup_logging
from app.middleware import RequestCorrelationMiddleware
from app.logging import request_id_ctx_var
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="RecoverAI", description="AI Revenue Recovery Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestCorrelationMiddleware)

# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    request_id = request_id_ctx_var.get()
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc),
                "request_id": request_id
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    request_id = request_id_ctx_var.get()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "request_id": request_id
            }
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    request_id = request_id_ctx_var.get()
    # E.g. our "Not eligible for execution" errors
    status_code = 400
    if "Approval required" in str(exc):
        status_code = 403
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": "BAD_REQUEST",
                "message": str(exc),
                "request_id": request_id
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    request_id = request_id_ctx_var.get()
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id
            }
        }
    )

app.include_router(health.router, tags=["Health"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(recovery.router, prefix="/api/v1")
app.include_router(approval.router, prefix="/api/v1/recovery", tags=["Approval"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "Welcome to RecoverAI API"}
