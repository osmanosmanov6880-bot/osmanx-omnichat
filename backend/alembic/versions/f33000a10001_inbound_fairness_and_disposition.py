"""R33 cross-worker fair inbound scheduling and auditable terminal disposition."""
from alembic import op
import sqlalchemy as sa

revision='f33000a10001'
down_revision='f32000a10001'
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table('channel_connections') as b:
        b.add_column(sa.Column('inbound_last_dispatched_at',sa.Float()))
    with op.batch_alter_table('inbound_jobs') as b:
        b.add_column(sa.Column('dismissed_at',sa.Float()))
        b.add_column(sa.Column('dismissed_by',sa.String(36)))
        b.add_column(sa.Column('dismissal_code',sa.String(32)))
    op.create_index('ix_inbound_jobs_ready_channel', 'inbound_jobs',
                    ['channel_id','status','next_attempt_at','created_at'])

def downgrade():
    op.drop_index('ix_inbound_jobs_ready_channel',table_name='inbound_jobs')
    with op.batch_alter_table('inbound_jobs') as b:
        b.drop_column('dismissal_code')
        b.drop_column('dismissed_by')
        b.drop_column('dismissed_at')
    with op.batch_alter_table('channel_connections') as b:
        b.drop_column('inbound_last_dispatched_at')
