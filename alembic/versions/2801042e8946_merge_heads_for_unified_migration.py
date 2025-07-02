"""merge heads for unified migration

Revision ID: 2801042e8946
Revises: 20250702_add_system_notification_table, f78a29ab6185
Create Date: 2025-07-02 19:26:14.274708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2801042e8946'
down_revision: Union[str, None] = ('20250702_add_system_notification_table', 'f78a29ab6185')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
