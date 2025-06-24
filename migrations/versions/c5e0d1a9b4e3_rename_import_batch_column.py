"""rename import_batch column to import_batch_label

Revision ID: c5e0d1a9b4e3
Revises: fedcba987654
Create Date: 2025-07-10 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c5e0d1a9b4e3'
down_revision = 'fedcba987654'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('import_batch', new_column_name='import_batch_label')


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('import_batch_label', new_column_name='import_batch')
