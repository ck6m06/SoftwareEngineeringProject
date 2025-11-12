"""add_adopted_status_to_animals

Revision ID: 46c1eaf9c935
Revises: 3d622e7e10eb
Create Date: 2025-10-29 16:40:05.606442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46c1eaf9c935'
down_revision = '3d622e7e10eb'
branch_labels = None
depends_on = None


def upgrade():
    # 修改 animals 表的 status 欄位，添加 ADOPTED 值
    # MySQL ENUM 需要重新定義所有值
    op.execute("""
        ALTER TABLE animals 
        MODIFY COLUMN status ENUM('DRAFT', 'SUBMITTED', 'PUBLISHED', 'ADOPTED', 'RETIRED') 
        NOT NULL DEFAULT 'DRAFT'
    """)


def downgrade():
    # 移除 ADOPTED 值 (將所有 ADOPTED 改回 PUBLISHED)
    op.execute("UPDATE animals SET status = 'PUBLISHED' WHERE status = 'ADOPTED'")
    op.execute("""
        ALTER TABLE animals 
        MODIFY COLUMN status ENUM('DRAFT', 'SUBMITTED', 'PUBLISHED', 'RETIRED') 
        NOT NULL DEFAULT 'DRAFT'
    """)
