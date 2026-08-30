from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Boolean, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime, timezone
from app.database import Base

class Policy(Base):
    __tablename__ = 'policies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.id'))
    policy_name = Column(String(100), nullable=False)
    max_attempts = Column(Integer, nullable=False, default=2)
    min_confidence = Column(Numeric(6,5), nullable=False, default=0.80)
    max_auto_action_amount = Column(BigInteger)
    enabled = Column(Boolean, nullable=False, default=True)
    rules = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        CheckConstraint('min_confidence >= 0 AND min_confidence <= 1', name='chk_policy_confidence_range'),
    )
