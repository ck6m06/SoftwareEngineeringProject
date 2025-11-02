"""
Alembic migration: add CHECK constraint to prevent owner_id and shelter_id both set

This migration adds a DB-level constraint to help keep animals rows consistent:
  CHECK (NOT (owner_id IS NOT NULL AND shelter_id IS NOT NULL))

The migration is defensive and will attempt to add the constraint; if the DB
doesn't enforce CHECK constraints or raises an error, the exception is ignored
so the upgrade doesn't completely fail in dev setups. In production you should
verify the constraint was applied.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251103_owner_shelter_exclusion'
down_revision = '20251103_add_region_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Add a CHECK constraint to prevent both owner_id and shelter_id being set
    constraint_name = 'chk_owner_or_shelter'
    try:
        # Prefer using Alembic helper
        op.create_check_constraint(
            constraint_name,
            'animals',
            "NOT (owner_id IS NOT NULL AND shelter_id IS NOT NULL)"
        )
    except Exception:
        # Fall back to raw SQL for MySQL / older connectors
        try:
            op.execute(
                f"ALTER TABLE animals ADD CONSTRAINT {constraint_name} CHECK (NOT (owner_id IS NOT NULL AND shelter_id IS NOT NULL))"
            )
        except Exception:
            # ignore - some MySQL installs parse but don't enforce CHECK constraints
            pass


def downgrade():
    constraint_name = 'chk_owner_or_shelter'
    try:
        op.drop_constraint(constraint_name, 'animals', type_='check')
    except Exception:
        try:
            op.execute(f"ALTER TABLE animals DROP CHECK {constraint_name}")
        except Exception:
            pass
