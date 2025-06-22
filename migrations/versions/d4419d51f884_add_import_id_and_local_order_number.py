"""add import_id and local_order_number

Revision ID: d4419d51f884
Revises: 00dad933315d
Create Date: 2025-06-22 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4419d51f884'
down_revision = '00dad933315d'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('import_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('local_order_number', sa.Integer(), nullable=True))

def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('local_order_number')
        batch_op.drop_column('import_id')
