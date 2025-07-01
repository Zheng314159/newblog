"""add uploader_id to media_file

Revision ID: e997a413f07f
Revises: d20b6d12e9eb
Create Date: 2025-07-01 18:12:31.204409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e997a413f07f'
down_revision: Union[str, None] = 'd20b6d12e9eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('media_file') as batch_op:
        batch_op.add_column(sa.Column('uploader_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_media_file_uploader_id_user', 'user', ['uploader_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('media_file') as batch_op:
        batch_op.drop_constraint('fk_media_file_uploader_id_user', type_='foreignkey')
        batch_op.drop_column('uploader_id')
