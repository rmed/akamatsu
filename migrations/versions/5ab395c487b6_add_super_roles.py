"""Add super roles

Revision ID: 5ab395c487b6
Revises: 2e68dbfc7374
Create Date: 2017-01-10 22:18:05.948081

"""

# revision identifiers, used by Alembic.
revision = '5ab395c487b6'
down_revision = '2e68dbfc7374'

from alembic import op
import sqlalchemy as sa

def upgrade():
    roles_table = sa.sql.table(
        'roles',
        sa.sql.column('name', sa.String)
    )

    # Insert new roles
    op.bulk_insert(
        roles_table,
        [
            {'name': 'superblogger'},
            {'name': 'supereditor'},
            {'name': 'superuploader'},
        ]
    )

def downgrade():
    op.execute(
        "DELETE FROM roles WHERE name IN ('superblogger', 'supereditor', 'superuploader')"
    )
