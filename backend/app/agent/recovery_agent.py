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
from app.recovery.state_machine import transition_to_analyzed, transition_to_pending_approval
from app.agent.schemas import AgentAnalyzeResponse
from app.ml.features import build_preprocessor
from app.ml.predict import predict_recovery
from app.recovery.prioritization import calculate_priority
from app.recovery.strategy import select_strategy
from app.recovery.experimentation import assign_experiment_variant
from app.models.experiment import Experiment
from app.models.experiment_assignment import ExperimentAssignment
from datetime import datetime, timezone

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
            reasoning=str(reasoning_data.get("reasoning", existing_decision.reasoning)),
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
    
    # 3. Strategy Optimizer (replaces/augments LLM)
    strat_action, strat_conf, strat_reasons, strat_exp = select_strategy(
        recovery_probability=recovery_probability,
        failure_reason=failure_category,
        attempt_number=payment.attempt_number,
        customer_history_success_rate=0.5 # placeholder
    )
    
    # 3.5 Check for active experiments
    now = datetime.now(timezone.utc)
    active_experiment = db.query(Experiment).filter(
        Experiment.start_date <= now,
        (Experiment.end_date == None) | (Experiment.end_date >= now)
    ).first()
    
    assigned_variant = None
    experiment_id = None
    if active_experiment:
        experiment_id = active_experiment.id
        variants = ["CONTROL", "VARIANT"]
        assigned_variant = assign_experiment_variant(recovery_case.id, active_experiment.id, variants)
        
        # Determine overridden action based on experiment variant
        if assigned_variant == "VARIANT" and active_experiment.strategy != strat_action:
            strat_action = active_experiment.strategy
            strat_reasons.append("EXPERIMENT_VARIANT_OVERRIDE")
            strat_exp = f"Overridden by experiment {active_experiment.name} variant."
        
        # Save assignment
        assignment = db.query(ExperimentAssignment).filter(
            ExperimentAssignment.experiment_id == active_experiment.id,
            ExperimentAssignment.recovery_case_id == recovery_case.id
        ).first()
        if not assignment:
            assignment = ExperimentAssignment(
                experiment_id=active_experiment.id,
                recovery_case_id=recovery_case.id,
                assigned_strategy=strat_action,
                variant=assigned_variant
            )
            db.add(assignment)
    
    # Optional LLM can still run, but strategy takes precedence for deterministic reasoning
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
    policy_result = evaluate_policy(policy, payment, recovery_case, recovery_probability, strat_action)
    
    # 5. Calculate Priority
    priority_score, priority_level, priority_exp = calculate_priority(
        recovery_probability=recovery_probability,
        amount_at_risk=payment.amount,
        attempt_number=payment.attempt_number
    )
    
    expected_value_minor = int(payment.amount * recovery_probability)
    recovery_case.priority_level = priority_level
    recovery_case.expected_recovery_value = expected_value_minor
    recovery_case.recovery_probability = recovery_probability
    db.add(recovery_case)
    
    # 6. Final Decision
    final_action = strat_action if policy_result["allowed"] else "NO_ACTION"
    final_confidence = strat_conf
    final_reasoning = {"strategy_explanation": strat_exp, "priority_explanation": priority_exp}
    
    # 7. Save Decision
    reasoning_data = {
        "reasoning": final_reasoning,
        "agent_version": AGENT_VERSION,
        "policy_version": POLICY_VERSION,
        "failure_category": failure_category,
        "recovery_probability": float(recovery_probability),
        "policy_allowed": policy_result["allowed"],
        "decision_source": "STRATEGY_OPTIMIZER",
        "expected_recovery_value_minor": expected_value_minor,
        "priority_level": priority_level,
        "experiment_id": str(experiment_id) if experiment_id else None,
        "experiment_variant": assigned_variant
    }
    
    decision = RecoveryDecision(
        recovery_case_id=recovery_case.id,
        model_name=ml_result["model_name"],
        model_version=model_version,
        diagnosis=failure_category,
        recommended_action=final_action,
        confidence=final_confidence,
        priority_score=priority_score,
        policy_checks=policy_result["checks"],
        reason_codes=strat_reasons,
        reasoning=reasoning_data
    )
    db.add(decision)
    
    # 8. Create Audit Log
    create_audit_log(
        db=db,
        payment=payment,
        recovery_case=recovery_case,
        agent_version=AGENT_VERSION,
        model_version=model_version,
        policy_version=POLICY_VERSION,
        recovery_probability=recovery_probability,
        failure_category=failure_category,
        recommended_action=final_action,
        confidence=final_confidence,
        policy_result=policy_result,
        decision_source="STRATEGY_OPTIMIZER",
        reasoning=str(final_reasoning)
    )
    
    db.flush() # Ensure decision has an ID
    
    if final_action != "NO_ACTION" and policy_result["allowed"]:
        transition_to_pending_approval(db, recovery_case, str(decision.id))
    else:
        transition_to_analyzed(db, recovery_case, str(decision.id))
        
    db.commit()
    
    return AgentAnalyzeResponse(
        decision_id=decision.id,
        recovery_case_id=recovery_case.id,
        failure_category=failure_category,
        recovery_probability=recovery_probability,
        recommended_action=final_action,
        agent_confidence=final_confidence,
        policy_allowed=policy_result["allowed"],
        reasoning=str(final_reasoning),
        decision_source="STRATEGY_OPTIMIZER",
        agent_version=AGENT_VERSION,
        model_version=model_version,
        policy_version=POLICY_VERSION
    )
