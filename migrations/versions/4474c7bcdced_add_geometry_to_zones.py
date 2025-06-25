"""add geometry to zones

Revision ID: 4474c7bcdced
Revises: e3203e9b82f3
Create Date: 2025-06-25 07:30:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '4474c7bcdced'
down_revision: Union[str, Sequence[str], None] = 'e3203e9b82f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('zones', sa.Column('geometry', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('zones', 'geometry')
