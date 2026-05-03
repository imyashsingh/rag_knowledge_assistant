"""Add chat_history table

Revision ID: add_chat_history
Revises: 
Create Date: 2026-05-03 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_chat_history'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create chat_history table
    op.create_table('chat_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('sources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for better query performance
    op.create_index('ix_chat_history_user_workspace', 'chat_history', ['user_id', 'workspace_id'])
    op.create_index('ix_chat_history_created_at', 'chat_history', ['created_at'])
    op.create_index('ix_chat_history_session_id', 'chat_history', ['session_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_chat_history_session_id', table_name='chat_history')
    op.drop_index('ix_chat_history_created_at', table_name='chat_history')
    op.drop_index('ix_chat_history_user_workspace', table_name='chat_history')
    
    # Drop table
    op.drop_table('chat_history')
