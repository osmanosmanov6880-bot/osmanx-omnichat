"""Provider webhook and outbound acceptance evidence.

Revision ID: e15caa761102
Revises: d081e22a0b17
"""
from alembic import op
import sqlalchemy as sa

revision='e15caa761102'
down_revision='d081e22a0b17'
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table('channel_connections') as batch:
        batch.add_column(sa.Column('webhook_provider_verified_at',sa.Float(),nullable=True))
        batch.add_column(sa.Column('outbound_api_accepted_at',sa.Float(),nullable=True))

def downgrade():
    with op.batch_alter_table('channel_connections') as batch:
        batch.drop_column('outbound_api_accepted_at')
        batch.drop_column('webhook_provider_verified_at')
