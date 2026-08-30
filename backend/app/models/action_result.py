from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class ActionResult(Base):
    __tablename__ = 'action_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_id = Column(UUID(as_uuid=True), ForeignKey('recovery_actions.id'), nullable=False)
    success = Column(Boolean)
    razorpay_reference = Column(String(150))
    previous_payment_status = Column(String(50))
    final_payment_status = Column(String(50))
    recovered_amount = Column(BigInteger, nullable=False, default=0)
    error_code = Column(String(100))
    error_message = Column(Text)
    response_payload = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    action = relationship('RecoveryActionModel', back_populates='results')
