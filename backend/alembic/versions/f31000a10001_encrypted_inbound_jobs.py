"""R31 durable encrypted inbound jobs, per-tenant observability and recovery."""
from alembic import op
import sqlalchemy as sa

revision='f31000a10001'
down_revision='f28000a10001'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('inbound_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('channel_id', sa.String(36), sa.ForeignKey('channel_connections.id'), nullable=False),
        sa.Column('provider', sa.String(32), nullable=False),
        sa.Column('fingerprint', sa.String(64), nullable=False),
        sa.Column('encrypted_event', sa.Text()),
        sa.Column('status', sa.String(24), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('duplicates', sa.Integer(), nullable=False),
        sa.Column('next_attempt_at', sa.Float(), nullable=False),
        sa.Column('claimed_at', sa.Float()),
        sa.Column('claim_token', sa.String(36)),
        sa.Column('claim_expires_at', sa.Float()),
        sa.Column('last_error', sa.String(90)),
        sa.Column('created_at', sa.Float(), nullable=False),
        sa.Column('processed_at', sa.Float()),
        sa.UniqueConstraint('channel_id', 'fingerprint', name='uq_inbound_channel_fingerprint'))
    op.create_index('ix_inbound_jobs_organization_id','inbound_jobs',['organization_id'])
    op.create_index('ix_inbound_jobs_channel_id','inbound_jobs',['channel_id'])
    op.create_index('ix_inbound_jobs_poll','inbound_jobs',['status','next_attempt_at'])
    op.create_index('ix_inbound_jobs_tenant_status','inbound_jobs',['organization_id','status','created_at'])
    op.create_index('ix_inbound_jobs_claim_expiry','inbound_jobs',['status','claim_expires_at'])


def downgrade():
    for index in ('ix_inbound_jobs_claim_expiry','ix_inbound_jobs_tenant_status',
                  'ix_inbound_jobs_poll','ix_inbound_jobs_channel_id','ix_inbound_jobs_organization_id'):
        op.drop_index(index,table_name='inbound_jobs')
    op.drop_table('inbound_jobs')
