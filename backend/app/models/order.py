from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'))
    razorpay_order_id = Column(String(100), unique=True, nullable=False)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(10), nullable=False, default='INR')
    status = Column(String(30), index=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    merchant = relationship('Merchant', back_populates='orders')
    customer = relationship('Customer', back_populates='orders')
    payments = relationship('Payment', back_populates='order')
    
    __table_args__ = (
        CheckConstraint('amount >= 0', name='chk_order_amount_positive'),
    )
