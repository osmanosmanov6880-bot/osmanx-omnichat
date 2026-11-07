"""Durable login abuse receipts without storing email addresses.

Revision ID: ab111f611001
Revises: f1000010cafe
"""
from alembic import op
import sqlalchemy as sa

revision='ab111f611001'
down_revision='f1000010cafe'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('login_failures',
        sa.Column('id',sa.String(length=36),primary_key=True),
        sa.Column('email_digest',sa.String(length=64),nullable=False),
        sa.Column('attempted_at',sa.Float(),nullable=False))
    op.create_index('ix_login_failure_identity_time','login_failures',['email_digest','attempted_at'])

def downgrade():
    op.drop_index('ix_login_failure_identity_time',table_name='login_failures')
    op.drop_table('login_failures')
