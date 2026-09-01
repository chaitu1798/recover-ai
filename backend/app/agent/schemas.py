from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID

class LLMRecommendation(BaseModel):
    recommended_action: Literal["RETRY", "PAYMENT_LINK", "REMINDER", "NO_ACTION"] = Field(..., description="Must be RETRY, PAYMENT_LINK, REMINDER, or NO_ACTION")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(...)

class AgentAnalyzeRequest(BaseModel):
    payment_id: UUID
    recovery_case_id: UUID

class AgentAnalyzeResponse(BaseModel):
    decision_id: UUID
    recovery_case_id: UUID
    failure_category: str
    recovery_probability: float
    recommended_action: str
    agent_confidence: float
    policy_allowed: bool
    reasoning: str
    decision_source: str
    agent_version: str
    model_version: str
    policy_version: str
