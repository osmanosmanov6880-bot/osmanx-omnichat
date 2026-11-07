"""R27 SQL sender slots to serialize one external account across workers.

Revision ID: f27000a10001
Revises: f26000a10001
"""
from alembic import op
import sqlalchemy as sa
revision='f27000a10001'
down_revision='f26000a10001'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('channel_dispatch_leases',
        sa.Column('channel_id',sa.String(length=36),sa.ForeignKey('channel_connections.id'),primary_key=True),
        sa.Column('organization_id',sa.String(length=36),nullable=False),
        sa.Column('owner_token',sa.String(length=36),nullable=False),
        sa.Column('acquired_at',sa.Float(),nullable=False),
        sa.Column('renewed_at',sa.Float(),nullable=False),
        sa.Column('expires_at',sa.Float(),nullable=False))
    op.create_index('ix_channel_dispatch_leases_organization_id','channel_dispatch_leases',['organization_id'])
    op.create_index('ix_channel_dispatch_expiry','channel_dispatch_leases',['expires_at'])
    op.create_index('ix_outgoing_account_status','outgoing_jobs',['channel_id','status'])


def downgrade():
    op.drop_index('ix_outgoing_account_status',table_name='outgoing_jobs')
    op.drop_index('ix_channel_dispatch_expiry',table_name='channel_dispatch_leases')
    op.drop_index('ix_channel_dispatch_leases_organization_id',table_name='channel_dispatch_leases')
    op.drop_table('channel_dispatch_leases')
