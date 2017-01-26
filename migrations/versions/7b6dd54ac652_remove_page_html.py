"""Remove page html

Revision ID: 7b6dd54ac652
Revises: 5ab395c487b6
Create Date: 2017-01-26 11:39:45.339306

"""

# revision identifiers, used by Alembic.
revision = '7b6dd54ac652'
down_revision = '5ab395c487b6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('pages') as batch_op:
        batch_op.drop_column('is_html')
        batch_op.drop_column('use_layout_header')


def downgrade():
    with op.batch_alter_table('pages') as batch_op:
            batch_op.add_column(
                sa.Column('is_html', sa.Boolean(), nullable=True)
            )
            batch_op.add_column(
                sa.Column('use_layout_header', sa.Boolean(), nullable=True)
            )
