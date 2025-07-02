"""add system_notification table

Revision ID: 20250702_add_system_notification_table
Revises: 
Create Date: 2025-07-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250702_add_system_notification_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'system_notification',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('message', sa.String(length=1024), nullable=False),
        sa.Column('notification_type', sa.String(length=32), server_default='info'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('is_sent', sa.Boolean, server_default=sa.text('0'))
    )

def downgrade():
    op.drop_table('system_notification') 