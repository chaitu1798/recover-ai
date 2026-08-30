from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.id'), nullable=False, index=True)
    external_customer_id = Column(String(100))
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(30))
    total_orders = Column(Integer, nullable=False, default=0)
    successful_orders = Column(Integer, nullable=False, default=0)
    failed_orders = Column(Integer, nullable=False, default=0)
    total_spend = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    merchant = relationship('Merchant', back_populates='customers')
    orders = relationship('Order', back_populates='customer')
    payments = relationship('Payment', back_populates='customer')
    
    __table_args__ = (
        UniqueConstraint('merchant_id', 'external_customer_id', name='uq_merchant_customer'),
    )
