"""Separate in-progress preparation from a possibly sent provider POST.

Revision ID: f23000a10001
Revises: f20000a10001

IMPORTANT: Existing R22 processing jobs have no claim_token. The worker treats
these as possibly sent and quarantines them. Do not stamp legacy jobs with a
new token: that would cause unsafe automatic retries after migration.
"""
from alembic import op
import sqlalchemy as sa
revision='f23000a10001'
down_revision='f20000a10001'
branch_labels=None
depends_on=None


def upgrade():
    with op.batch_alter_table('outgoing_jobs') as batch:
        batch.add_column(sa.Column('claim_token',sa.String(36),nullable=True))
        batch.add_column(sa.Column('send_started_at',sa.Float(),nullable=True))


def downgrade():
    with op.batch_alter_table('outgoing_jobs') as batch:
        batch.drop_column('send_started_at')
        batch.drop_column('claim_token')
