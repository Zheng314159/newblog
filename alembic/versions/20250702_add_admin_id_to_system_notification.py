"""add admin_id to system_notification

Revision ID: 20250702_add_admin_id_to_system_notification
Revises: 20250702_add_system_notification_table
Create Date: 2025-07-02
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250702_add_admin_id_to_system_notification'
down_revision = '20250702_add_system_notification_table'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('system_notification', sa.Column('admin_id', sa.Integer(), nullable=True))
    # SQLite 不支持在线添加外键约束，如需外键请用 batch mode 重建表

def downgrade():
    op.drop_column('system_notification', 'admin_id') 