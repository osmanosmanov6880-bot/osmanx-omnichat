"""Stable message-history cursor index.

Revision ID: f20000a10001
Revises: f19000a10001
"""
from alembic import op
revision='f20000a10001'
down_revision='f19000a10001'
branch_labels=None
depends_on=None


def upgrade():
    op.create_index('ix_message_history_cursor','messages',
                    ['organization_id','conversation_id','created_at','id'])


def downgrade():
    op.drop_index('ix_message_history_cursor',table_name='messages')
