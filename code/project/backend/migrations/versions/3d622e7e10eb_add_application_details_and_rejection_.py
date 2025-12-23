"""add_application_details_and_rejection_fields

Revision ID: 3d622e7e10eb
Revises: 54b26531e228
Create Date: 2025-10-29 15:20:48.207403

整合 003_system_fixes.sql 的內容:
- 問題2: 領養申請表單添加申請人詳細資料 (7個新欄位)
- 問題5: 動物拒絕批准原因登錄 (3個新欄位 + 外鍵)

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d622e7e10eb'
down_revision = '54b26531e228'
branch_labels = None
depends_on = None


def upgrade():
    # 使用原生 SQL 檢查欄位是否存在,避免重複添加
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # 問題2: 領養申請表單添加申請人詳細資料
    existing_app_columns = [col['name'] for col in inspector.get_columns('applications')]
    
    with op.batch_alter_table('applications', schema=None) as batch_op:
        if 'contact_phone' not in existing_app_columns:
            batch_op.add_column(sa.Column('contact_phone', sa.String(length=32), nullable=True, comment='聯絡電話'))
        if 'contact_address' not in existing_app_columns:
            batch_op.add_column(sa.Column('contact_address', sa.String(length=500), nullable=True, comment='聯絡地址'))
        if 'occupation' not in existing_app_columns:
            batch_op.add_column(sa.Column('occupation', sa.String(length=100), nullable=True, comment='職業'))
        if 'housing_type' not in existing_app_columns:
            batch_op.add_column(sa.Column('housing_type', sa.String(length=50), nullable=True, comment='居住環境'))
        if 'has_experience' not in existing_app_columns:
            batch_op.add_column(sa.Column('has_experience', sa.Boolean(), default=False, comment='是否有養寵經驗'))
        if 'reason' not in existing_app_columns:
            batch_op.add_column(sa.Column('reason', sa.Text(), nullable=True, comment='領養原因'))
        if 'notes' not in existing_app_columns:
            batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True, comment='其他備註'))

    # 問題5: 動物拒絕批准原因登錄
    existing_animal_columns = [col['name'] for col in inspector.get_columns('animals')]
    
    with op.batch_alter_table('animals', schema=None) as batch_op:
        if 'rejection_reason' not in existing_animal_columns:
            batch_op.add_column(sa.Column('rejection_reason', sa.Text(), nullable=True, comment='拒絕原因'))
        if 'rejected_at' not in existing_animal_columns:
            batch_op.add_column(sa.Column('rejected_at', sa.DateTime(timezone=6), nullable=True, comment='拒絕時間'))
        if 'rejected_by' not in existing_animal_columns:
            batch_op.add_column(sa.Column('rejected_by', sa.BigInteger(), nullable=True, comment='拒絕者ID'))
        
        # 檢查外鍵是否存在
        existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('animals')]
        if 'fk_animals_rejected_by' not in existing_fks:
            batch_op.create_foreign_key('fk_animals_rejected_by', 'users', ['rejected_by'], ['user_id'])


def downgrade():
    # 移除動物拒絕相關欄位
    with op.batch_alter_table('animals', schema=None) as batch_op:
        batch_op.drop_constraint('fk_animals_rejected_by', type_='foreignkey')
        batch_op.drop_column('rejected_by')
        batch_op.drop_column('rejected_at')
        batch_op.drop_column('rejection_reason')

    # 移除申請表單詳細資料欄位
    with op.batch_alter_table('applications', schema=None) as batch_op:
        batch_op.drop_column('notes')
        batch_op.drop_column('reason')
        batch_op.drop_column('has_experience')
        batch_op.drop_column('housing_type')
        batch_op.drop_column('occupation')
        batch_op.drop_column('contact_address')
        batch_op.drop_column('contact_phone')
