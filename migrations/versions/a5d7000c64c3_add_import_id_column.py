"""add import_id column

Revision ID: a5d7000c64c3
Revises: d4419d51f884
Create Date: 2025-06-22 02:53:52.069652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5d7000c64c3'
down_revision = 'd4419d51f884'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('import_id', sa.String(length=36), nullable=True))


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('import_id')
