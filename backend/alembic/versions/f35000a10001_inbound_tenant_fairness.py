"""R35: persistent organization-level inbound scheduling checkpoint."""
from alembic import op
import sqlalchemy as sa

revision = 'f35000a10001'
down_revision = 'f34000a10001'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('organizations') as batch:
        batch.add_column(sa.Column('inbound_last_dispatched_at', sa.Float(), nullable=True))

def downgrade():
    with op.batch_alter_table('organizations') as batch:
        batch.drop_column('inbound_last_dispatched_at')
