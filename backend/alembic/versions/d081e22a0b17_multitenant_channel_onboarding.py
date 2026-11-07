"""Track each company's provider verification and webhook readiness.

Revision ID: d081e22a0b17
Revises: c0477a0e8311
"""
from alembic import op
import sqlalchemy as sa

revision = 'd081e22a0b17'
down_revision = 'c0477a0e8311'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('channel_connections') as batch:
        for field in ('last_verified_at', 'webhook_verified_at', 'webhook_registered_at', 'token_expires_at'):
            batch.add_column(sa.Column(field, sa.Float(), nullable=True))
    op.create_table('pending_channel_selections',
        sa.Column('id',sa.String(length=36),primary_key=True),
        sa.Column('user_id',sa.String(length=36),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('organization_id',sa.String(length=36),sa.ForeignKey('organizations.id'),nullable=False),
        sa.Column('provider',sa.String(length=32),nullable=False),
        sa.Column('encrypted_payload',sa.Text(),nullable=False),
        sa.Column('expires_at',sa.Float(),nullable=False),
        sa.Column('created_at',sa.Float(),nullable=False))
    op.create_index('ix_pending_channel_selection_owner','pending_channel_selections',['organization_id','user_id'])
    # A single active identity may only be routed to one tenant. Rejected duplicates
    # must be resolved by explicit disconnect; no automatic reassignment of data.
    duplicates=op.get_bind().execute(sa.text('''
        SELECT provider, external_account_id, count(*) AS n
        FROM channel_connections
        WHERE mode='live' AND status!='disconnected' AND external_account_id IS NOT NULL
        GROUP BY provider,external_account_id HAVING count(*)>1 LIMIT 1
    ''')).first()
    if duplicates:
        raise RuntimeError('Обнаружены неоднозначные подключения внешних аккаунтов: проверьте дубли до миграции. Автоматическая передача переписок другой компании запрещена.')
    condition = "mode = 'live' AND status != 'disconnected' AND external_account_id IS NOT NULL"
    op.create_index('uq_live_channel_identity', 'channel_connections', ['provider','external_account_id'], unique=True,
        sqlite_where=sa.text(condition), postgresql_where=sa.text(condition))


def downgrade():
    op.drop_index('uq_live_channel_identity', table_name='channel_connections')
    op.drop_index('ix_pending_channel_selection_owner',table_name='pending_channel_selections')
    op.drop_table('pending_channel_selections')
    with op.batch_alter_table('channel_connections') as batch:
        for field in ('token_expires_at', 'webhook_registered_at', 'webhook_verified_at', 'last_verified_at'):
            batch.drop_column(field)
