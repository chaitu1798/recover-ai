from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class RecoveryActionModel(Base):
    __tablename__ = 'recovery_actions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recovery_case_id = Column(UUID(as_uuid=True), ForeignKey('recovery_cases.id'), nullable=False)
    decision_id = Column(UUID(as_uuid=True), ForeignKey('recovery_decisions.id'))
    action_type = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False, default='pending', index=True)
    idempotency_key = Column(String(150), unique=True)
    attempt_number = Column(Integer, nullable=False, default=1)
    approved_by_policy = Column(Boolean, nullable=False, default=False)
    policy_reason = Column(Text)
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    recovery_case = relationship('RecoveryCase', back_populates='actions')
    decision = relationship('RecoveryDecision', back_populates='actions')
    results = relationship('ActionResult', back_populates='action')
    
    __table_args__ = (
        CheckConstraint(
            "action_type IN ('RETRY','PAYMENT_LINK','REMINDER','ESCALATE','NO_ACTION')",
            name='valid_action_type'
        ),
    )
