"""Add import_batch_label column

Revision ID: 9b3b39c284f0
Revises: f280d8488846
Create Date: 2025-07-20 00:00:00
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '9b3b39c284f0'
down_revision = 'f280d8488846'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS import_batch_label VARCHAR(128);")


def downgrade():
    op.execute("ALTER TABLE orders DROP COLUMN IF EXISTS import_batch_label;")

