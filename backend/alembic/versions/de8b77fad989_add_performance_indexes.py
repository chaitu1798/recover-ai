"""add_performance_indexes

Revision ID: de8b77fad989
Revises: a15a0a689b7a
Create Date: 2026-09-01 18:23:44.112595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de8b77fad989'
down_revision: Union[str, Sequence[str], None] = 'a15a0a689b7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_recovery_cases_approval_status', 'recovery_cases', ['approval_status'])
    op.create_index('ix_recovery_decisions_recovery_case_id', 'recovery_decisions', ['recovery_case_id'])
    op.create_index('ix_recovery_actions_recovery_case_id', 'recovery_actions', ['recovery_case_id'])
    op.create_index('ix_payment_events_payment_id', 'payment_events', ['payment_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_payment_events_payment_id', table_name='payment_events')
    op.drop_index('ix_recovery_actions_recovery_case_id', table_name='recovery_actions')
    op.drop_index('ix_recovery_decisions_recovery_case_id', table_name='recovery_decisions')
    op.drop_index('ix_recovery_cases_approval_status', table_name='recovery_cases')
