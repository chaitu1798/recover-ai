"""phase9 indexes

Revision ID: f80350304af4
Revises: f80350304af3
Create Date: 2026-09-02 12:41:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f80350304af4'
down_revision = 'f80350304af3'
branch_labels = None
depends_on = None


def upgrade():
    # Performance indexing for queries heavily used by the Dashboard and Phase 9 ML
    op.create_index('ix_recovery_decisions_recommended_action', 'recovery_decisions', ['recommended_action'])
    op.create_index('ix_experiment_assignments_variant', 'experiment_assignments', ['variant'])


def downgrade():
    op.drop_index('ix_experiment_assignments_variant', table_name='experiment_assignments')
    op.drop_index('ix_recovery_decisions_recommended_action', table_name='recovery_decisions')
