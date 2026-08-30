from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Merchant(Base):
    __tablename__ = 'merchants'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    razorpay_account_id = Column(String(100))
    environment = Column(String(20), nullable=False, default='test')
    currency = Column(String(10), nullable=False, default='INR')
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    customers = relationship('Customer', back_populates='merchant')
    orders = relationship('Order', back_populates='merchant')
    payments = relationship('Payment', back_populates='merchant')
