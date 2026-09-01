from typing import Dict, Any, Optional
from app.models.payment import Payment
from app.models.policy import Policy
from app.agent.schemas import LLMRecommendation

def get_fallback_recommendation(
    payment: Payment,
    failure_category: str,
    recovery_probability: float,
    policy: Policy,
    policy_allowed: bool
) -> LLMRecommendation:
    """
    Deterministic fallback logic when LLM is unavailable or policy is denied.
    """
    if not policy_allowed:
        return LLMRecommendation(
            recommended_action="NO_ACTION",
            confidence=1.0,
            reasoning="Policy denial enforced."
        )

    if policy and recovery_probability < float(policy.min_confidence):
        return LLMRecommendation(
            recommended_action="NO_ACTION",
            confidence=1.0,
            reasoning="Recovery probability below threshold."
        )

    if failure_category == "TEMPORARY_FAILURE":
        return LLMRecommendation(
            recommended_action="RETRY",
            confidence=0.8,
            reasoning="Temporary failure mapped to RETRY."
        )
    elif failure_category == "CUSTOMER_ACTION_REQUIRED":
        return LLMRecommendation(
            recommended_action="PAYMENT_LINK",
            confidence=0.8,
            reasoning="Customer action required mapped to PAYMENT_LINK."
        )
    elif failure_category == "FUNDS_PROBLEM":
        return LLMRecommendation(
            recommended_action="REMINDER",
            confidence=0.8,
            reasoning="Funds problem mapped to REMINDER."
        )
    
    return LLMRecommendation(
        recommended_action="NO_ACTION",
        confidence=1.0,
        reasoning="Default fallback to NO_ACTION for unknown or unsupported category."
    )

def make_decision(
    payment: Payment,
    failure_category: str,
    recovery_probability: float,
    policy: Policy,
    policy_result: Dict[str, Any],
    llm_recommendation: Optional[LLMRecommendation]
) -> Dict[str, Any]:
    """
    Combines everything into a final structured decision.
    Calculates expected recovery value in minor units.
    """
    expected_recovery_value_minor = int(payment.amount * recovery_probability)
    policy_allowed = policy_result["allowed"]

    if llm_recommendation and policy_allowed:
        final_action = llm_recommendation.recommended_action
        final_confidence = llm_recommendation.confidence
        final_reasoning = llm_recommendation.reasoning
        decision_source = "LLM"
    else:
        # Fallback (or forced NO_ACTION due to policy)
        fallback = get_fallback_recommendation(
            payment, 
            failure_category, 
            recovery_probability, 
            policy, 
            policy_allowed
        )
        final_action = fallback.recommended_action
        final_confidence = fallback.confidence
        final_reasoning = fallback.reasoning
        decision_source = "DETERMINISTIC_FALLBACK"

    return {
        "recommended_action": final_action,
        "confidence": final_confidence,
        "reasoning": final_reasoning,
        "policy_allowed": policy_allowed,
        "decision_source": decision_source,
        "expected_recovery_value_minor": expected_recovery_value_minor
    }
