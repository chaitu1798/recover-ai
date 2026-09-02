from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class ExperimentAssignment(Base):
    __tablename__ = 'experiment_assignments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey('experiments.id'), nullable=False, index=True)
    recovery_case_id = Column(UUID(as_uuid=True), ForeignKey('recovery_cases.id'), nullable=False, index=True)
    assigned_strategy = Column(String(50), nullable=False)
    variant = Column(String(50), nullable=False)
    outcome = Column(String(50))
    recovered_amount = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    
    experiment = relationship('Experiment')
    recovery_case = relationship('RecoveryCase')
    
    __table_args__ = (
        UniqueConstraint('experiment_id', 'recovery_case_id', name='uq_experiment_case_assignment'),
    )
