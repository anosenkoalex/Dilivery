"""add geometry column to zones

Revision ID: 65c40ee3c1ce
Revises: 4474c7bcdced
Create Date: 2025-06-25 21:40:41.814211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65c40ee3c1ce'
down_revision: Union[str, Sequence[str], None] = '4474c7bcdced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('zones') as batch_op:
        batch_op.add_column(sa.Column('geometry', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('zones') as batch_op:
        batch_op.drop_column('geometry')

