from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, Numeric
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
