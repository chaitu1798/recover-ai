from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class RecoveryDecision(Base):
    __tablename__ = 'recovery_decisions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recovery_case_id = Column(UUID(as_uuid=True), ForeignKey('recovery_cases.id'), nullable=False)
    model_name = Column(String(100))
    model_version = Column(String(50))
    diagnosis = Column(Text)
    recommended_action = Column(String(50), nullable=False)
    confidence = Column(Numeric(6,5))
    reasoning = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    recovery_case = relationship('RecoveryCase', back_populates='decisions')
    actions = relationship('RecoveryActionModel', back_populates='decision')
    
    __table_args__ = (
        CheckConstraint(
            "recommended_action IN ('RETRY','PAYMENT_LINK','REMINDER','ESCALATE','NO_ACTION')",
            name='valid_recommended_action'
        ),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='chk_decision_confidence_range'),
    )
