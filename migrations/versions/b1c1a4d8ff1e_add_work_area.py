"""add work area table

Revision ID: b1c1a4d8ff1e
Revises: a5d7000c64c3
Create Date: 2025-07-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b1c1a4d8ff1e'
down_revision = 'a5d7000c64c3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'work_area',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('geojson', sa.Text(), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
    )


def downgrade():
    op.drop_table('work_area')
