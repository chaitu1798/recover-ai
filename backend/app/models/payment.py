from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, CheckConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey('merchants.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'))
    razorpay_payment_id = Column(String(100), unique=True, nullable=False)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(10), nullable=False, default='INR')
    method = Column(String(50))
    status = Column(String(30), index=True)
    error_code = Column(String(100))
    error_description = Column(Text)
    attempt_number = Column(Integer, nullable=False, default=1)
    authorized_at = Column(DateTime(timezone=True))
    captured_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    merchant = relationship('Merchant', back_populates='payments')
    customer = relationship('Customer', back_populates='payments')
    order = relationship('Order', back_populates='payments')
    events = relationship('PaymentEvent', back_populates='payment')
    recovery_cases = relationship('RecoveryCase', back_populates='payment')
    
    __table_args__ = (
        CheckConstraint('amount >= 0', name='chk_payment_amount_positive'),
        CheckConstraint('attempt_number >= 1', name='chk_payment_attempt_min'),
    )
