"""R25 admin emergency stop for NEW outbound sends per connected account.

Revision ID: f25000a10001
Revises: f24000a10001
"""
from alembic import op
import sqlalchemy as sa
revision='f25000a10001'
down_revision='f24000a10001'
branch_labels=None
depends_on=None


def upgrade():
    with op.batch_alter_table('channel_connections') as batch:
        batch.add_column(sa.Column('outbound_paused_at',sa.Float(),nullable=True))
        batch.add_column(sa.Column('outbound_paused_by',sa.String(36),nullable=True))
        batch.add_column(sa.Column('outbound_pause_reason',sa.String(40),nullable=True))


def downgrade():
    with op.batch_alter_table('channel_connections') as batch:
        batch.drop_column('outbound_pause_reason')
        batch.drop_column('outbound_paused_by')
        batch.drop_column('outbound_paused_at')
