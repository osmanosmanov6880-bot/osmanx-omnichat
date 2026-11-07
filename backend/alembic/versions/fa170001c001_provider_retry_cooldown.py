"""Per-account provider 429 cooldown. Revision ID: fa170001c001.
Revises: f1660001c001.
"""
from alembic import op
import sqlalchemy as sa
revision='fa170001c001'
down_revision='f1660001c001'
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table('channel_connections') as b:
        b.add_column(sa.Column('rate_limited_until',sa.Float(),nullable=True))

def downgrade():
    with op.batch_alter_table('channel_connections') as b:
        b.drop_column('rate_limited_until')
