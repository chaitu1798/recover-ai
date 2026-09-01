import pytest
from app.agent.decision import make_decision
from app.models.payment import Payment
from app.models.policy import Policy
from app.agent.schemas import LLMRecommendation

def test_safety_unsupported_action():
    # Even if LLM somehow bypasses Pydantic schema (it shouldn't, but let's test safety boundary)
    payment = Payment(amount=1000)
    policy = Policy(min_confidence=0.8)
    
    from pydantic import ValidationError
    try:
        llm_rec = LLMRecommendation(recommended_action="EXECUTE_PAYMENT", confidence=0.9, reasoning="Bad LLM")
        assert False, "Pydantic should have blocked this"
    except ValidationError:
        assert True

def test_safety_policy_override():
    payment = Payment(amount=1000)
    policy = Policy(min_confidence=0.8)
    llm_rec = LLMRecommendation(recommended_action="RETRY", confidence=0.9, reasoning="LLM says retry")
    
    # Policy says NOT allowed
    result = make_decision(
        payment=payment,
        failure_category="UNKNOWN",
        recovery_probability=0.9,
        policy=policy,
        policy_result={"allowed": False, "violations": ["Amount too high"]},
        llm_recommendation=llm_rec
    )
    
    assert result["recommended_action"] == "NO_ACTION"
    assert result["decision_source"] == "DETERMINISTIC_FALLBACK"
