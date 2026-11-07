"""First-party site widgets, visitor sessions and conversation leases.

Revision ID: ae3c92b4d001
Revises: b692c1e3cebe
"""
from alembic import op
import sqlalchemy as sa

revision='ae3c92b4d001'
down_revision='b692c1e3cebe'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('organizations',sa.Column('currency',sa.String(length=3),nullable=False,server_default='RUB'))
    op.add_column('organizations',sa.Column('timezone',sa.String(length=64),nullable=False,server_default='UTC'))
    op.add_column('conversations',sa.Column('reply_lock_owner_id',sa.String(length=36),nullable=True))
    op.add_column('conversations',sa.Column('reply_lock_expires_at',sa.Float(),nullable=True))
    op.create_table('website_widgets',
        sa.Column('id',sa.String(length=36),primary_key=True),
        sa.Column('organization_id',sa.String(length=36),sa.ForeignKey('organizations.id'),nullable=False),
        sa.Column('channel_id',sa.String(length=36),sa.ForeignKey('channel_connections.id'),nullable=False,unique=True),
        sa.Column('public_key',sa.String(length=64),nullable=False),
        sa.Column('allowed_origins',sa.Text(),nullable=False),
        sa.Column('greeting',sa.String(length=240),nullable=False),
        sa.Column('accent',sa.String(length=7),nullable=False),
        sa.Column('enabled',sa.Boolean(),nullable=False),
        sa.Column('created_at',sa.Float(),nullable=False))
    op.create_index('ix_website_widgets_organization_id','website_widgets',['organization_id'])
    op.create_index('ix_website_widgets_public_key','website_widgets',['public_key'], unique=True)
    op.create_table('website_visitors',
        sa.Column('id',sa.String(length=36),primary_key=True),
        sa.Column('organization_id',sa.String(length=36),sa.ForeignKey('organizations.id'),nullable=False),
        sa.Column('widget_id',sa.String(length=36),sa.ForeignKey('website_widgets.id'),nullable=False),
        sa.Column('token_hash',sa.String(length=64),nullable=False,unique=True),
        sa.Column('conversation_id',sa.String(length=36),sa.ForeignKey('conversations.id')),
        sa.Column('nickname',sa.String(length=80),nullable=False),
        sa.Column('expires_at',sa.Float(),nullable=False),
        sa.Column('last_activity_at',sa.Float(),nullable=False),
        sa.Column('created_at',sa.Float(),nullable=False))
    op.create_index('ix_website_visitors_organization_id','website_visitors',['organization_id'])
    op.create_index('ix_website_visitors_widget_id','website_visitors',['widget_id'])


def downgrade():
    op.drop_index('ix_website_visitors_widget_id',table_name='website_visitors')
    op.drop_index('ix_website_visitors_organization_id',table_name='website_visitors')
    op.drop_table('website_visitors')
    op.drop_index('ix_website_widgets_public_key',table_name='website_widgets')
    op.drop_index('ix_website_widgets_organization_id',table_name='website_widgets')
    op.drop_table('website_widgets')
    with op.batch_alter_table('conversations') as batch:
        batch.drop_column('reply_lock_expires_at')
        batch.drop_column('reply_lock_owner_id')
    with op.batch_alter_table('organizations') as batch:
        batch.drop_column('timezone')
        batch.drop_column('currency')
