"""R36 dispatch gates and privacy-safe delivery transition receipts.

Revision ID: f36000a10001
Revises: f35000a10001 (verified R35 archive).
"""
from alembic import op
import sqlalchemy as sa
revision='f36000a10001'
down_revision='f35000a10001'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('dispatch_pauses',
        sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('organization_id',sa.String(36),nullable=False),
        sa.Column('channel_id',sa.String(36),nullable=False),
        sa.Column('reason_code',sa.String(40),nullable=False),
        sa.Column('expires_at',sa.Float()),
        sa.Column('created_at',sa.Float(),nullable=False),
        sa.Column('actor_user_id',sa.String(36),nullable=False),
        sa.UniqueConstraint('organization_id','channel_id',name='uq_dispatch_pause_scope'))
    op.create_index('ix_dispatch_pause_org_expiry','dispatch_pauses',['organization_id','expires_at'])
    op.create_table('delivery_transitions',
        sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('organization_id',sa.String(36),nullable=False),
        sa.Column('job_id',sa.String(36),nullable=False),
        sa.Column('status_from',sa.String(25),nullable=False),
        sa.Column('status_to',sa.String(25),nullable=False),
        sa.Column('event_code',sa.String(40),nullable=False),
        sa.Column('attempts',sa.Integer(),nullable=False),
        sa.Column('created_at',sa.Float(),nullable=False))
    op.create_index('ix_delivery_transition_org_time','delivery_transitions',['organization_id','created_at'])
    op.create_index('ix_delivery_transition_job_time','delivery_transitions',['organization_id','job_id','created_at'])


def downgrade():
    op.drop_index('ix_delivery_transition_job_time',table_name='delivery_transitions')
    op.drop_index('ix_delivery_transition_org_time',table_name='delivery_transitions')
    op.drop_table('delivery_transitions')
    op.drop_index('ix_dispatch_pause_org_expiry',table_name='dispatch_pauses')
    op.drop_table('dispatch_pauses')
