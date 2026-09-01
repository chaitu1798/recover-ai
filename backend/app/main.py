from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, webhooks, agent, recovery
from app.api.api_v1.endpoints import approval, dashboard

app = FastAPI(title="RecoverAI", description="AI Revenue Recovery Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(health.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
app.include_router(recovery.router, prefix="/api/v1")
app.include_router(approval.router, prefix="/api/v1/recovery", tags=["Approval"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "Welcome to RecoverAI API"}
