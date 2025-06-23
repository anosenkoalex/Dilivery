"""add import batch table and fk

Revision ID: e2b35c8f4c7a
Revises: a5d7000c64c3
Create Date: 2025-07-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e2b35c8f4c7a'
down_revision = 'a5d7000c64c3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'import_batch',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('import_batch_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'import_batch', ['import_batch_id'], ['id'])


def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('import_batch_id')
    op.drop_table('import_batch')
