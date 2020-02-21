"""Base migration 2.0.0

Revision ID: 7cc292cfbb0a
Revises: None
Create Date: 2020-02-21 19:33:55.870010

"""

# revision identifiers, used by Alembic.
revision = '7cc292cfbb0a'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('pages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ghosted_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('mini', sa.String(length=50), nullable=False),
    sa.Column('route', sa.String(length=512), nullable=False),
    sa.Column('custom_head', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=True),
    sa.Column('comments_enabled', sa.Boolean(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ghosted_id'], ['pages.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('route')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ghosted_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('slug', sa.String(length=512), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=True),
    sa.Column('comments_enabled', sa.Boolean(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ghosted_id'], ['posts.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    roles_table = op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('uploads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(length=512), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('mime', sa.String(length=128), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('path')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('reset_password_token', sa.String(length=100), nullable=True),
    sa.Column('reset_expiration', sa.DateTime(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('personal_bio', sa.String(length=1024), nullable=True),
    sa.Column('notify_login', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('post_tags',
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='fk_post_tags_post'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name='fk_post_tags_tag'),
    sa.PrimaryKeyConstraint('post_id', 'tag_id')
    )
    op.create_table('user_posts',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='fk_user_posts_post'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_posts_user'),
    sa.PrimaryKeyConstraint('user_id', 'post_id')
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], name='fk_user_roles_role'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_roles_user'),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Insert default roles
    op.bulk_insert(
        roles_table,
        [
            {'id': 1, 'name': 'administrator'},
            {'id': 2, 'name': 'blogger'},
            {'id': 3, 'name': 'editor'}
        ]
    )


def downgrade():
    op.drop_table('user_roles')
    op.drop_table('user_posts')
    op.drop_table('post_tags')
    op.drop_table('users')
    op.drop_table('uploads')
    op.drop_table('tags')
    op.drop_table('roles')
    op.drop_table('posts')
    op.drop_table('pages')
