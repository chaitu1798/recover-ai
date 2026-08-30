from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class PaymentEvent(Base):
    __tablename__ = 'payment_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey('payments.id'))
    event_type = Column(String(100), nullable=False, index=True)
    razorpay_event_id = Column(String(150), unique=True)
    payload = Column(JSONB, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True))
    processing_status = Column(String(30), nullable=False, default='pending', index=True)
    
    payment = relationship('Payment', back_populates='events')
