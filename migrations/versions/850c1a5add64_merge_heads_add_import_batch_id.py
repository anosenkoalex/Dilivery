"""merge heads and ensure import_batch_id column exists"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '850c1a5add64'
down_revision = ('b1c1a4d8ff1e', 'e2b35c8f4c7a')
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('orders')]
    with op.batch_alter_table('orders', schema=None) as batch_op:
        if 'import_batch_id' not in columns:
            batch_op.add_column(sa.Column('import_batch_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(None, 'import_batch', ['import_batch_id'], ['id'])


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('orders')]
    with op.batch_alter_table('orders', schema=None) as batch_op:
        if 'import_batch_id' in columns:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_column('import_batch_id')
