import pytest
import uuid
from unittest.mock import patch, MagicMock

from app.agent.recovery_agent import analyze_recovery_case
from app.models.payment import Payment
from app.models.recovery_case import RecoveryCase
from app.models.policy import Policy
from app.models.recovery_decision import RecoveryDecision
from app.agent.schemas import LLMRecommendation

@patch('app.agent.recovery_agent.predict_recovery')
@patch('app.agent.recovery_agent.provider.get_recommendation')
def test_agent_analyze_case(mock_get_recommendation, mock_predict_recovery):
    db_mock = MagicMock()

    payment = Payment(id=uuid.uuid4(), merchant_id=uuid.uuid4(), amount=1000, attempt_number=1, error_code="BANK_TIMEOUT", currency="INR", method="card")
    recovery_case = RecoveryCase(id=uuid.uuid4(), payment_id=payment.id, eligible=True)
    policy = Policy(merchant_id=payment.merchant_id, min_confidence=0.5, max_attempts=3, enabled=True)

    # Mock queries
    def side_effect(model):
        query_mock = MagicMock()
        if model == Payment:
            query_mock.filter.return_value.first.return_value = payment
        elif model == RecoveryCase:
            query_mock.filter.return_value.first.return_value = recovery_case
        elif model == RecoveryDecision:
            query_mock.filter.return_value.order_by.return_value.first.return_value = None
        elif model == Policy:
            query_mock.filter.return_value.first.return_value = policy
        return query_mock

    db_mock.query.side_effect = side_effect

    def mock_add(obj):
        obj.id = uuid.uuid4()
    db_mock.add.side_effect = mock_add

    mock_predict_recovery.return_value = {"recovery_probability": 0.9, "model_name": "test", "model_version": "1.0"}
    mock_get_recommendation.return_value = LLMRecommendation(recommended_action="RETRY", confidence=0.95, reasoning="LLM logic")

    response = analyze_recovery_case(db_mock, payment.id, recovery_case.id)

    assert response.recommended_action == "RETRY"
    assert response.policy_allowed is True
    assert response.decision_source == "LLM"
    assert db_mock.add.call_count == 2 # One for decision, one for audit log

@patch('app.agent.recovery_agent.predict_recovery')
def test_agent_idempotency(mock_predict_recovery):
    db_mock = MagicMock()

    payment = Payment(id=uuid.uuid4(), merchant_id=uuid.uuid4(), amount=1000, attempt_number=1, error_code="BANK_TIMEOUT", currency="INR", method="card")
    recovery_case = RecoveryCase(id=uuid.uuid4(), payment_id=payment.id, eligible=True)

    existing_decision = RecoveryDecision(
        id=uuid.uuid4(),
        recovery_case_id=recovery_case.id,
        recommended_action="PAYMENT_LINK",
        confidence=0.8,
        model_version="1.0",
        reasoning={"decision_source": "DETERMINISTIC_FALLBACK"}
    )

    def side_effect(model):
        query_mock = MagicMock()
        if model == Payment:
            query_mock.filter.return_value.first.return_value = payment
        elif model == RecoveryCase:
            query_mock.filter.return_value.first.return_value = recovery_case
        elif model == RecoveryDecision:
            query_mock.filter.return_value.order_by.return_value.first.return_value = existing_decision
        return query_mock

    db_mock.query.side_effect = side_effect

    response = analyze_recovery_case(db_mock, payment.id, recovery_case.id)

    assert response.recommended_action == "PAYMENT_LINK"
    assert response.decision_source == "DETERMINISTIC_FALLBACK"
    assert db_mock.add.call_count == 0 # Should not add anything
