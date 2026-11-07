"""Durable, tenant-scoped WhatsApp delivery status callbacks.

Revision ID: f24000a10001
Revises: f23000a10001
"""
from alembic import op
import sqlalchemy as sa
revision='f24000a10001'
down_revision='f23000a10001'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('provider_delivery_receipts',
        sa.Column('channel_id',sa.String(36),sa.ForeignKey('channel_connections.id'),primary_key=True),
        sa.Column('external_message_id',sa.String(250),primary_key=True),
        sa.Column('organization_id',sa.String(36),nullable=False),
        sa.Column('status',sa.String(20),nullable=False),
        sa.Column('recipient_digest',sa.String(64)),
        sa.Column('first_seen_at',sa.Float(),nullable=False),
        sa.Column('last_seen_at',sa.Float(),nullable=False))
    op.create_index('ix_provider_receipts_cleanup','provider_delivery_receipts',['last_seen_at'])
    op.create_index('ix_provider_delivery_receipts_organization_id',
                    'provider_delivery_receipts',['organization_id'])


def downgrade():
    op.drop_index('ix_provider_delivery_receipts_organization_id',table_name='provider_delivery_receipts')
    op.drop_index('ix_provider_receipts_cleanup',table_name='provider_delivery_receipts')
    op.drop_table('provider_delivery_receipts')
