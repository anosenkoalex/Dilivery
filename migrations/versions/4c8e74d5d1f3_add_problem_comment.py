"""add problem_comment to orders

Revision ID: 4c8e74d5d1f3
Revises: 8922a5ebcd01
Create Date: 2025-06-21 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4c8e74d5d1f3'
down_revision = '8922a5ebcd01'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('problem_comment', sa.Text()))

def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('problem_comment')
