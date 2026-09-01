from fastapi import FastAPI
from app.api import health, webhooks, agent

app = FastAPI(title="RecoverAI", description="AI Revenue Recovery Platform")

app.include_router(health.router)
app.include_router(health.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to RecoverAI API"}
