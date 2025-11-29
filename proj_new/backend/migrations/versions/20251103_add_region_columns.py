"""
Alembic migration: add region columns to shelters and users and populate shelters.region

NOTE: This file is a minimal migration stub. Please set `down_revision` to the
current head of your migrations before running `flask db upgrade`.

It is written defensively so running it twice is safe in most environments.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '20251103_add_region_columns'
down_revision = '24f846716da3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # add shelters.region if not exists
    shelter_columns = [col['name'] for col in inspector.get_columns('shelters')]
    if 'region' not in shelter_columns:
        op.add_column('shelters', sa.Column('region', sa.String(length=100), nullable=True))

    # add users.region if not exists
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'region' not in user_columns:
        op.add_column('users', sa.Column('region', sa.String(length=100), nullable=True))

    # populate shelters.region from JSON address->city where possible
    try:
        op.execute("""
        UPDATE shelters
        SET region = JSON_UNQUOTE(JSON_EXTRACT(address, '$.city'))
        WHERE (region IS NULL OR region = '') AND address IS NOT NULL;
        """)
    except Exception:
        # ignore if DB doesn't support JSON_EXTRACT or other issues - do manually if needed
        pass


def downgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # NOTE: downgrading will drop the columns; keep in mind this removes data.
    shelter_columns = [col['name'] for col in inspector.get_columns('shelters')]
    if 'region' in shelter_columns:
        op.drop_column('shelters', 'region')
    
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'region' in user_columns:
        op.drop_column('users', 'region')
