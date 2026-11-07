"""Cross-process scheduler leases. Revision ID f1660001c001.
Revises: ee4a14b80001.
"""
from alembic import op
import sqlalchemy as sa
revision='f1660001c001'
down_revision='ee4a14b80001'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('scheduler_leases',
        sa.Column('name',sa.String(60),primary_key=True),
        sa.Column('owner_id',sa.String(36),nullable=False),
        sa.Column('acquired_at',sa.Float(),nullable=False),
        sa.Column('renewed_at',sa.Float(),nullable=False),
        sa.Column('expires_at',sa.Float(),nullable=False))
    op.create_index('ix_scheduler_leases_expiry','scheduler_leases',['expires_at'])

def downgrade():
    op.drop_index('ix_scheduler_leases_expiry',table_name='scheduler_leases')
    op.drop_table('scheduler_leases')
