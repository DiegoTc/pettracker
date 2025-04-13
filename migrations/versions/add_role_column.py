"""add role column to user table

Revision ID: 3f3a8f5a6b12
Revises: 
Create Date: 2025-04-13 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f3a8f5a6b12'
down_revision = None  # Update this if you know your previous migration version
branch_labels = None
depends_on = None


def upgrade():
    # Add the role column with default value 'user'
    op.add_column('user', sa.Column('role', sa.String(20), nullable=False, server_default='user'))


def downgrade():
    # Remove the role column
    op.drop_column('user', 'role')