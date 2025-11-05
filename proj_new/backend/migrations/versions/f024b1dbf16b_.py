"""empty message

Revision ID: f024b1dbf16b
Revises: 20251103_add_pending_registrations, 20251103_owner_shelter_exclusion
Create Date: 2025-11-05 07:06:45.020838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f024b1dbf16b'
down_revision = ('20251103_add_pending_registrations', '20251103_owner_shelter_exclusion')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
