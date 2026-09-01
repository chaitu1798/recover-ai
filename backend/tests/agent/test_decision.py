import pytest
from app.agent.decision import make_decision
from app.models.payment import Payment
from app.models.policy import Policy
from app.agent.schemas import LLMRecommendation

def test_make_decision_llm_allowed():
    payment = Payment(amount=1000)
    policy = Policy(min_confidence=0.8)
    llm_rec = LLMRecommendation(recommended_action="RETRY", confidence=0.9, reasoning="LLM logic")
    
    result = make_decision(
        payment=payment,
        failure_category="TEMPORARY_FAILURE",
        recovery_probability=0.9,
        policy=policy,
        policy_result={"allowed": True},
        llm_recommendation=llm_rec
    )
    
    assert result["recommended_action"] == "RETRY"
    assert result["decision_source"] == "LLM"
    assert result["expected_recovery_value_minor"] == 900

def test_make_decision_llm_denied():
    payment = Payment(amount=1000)
    policy = Policy(min_confidence=0.8)
    llm_rec = LLMRecommendation(recommended_action="RETRY", confidence=0.9, reasoning="LLM logic")
    
    result = make_decision(
        payment=payment,
        failure_category="TEMPORARY_FAILURE",
        recovery_probability=0.9,
        policy=policy,
        policy_result={"allowed": False},
        llm_recommendation=llm_rec
    )
    
    assert result["recommended_action"] == "NO_ACTION"
    assert result["decision_source"] == "DETERMINISTIC_FALLBACK"

def test_make_decision_fallback():
    payment = Payment(amount=1000)
    policy = Policy(min_confidence=0.8)
    
    result = make_decision(
        payment=payment,
        failure_category="TEMPORARY_FAILURE",
        recovery_probability=0.9,
        policy=policy,
        policy_result={"allowed": True},
        llm_recommendation=None
    )
    
    assert result["recommended_action"] == "RETRY"
    assert result["decision_source"] == "DETERMINISTIC_FALLBACK"
