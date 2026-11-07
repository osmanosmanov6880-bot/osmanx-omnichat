"""Durable worker heartbeats and explicit cycle-health evidence.

Revision ID: ee4a14b80001
Revises: b1390a1e0001
"""
from alembic import op
import sqlalchemy as sa
revision='ee4a14b80001'
down_revision='b1390a1e0001'
branch_labels=None
depends_on=None


def upgrade():
    op.create_table('worker_heartbeats',
        sa.Column('worker_id',sa.String(64),primary_key=True),
        sa.Column('kind',sa.String(16),nullable=False),
        sa.Column('started_at',sa.Float(),nullable=False),
        sa.Column('last_seen_at',sa.Float(),nullable=False),
        sa.Column('last_cycle_at',sa.Float()),
        sa.Column('stopped_at',sa.Float()),
        sa.Column('error_count',sa.Integer(),nullable=False,server_default='0'),
        sa.Column('processed_jobs',sa.Integer(),nullable=False,server_default='0'))
    op.create_index('ix_worker_heartbeats_status','worker_heartbeats',['stopped_at','last_seen_at'])


def downgrade():
    op.drop_index('ix_worker_heartbeats_status',table_name='worker_heartbeats')
    op.drop_table('worker_heartbeats')
