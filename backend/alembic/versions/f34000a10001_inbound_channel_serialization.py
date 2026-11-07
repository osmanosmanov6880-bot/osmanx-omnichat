"""R34: fence concurrent inbound consumers for the same connected account."""
from alembic import op
import sqlalchemy as sa

revision='f34000a10001'
down_revision='f33000a10001'
branch_labels=None
depends_on=None

def upgrade():
    with op.batch_alter_table('channel_connections') as b:
        b.add_column(sa.Column('inbound_processing_token',sa.String(36)))
        b.add_column(sa.Column('inbound_processing_job_id',sa.String(36)))
        b.add_column(sa.Column('inbound_processing_until',sa.Float()))

def downgrade():
    with op.batch_alter_table('channel_connections') as b:
        b.drop_column('inbound_processing_until')
        b.drop_column('inbound_processing_job_id')
        b.drop_column('inbound_processing_token')
