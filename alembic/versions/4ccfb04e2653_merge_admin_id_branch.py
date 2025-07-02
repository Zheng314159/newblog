"""merge admin_id branch

Revision ID: 4ccfb04e2653
Revises: 2801042e8946, 20250702_add_admin_id_to_system_notification
Create Date: 2025-07-02 19:40:19.414906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ccfb04e2653'
down_revision: Union[str, None] = ('2801042e8946', '20250702_add_admin_id_to_system_notification')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
