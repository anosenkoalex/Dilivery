"""increase password_hash length

Revision ID: 00dad933315d
Revises: 4c8e74d5d1f3
Create Date: 2025-06-21 20:51:20.794097
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00dad933315d'
down_revision = '4c8e74d5d1f3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=128),
               type_=sa.String(length=512),
               existing_nullable=False)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=512),
               type_=sa.String(length=128),
               existing_nullable=False)
