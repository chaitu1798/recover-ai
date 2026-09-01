from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any

from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from app.models.policy import Policy
from app.models.recovery_decision import RecoveryDecision

from app.agent import AGENT_VERSION, POLICY_VERSION
from app.agent.diagnosis import diagnose_failure
from app.agent.policy_engine import evaluate_policy
from app.agent.providers.openai_provider import OpenAIProvider
from app.agent.prompts import build_prompt
from app.agent.decision import make_decision
from app.agent.audit import create_audit_log
from app.agent.schemas import AgentAnalyzeResponse
from app.ml.features import build_preprocessor
from app.ml.predict import predict_recovery

provider = OpenAIProvider()

def extract_features(payment: Payment) -> Dict[str, Any]:
    return {
        "amount": float(payment.amount),
        "attempt_number": payment.attempt_number,
        "previous_successes": 0, # Placeholder
        "previous_failures": payment.attempt_number - 1,
        "customer_tenure_days": 30, # Placeholder
        "time_since_failure_minutes": 60, # Placeholder
        "historical_recovery_rate": 0.5, # Placeholder
        "currency": payment.currency,
        "payment_method": payment.method or "unknown",
        "failure_reason": payment.error_code or "unknown"
    }

def analyze_recovery_case(db: Session, payment_id: UUID, recovery_case_id: UUID) -> AgentAnalyzeResponse:
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    recovery_case = db.query(RecoveryCase).filter(RecoveryCase.id == recovery_case_id).first()
    
    if not payment:
        raise ValueError(f"Payment {payment_id} not found.")
    if not recovery_case:
        raise ValueError(f"RecoveryCase {recovery_case_id} not found.")
    if recovery_case.payment_id != payment.id:
        raise ValueError("Payment and RecoveryCase mismatch.")
        
    # Check for existing decision (Idempotency)
    existing_decision = db.query(RecoveryDecision).filter(
        RecoveryDecision.recovery_case_id == recovery_case.id
    ).order_by(RecoveryDecision.created_at.desc()).first()
    
    if existing_decision:
        reasoning_data = existing_decision.reasoning or {}
        return AgentAnalyzeResponse(
            decision_id=existing_decision.id,
            recovery_case_id=recovery_case.id,
            failure_category=reasoning_data.get("failure_category", "UNKNOWN"),
            recovery_probability=float(reasoning_data.get("recovery_probability", 0.0)),
            recommended_action=existing_decision.recommended_action,
            agent_confidence=float(existing_decision.confidence),
            policy_allowed=reasoning_data.get("policy_allowed", False),
            reasoning=reasoning_data.get("reasoning", str(existing_decision.reasoning)),
            decision_source=reasoning_data.get("decision_source", "UNKNOWN"),
            agent_version=reasoning_data.get("agent_version", AGENT_VERSION),
            model_version=existing_decision.model_version,
            policy_version=reasoning_data.get("policy_version", POLICY_VERSION)
        )
        
    policy = db.query(Policy).filter(Policy.merchant_id == payment.merchant_id).first()
    
    # 1. Extract Features & Predict
    features = extract_features(payment)
    ml_result = predict_recovery(features)
    recovery_probability = ml_result["recovery_probability"]
    model_version = ml_result["model_version"]
    
    # 2. Diagnose
    failure_category = diagnose_failure(payment.error_code or "OTHER")
    
    # 3. Ask LLM (optional)
    prompt = build_prompt(
        payment_amount=float(payment.amount),
        currency=payment.currency,
        failure_reason=payment.error_code or "OTHER",
        failure_category=failure_category,
        recovery_probability=recovery_probability,
        attempt_number=payment.attempt_number,
        policy_summary=str(policy.rules if policy else "No explicit rules")
    )
    llm_recommendation = provider.get_recommendation(prompt)
    
    # 4. Evaluate Policy
    temp_action = llm_recommendation.recommended_action if llm_recommendation else "NO_ACTION"
    policy_result = evaluate_policy(policy, payment, recovery_case, recovery_probability, temp_action)
    
    # 5. Final Decision
    final_decision = make_decision(
        payment,
        failure_category,
        recovery_probability,
        policy,
        policy_result,
        llm_recommendation
    )
    
    # 6. Save Decision
    reasoning_data = {
        "reasoning": final_decision["reasoning"],
        "agent_version": AGENT_VERSION,
        "policy_version": POLICY_VERSION,
        "failure_category": failure_category,
        "recovery_probability": float(recovery_probability),
        "policy_allowed": final_decision["policy_allowed"],
        "decision_source": final_decision["decision_source"],
        "expected_recovery_value_minor": final_decision["expected_recovery_value_minor"]
    }
    
    decision = RecoveryDecision(
        recovery_case_id=recovery_case.id,
        model_name=ml_result["model_name"],
        model_version=model_version,
        diagnosis=failure_category,
        recommended_action=final_decision["recommended_action"],
        confidence=final_decision["confidence"],
        reasoning=reasoning_data
    )
    db.add(decision)
    
    # 7. Create Audit Log
    create_audit_log(
        db=db,
        payment=payment,
        recovery_case=recovery_case,
        agent_version=AGENT_VERSION,
        model_version=model_version,
        policy_version=POLICY_VERSION,
        recovery_probability=recovery_probability,
        failure_category=failure_category,
        recommended_action=final_decision["recommended_action"],
        confidence=final_decision["confidence"],
        policy_result=policy_result,
        decision_source=final_decision["decision_source"],
        reasoning=final_decision["reasoning"]
    )
    
    db.flush() # Ensure decision has an ID
    db.commit()
    
    return AgentAnalyzeResponse(
        decision_id=decision.id,
        recovery_case_id=recovery_case.id,
        failure_category=failure_category,
        recovery_probability=recovery_probability,
        recommended_action=final_decision["recommended_action"],
        agent_confidence=final_decision["confidence"],
        policy_allowed=final_decision["policy_allowed"],
        reasoning=final_decision["reasoning"],
        decision_source=final_decision["decision_source"],
        agent_version=AGENT_VERSION,
        model_version=model_version,
        policy_version=POLICY_VERSION
    )
