"""Add name column to chat_history table

Revision ID: 2ed541dd97fb
Revises: ffbeba73459a
Create Date: 2026-05-10 16:58:06.988780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2ed541dd97fb'
down_revision: Union[str, Sequence[str], None] = 'ffbeba73459a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add name column to chat_history table
    op.add_column('chat_history', sa.Column(
        'name', sa.VARCHAR(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove name column from chat_history table
    op.drop_column('chat_history', 'name')
    # ### end Alembic commands ###
