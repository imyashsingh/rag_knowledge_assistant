"""Add owner_id to workspaces table

Revision ID: 002
Revises: 001
Create Date: 2026-05-10 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make workspace_id nullable in users table first
    op.alter_column('users', 'workspace_id', nullable=True)

    # Add owner_id column as nullable first
    op.add_column('workspaces', sa.Column(
        'owner_id', sa.Integer(), nullable=True))

    # Create foreign key constraint
    op.create_foreign_key('fk_workspaces_owner_id',
                          'workspaces', 'users', ['owner_id'], ['id'])

    # Migrate existing workspaces: assign to first user in each workspace
    op.execute('''
        UPDATE workspaces 
        SET owner_id = (
            SELECT u.id 
            FROM users u 
            WHERE u.workspace_id = workspaces.id 
            ORDER BY u.id ASC 
            LIMIT 1
        )
        WHERE owner_id IS NULL
    ''')

    # Make owner_id NOT NULL after migration
    op.alter_column('workspaces', 'owner_id', nullable=False)


def downgrade() -> None:
    # Make workspace_id NOT NULL again
    op.alter_column('users', 'workspace_id', nullable=False)

    # Remove foreign key constraint
    op.drop_constraint('fk_workspaces_owner_id',
                       'workspaces', type_='foreignkey')

    # Remove owner_id column
    op.drop_column('workspaces', 'owner_id')
