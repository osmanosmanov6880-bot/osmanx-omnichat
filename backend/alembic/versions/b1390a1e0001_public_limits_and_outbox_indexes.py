"""Shared public rate buckets and fair-queue supporting indexes.

Revision ID: b1390a1e0001
Revises: ab111f611001
"""
from alembic import op
import sqlalchemy as sa
revision='b1390a1e0001'
down_revision='ab111f611001'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('public_rate_buckets',
        sa.Column('scope',sa.String(60),primary_key=True),
        sa.Column('actor_digest',sa.String(64),primary_key=True),
        sa.Column('window_start',sa.Integer(),primary_key=True),
        sa.Column('attempts',sa.Integer(),nullable=False),
        sa.Column('created_at',sa.Float(),nullable=False))
    op.create_index('ix_public_rate_bucket_cleanup','public_rate_buckets',['created_at'])
    op.create_index('ix_outgoing_due','outgoing_jobs',
                    ['status','next_attempt_at','organization_id','created_at'])
    op.create_index('ix_outgoing_processing','outgoing_jobs',['status','claimed_at'])


def downgrade():
    op.drop_index('ix_outgoing_processing',table_name='outgoing_jobs')
    op.drop_index('ix_outgoing_due',table_name='outgoing_jobs')
    op.drop_index('ix_public_rate_bucket_cleanup',table_name='public_rate_buckets')
    op.drop_table('public_rate_buckets')
