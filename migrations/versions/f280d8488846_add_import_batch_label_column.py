"""add import_batch_label column to orders

Revision ID: f280d8488846
Revises: c5e0d1a9b4e3
Create Date: 2025-06-24 15:28:26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f280d8488846'
down_revision = 'c5e0d1a9b4e3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('orders')]
    with op.batch_alter_table('orders', schema=None) as batch_op:
        if 'import_batch_label' not in columns:
            batch_op.add_column(sa.Column('import_batch_label', sa.String(), nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('orders')]
    with op.batch_alter_table('orders', schema=None) as batch_op:
        if 'import_batch_label' in columns:
            batch_op.drop_column('import_batch_label')
