"""Remove Flask-WaffleConf

Revision ID: aede8cd191c8
Revises: 7b6dd54ac652
Create Date: 2018-01-14 11:48:02.200428

"""

# revision identifiers, used by Alembic.
revision = 'aede8cd191c8'
down_revision = '7b6dd54ac652'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('waffleconfs')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('waffleconfs',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('key', sa.VARCHAR(length=255), nullable=False),
    sa.Column('value', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    # ### end Alembic commands ###