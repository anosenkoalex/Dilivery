"""add processed_rows

Revision ID: 8922a5ebcd01
Revises: 
Create Date: 2025-06-19 23:05:45.090821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8922a5ebcd01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('import_jobs', sa.Column('processed_rows', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('import_jobs', 'processed_rows')
