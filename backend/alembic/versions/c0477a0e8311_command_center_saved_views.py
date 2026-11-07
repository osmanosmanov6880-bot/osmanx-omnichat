"""Conversation priority and saved Inbox views.

Revision ID: c0477a0e8311
Revises: ae3c92b4d001
"""
from alembic import op
import sqlalchemy as sa

revision='c0477a0e8311'
down_revision='ae3c92b4d001'
branch_labels=None
depends_on=None


def upgrade():
    op.add_column('conversations',sa.Column('priority',sa.String(length=12),nullable=False,server_default='normal'))
    op.create_index('ix_conversation_tenant_priority','conversations',['organization_id','priority','last_message_at'])
    op.create_index('ix_conversation_tenant_queue','conversations',['organization_id','archived','status','last_message_at'])
    op.create_index('ix_message_tenant_conversation_direction_date','messages',['organization_id','conversation_id','direction','created_at'])
    op.create_table('saved_inbox_views',
        sa.Column('id',sa.String(length=36),primary_key=True),
        sa.Column('organization_id',sa.String(length=36),sa.ForeignKey('organizations.id'),nullable=False),
        sa.Column('creator_user_id',sa.String(length=36),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('name',sa.String(length=64),nullable=False),
        sa.Column('filters_json',sa.Text(),nullable=False),
        sa.Column('shared',sa.Boolean(),nullable=False),
        sa.Column('created_at',sa.Float(),nullable=False),
        sa.UniqueConstraint('organization_id','creator_user_id','name',name='uq_saved_views_owner_name'))
    op.create_index('ix_saved_inbox_views_organization_id','saved_inbox_views',['organization_id'])
    op.create_index('ix_saved_inbox_views_creator_user_id','saved_inbox_views',['creator_user_id'])


def downgrade():
    op.drop_index('ix_saved_inbox_views_creator_user_id',table_name='saved_inbox_views')
    op.drop_index('ix_saved_inbox_views_organization_id',table_name='saved_inbox_views')
    op.drop_table('saved_inbox_views')
    op.drop_index('ix_message_tenant_conversation_direction_date',table_name='messages')
    op.drop_index('ix_conversation_tenant_queue',table_name='conversations')
    op.drop_index('ix_conversation_tenant_priority',table_name='conversations')
    with op.batch_alter_table('conversations') as batch:
        batch.drop_column('priority')
