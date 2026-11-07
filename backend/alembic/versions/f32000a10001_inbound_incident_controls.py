"""R32 inbound tenant/channel processing controls and bounded encrypted ingress."""
from alembic import op
import sqlalchemy as sa

revision='f32000a10001'
down_revision='f31000a10001'
branch_labels=None
depends_on=None

def upgrade():
    for table in ('organizations','channel_connections'):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column('inbound_paused_at',sa.Float()))
            batch.add_column(sa.Column('inbound_paused_by',sa.String(36)))
            batch.add_column(sa.Column('inbound_pause_reason',sa.String(160)))

def downgrade():
    for table in ('channel_connections','organizations'):
        with op.batch_alter_table(table) as batch:
            batch.drop_column('inbound_pause_reason')
            batch.drop_column('inbound_paused_by')
            batch.drop_column('inbound_paused_at')
