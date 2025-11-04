"""add pending_registrations table

Revision ID: 20251103_add_pending_registrations
Revises: 
Create Date: 2025-11-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251103_add_pending_registrations'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pending_registrations',
        # use Integer primary key for compatibility with SQLite tests (autoincrement works on INTEGER)
        sa.Column('pending_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(320), nullable=False),
        sa.Column('username', sa.String(150), nullable=True),
        sa.Column('phone_number', sa.String(32), nullable=True),
        sa.Column('region', sa.String(100), nullable=True),
        sa.Column('address', sa.JSON, nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('verification_code_hash', sa.String(255), nullable=False),
    sa.Column('code_expires_at', sa.DateTime, nullable=False),
        sa.Column('attempts', sa.Integer, nullable=False, server_default='0'),
        sa.Column('resend_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('client_ip', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(1024), nullable=True),
    sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
        sa.UniqueConstraint('email', name='uq_pending_email')
    )


def downgrade():
    op.drop_table('pending_registrations')
