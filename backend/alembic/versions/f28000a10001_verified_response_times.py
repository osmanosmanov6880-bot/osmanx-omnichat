"""R28: verified provider acceptance / browser render response time.

Revision ID: f28000a10001
Revises: f27000a10001

Historical queued and accepted messages are NOT backfilled from their local
composition timestamp: that would fabricate a provider acceptance time.
"""
from alembic import op
import sqlalchemy as sa

revision='f28000a10001'
down_revision='f27000a10001'
branch_labels=None
depends_on=None


def upgrade():
    with op.batch_alter_table('messages') as b:
        b.add_column(sa.Column('response_confirmed_at',sa.Float(),nullable=True))


def downgrade():
    with op.batch_alter_table('messages') as b:
        b.drop_column('response_confirmed_at')
