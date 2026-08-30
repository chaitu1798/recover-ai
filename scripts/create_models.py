import os

models_dir = 'backend/app/models'
os.makedirs(models_dir, exist_ok=True)

models = {
"enums.py": """from enum import Enum

class PaymentStatus(str, Enum):
    created = 'created'
    authorized = 'authorized'
    captured = 'captured'
    failed = 'failed'
    refunded = 'refunded'
    expired = 'expired'
    unknown = 'unknown'

class RecoveryCaseStatus(str, Enum):
    open = 'open'
    closed = 'closed'
    resolved = 'resolved'

class RecoveryAction(str, Enum):
    RETRY = 'RETRY'
    PAYMENT_LINK = 'PAYMENT_LINK'
    REMINDER = 'REMINDER'
    ESCALATE = 'ESCALATE'
    NO_ACTION = 'NO_ACTION'

class ActionStatus(str, Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'
    unknown = 'unknown'

class ActorType(str, Enum):
    system = 'system'
    ai = 'ai'
    user = 'user'

class ExperimentStrategy(str, Enum):
    baseline = 'baseline'
    ai = 'ai'

class ProcessingStatus(str, Enum):
    pending = 'pending'
    processed = 'processed'
    failed = 'failed'
""",
"__init__.py": """from .enums import *
from .merchant import Merchant
from .customer import Customer
from .order import Order
from .payment import Payment
from .payment_event import PaymentEvent
from .recovery_case import RecoveryCase
from .recovery_decision import RecoveryDecision
from .recovery_action import RecoveryActionModel
from .action_result import ActionResult
from .policy import Policy
from .audit_log import AuditLog
from .experiment import Experiment
from .experiment_result import ExperimentResult
from .notification import Notification
""",
"merchant.py": """from sqlalchemy import Column, String, DateTime
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
""",
"customer.py": """from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, UniqueConstraint
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
""",
"order.py": """from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, CheckConstraint
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
""",
"payment.py": """from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, CheckConstraint, Text
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
""",
"payment_event.py": """from sqlalchemy import Column, String, DateTime, ForeignKey
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
""",
"recovery_case.py": """from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Boolean, Numeric, CheckConstraint, Text
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
    )
""",
"recovery_decision.py": """from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class RecoveryDecision(Base):
    __tablename__ = 'recovery_decisions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recovery_case_id = Column(UUID(as_uuid=True), ForeignKey('recovery_cases.id'), nullable=False)
    model_name = Column(String(100))
    model_version = Column(String(50))
    diagnosis = Column(Text)
    recommended_action = Column(String(50), nullable=False)
    confidence = Column(Numeric(6,5))
    reasoning = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    recovery_case = relationship('RecoveryCase', back_populates='decisions')
    actions = relationship('RecoveryActionModel', back_populates='decision')
    
    __table_args__ = (
        CheckConstraint(
            "recommended_action IN ('RETRY','PAYMENT_LINK','REMINDER','ESCALATE','NO_ACTION')",
            name='valid_recommended_action'
        ),
    )
""",
"recovery_action.py": """from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class RecoveryActionModel(Base):
    __tablename__ = 'recovery_actions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recovery_case_id = Column(UUID(as_uuid=True), ForeignKey('recovery_cases.id'), nullable=False)
    decision_id = Column(UUID(as_uuid=True), ForeignKey('recovery_decisions.id'))
    action_type = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False, default='pending', index=True)
    idempotency_key = Column(String(150), unique=True)
    attempt_number = Column(Integer, nullable=False, default=1)
    approved_by_policy = Column(Boolean, nullable=False, default=False)
    policy_reason = Column(Text)
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    recovery_case = relationship('RecoveryCase', back_populates='actions')
    decision = relationship('RecoveryDecision', back_populates='actions')
    results = relationship('ActionResult', back_populates='action')
    
    __table_args__ = (
        CheckConstraint(
            "action_type IN ('RETRY','PAYMENT_LINK','REMINDER','ESCALATE','NO_ACTION')",
            name='valid_action_type'
        ),
    )
""",
"action_result.py": """from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Boolean, Text
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
""",
"policy.py": """from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Boolean, Numeric
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
""",
"audit_log.py": """from sqlalchemy import Column, String, DateTime, ForeignKey, Text
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
""",
"experiment.py": """from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Experiment(Base):
    __tablename__ = 'experiments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    strategy = Column(String(50), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    results = relationship('ExperimentResult', back_populates='experiment')
""",
"experiment_result.py": """from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class ExperimentResult(Base):
    __tablename__ = 'experiment_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey('experiments.id'), nullable=False)
    total_cases = Column(Integer, nullable=False, default=0)
    eligible_cases = Column(Integer, nullable=False, default=0)
    actions_executed = Column(Integer, nullable=False, default=0)
    successful_recoveries = Column(Integer, nullable=False, default=0)
    revenue_at_risk = Column(BigInteger, nullable=False, default=0)
    revenue_recovered = Column(BigInteger, nullable=False, default=0)
    recovery_rate = Column(Numeric(8,5))
    false_positive_rate = Column(Numeric(8,5))
    average_attempts = Column(Numeric(8,4))
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    experiment = relationship('Experiment', back_populates='results')
""",
"notification.py": """from sqlalchemy import Column, String, DateTime, ForeignKey
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
"""
}

for name, content in models.items():
    with open(os.path.join(models_dir, name), "w", encoding="utf-8") as f:
        f.write(content)

print("Models created.")
