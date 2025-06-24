"""Add import_batch_id to orders

Revision ID: fedcba987654
Revises: 850c1a5add64
Create Date: 2025-07-05 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fedcba987654'
down_revision = '850c1a5add64'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('import_batch_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'import_batch', ['import_batch_id'], ['id'])


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('import_batch_id')
