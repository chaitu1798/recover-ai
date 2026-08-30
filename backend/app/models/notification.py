from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime, timezone
from app.database import Base

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.id'))
    recovery_case_id = Column(UUID(as_uuid=True), ForeignKey('recovery_cases.id'))
    channel = Column(String(30))
    recipient = Column(String(255))
    template = Column(String(100))
    status = Column(String(30))
    provider_reference = Column(String(150))
    payload = Column(JSONB)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
