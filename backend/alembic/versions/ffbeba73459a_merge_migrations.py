"""merge migrations

Revision ID: ffbeba73459a
Revises: 002, add_chat_history
Create Date: 2026-05-10 14:43:03.446899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffbeba73459a'
down_revision: Union[str, Sequence[str], None] = ('002', 'add_chat_history')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
