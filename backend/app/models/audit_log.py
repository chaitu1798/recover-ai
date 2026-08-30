from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime, timezone
from app.database import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.id'))
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    actor_type = Column(String(30), nullable=False)
    action = Column(String(100), nullable=False)
    before_state = Column(JSONB)
    after_state = Column(JSONB)
    reason = Column(Text)
    correlation_id = Column(String(150), index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
