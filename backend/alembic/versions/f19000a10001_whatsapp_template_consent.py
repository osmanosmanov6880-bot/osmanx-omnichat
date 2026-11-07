"""Consent ledger for approved WhatsApp templates.

Revision ID: f19000a10001
Revises: fa170001c001
"""
from alembic import op
import sqlalchemy as sa
revision='f19000a10001'
down_revision='fa170001c001'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('whatsapp_consents',
        sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('organization_id',sa.String(36),sa.ForeignKey('organizations.id'),nullable=False),
        sa.Column('contact_id',sa.String(36),sa.ForeignKey('contacts.id'),nullable=False),
        sa.Column('channel_id',sa.String(36),sa.ForeignKey('channel_connections.id'),nullable=False),
        sa.Column('recipient_id',sa.String(250),nullable=False),
        sa.Column('source',sa.String(240),nullable=False),
        sa.Column('captured_at',sa.Float(),nullable=False),
        sa.Column('revoked_at',sa.Float()),
        sa.Column('recorded_by',sa.String(36),sa.ForeignKey('users.id')),
        sa.UniqueConstraint('channel_id','recipient_id',name='uq_whatsapp_consent_channel_recipient'))
    op.create_index('ix_whatsapp_consents_organization_id','whatsapp_consents',['organization_id'])

def downgrade():
    op.drop_index('ix_whatsapp_consents_organization_id',table_name='whatsapp_consents')
    op.drop_table('whatsapp_consents')
