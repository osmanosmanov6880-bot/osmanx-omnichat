"""Track read-only official channel checks and throttle requests.

Revision ID: f1000010cafe
Revises: e15caa761102
"""
from alembic import op
import sqlalchemy as sa

revision = "f1000010cafe"
down_revision = "e15caa761102"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("channel_connections") as batch:
        batch.add_column(sa.Column("last_probe_at", sa.Float(), nullable=True))

def downgrade():
    with op.batch_alter_table("channel_connections") as batch:
        batch.drop_column("last_probe_at")
