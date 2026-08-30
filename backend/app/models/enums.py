from enum import Enum

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
