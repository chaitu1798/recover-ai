from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Boolean, Numeric, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class RecoveryCase(Base):
    __tablename__ = 'recovery_cases'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey('payments.id'), nullable=False, index=True)
    status = Column(String(30), nullable=False, default='open', index=True)
    amount_at_risk = Column(BigInteger, nullable=False)
    recovery_probability = Column(Numeric(6,5))
    priority_score = Column(Numeric(10,5), index=True)
    eligible = Column(Boolean, nullable=False, default=True)
    eligibility_reason = Column(Text)
    opened_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True))
    
    payment = relationship('Payment', back_populates='recovery_cases')
    decisions = relationship('RecoveryDecision', back_populates='recovery_case')
    actions = relationship('RecoveryActionModel', back_populates='recovery_case')
    
    __table_args__ = (
        CheckConstraint('amount_at_risk >= 0', name='chk_recovery_amount_positive'),
        CheckConstraint('recovery_probability >= 0 AND recovery_probability <= 1', name='chk_recovery_prob_range'),
    )
