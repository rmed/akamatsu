"""Rewrite with new structure

Revision ID: b919bda38d42
Revises: aede8cd191c8
Create Date: 2020-01-12 14:19:44.789986

"""

# revision identifiers, used by Alembic.
revision = 'b919bda38d42'
down_revision = 'aede8cd191c8'

from alembic import op
import sqlalchemy as sa

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DummyUser(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String, nullable=False, unique=True)


class DummyPost(Base):
    __tablename__ = 'posts'

    id = sa.Column(sa.Integer, primary_key=True)
    author_id = sa.Column(sa.Integer)
    ghost = sa.Column(sa.String)
    ghosted_id = sa.Column(sa.Integer)
    timestamp = sa.Column(sa.DateTime)
    last_updated = sa.Column(sa.DateTime)


class DummyPage(Base):
    __tablename__ = 'pages'

    id = sa.Column(sa.Integer, primary_key=True)
    ghost = sa.Column(sa.String)
    ghosted_id = sa.Column(sa.Integer)
    timestamp = sa.Column(sa.DateTime)
    last_updated = sa.Column(sa.DateTime)


class UserPost(Base):
    __tablename__ = 'user_posts'

    user_id = sa.Column(sa.Integer, primary_key=True)
    post_id = sa.Column(sa.Integer, primary_key=True)


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    with op.batch_alter_table('posts') as batch_op:
        batch_op.add_column(sa.Column('ghosted_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_updated', sa.DateTime(), nullable=True))

    # Migrate post data
    for post in session.query(DummyPost):
        if post.ghost:
            slug = post.ghost.split('/')

            if len(slug) > 1:
                slug = slug[-1]
                ghost = session.query(DummyPost).filter(DummyPost.slug==slug).first()

                if ghost:
                    post.ghosted_id = ghost.id

        post.last_updated = post.timestamp

    session.commit()



    # Create post-user intermediate table
    op.create_table('user_posts',
        sa.Column('user_id', sa.Integer(), nullable=True, primary_key=True),
        sa.Column('post_id', sa.Integer(), nullable=True, primary_key=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], name='fk_user_posts_post'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_user_posts_user')
    )

    # Migrate author data
    for post in session.query(DummyPost):
        session.add(UserPost(user_id=post.author_id, post_id=post.id))

    session.commit()


    with op.batch_alter_table('pages') as batch_op:
        batch_op.add_column(sa.Column('ghosted_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_updated', sa.DateTime(), nullable=True))

    # Migrate page data
    for page in session.query(DummyPage):
        if page.ghost:
            ghost = session.query(DummyPage).filter(DummyPage.route==page.ghost).first()

            if ghost:
                page.ghosted_id = ghost.id

        page.last_updated = page.timestamp

    session.commit()


    with op.batch_alter_table('pages') as batch_op:
        batch_op.alter_column('mini',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=False)

        op.create_foreign_key(None, 'pages', 'pages', ['ghosted_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')

        batch_op.drop_column('pages', 'slug')
        batch_op.op.drop_column('pages', 'base_route')
        batch_op.op.drop_column('pages', 'is_root')
        batch_op.op.drop_column('pages', 'ghost')
        batch_op.op.drop_column('pages', 'timestamp')


    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.create_foreign_key(None, 'posts', 'posts', ['ghosted_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')


    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_column('author_id')
        batch_op.drop_column('ghost')
        batch_op.drop_column('timestamp')


    with op.batch_alter_table('uploads') as batch_op:
        batch_op.alter_column('description',
                   existing_type=sa.TEXT(),
                   nullable=True)

    op.drop_constraint(None, 'user_roles', type_='foreignkey')
    op.drop_constraint(None, 'user_roles', type_='foreignkey')
    op.create_foreign_key('fk_user_roles_user', 'user_roles', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_user_roles_role', 'user_roles', 'roles', ['role_id'], ['id'])

    with op.batch_alter_table('user_roles') as batch_op:
        batch_op.drop_column('id')

    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('reset_expiration', sa.DateTime(), nullable=True))
        batch_op.alter_column('reset_password_token',
                   existing_type=sa.VARCHAR(length=100),
                   nullable=True)
        batch_op.drop_column('is_enabled')
        batch_op.drop_column('confirmed_at')
        batch_op.drop_column('first_name')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('personal_bio', sa.VARCHAR(length=1024), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.VARCHAR(length=50), nullable=False))
    op.add_column('users', sa.Column('confirmed_at', sa.DATETIME(), nullable=True))
    op.add_column('users', sa.Column('is_enabled', sa.BOOLEAN(), nullable=False))
    op.alter_column('users', 'reset_password_token',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_column('users', 'reset_expiration')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'fist_name')
    op.add_column('user_roles', sa.Column('id', sa.INTEGER(), nullable=False))
    op.drop_constraint('fk_user_roles_role', 'user_roles', type_='foreignkey')
    op.drop_constraint('fk_user_roles_user', 'user_roles', type_='foreignkey')
    op.create_foreign_key(None, 'user_roles', 'roles', ['role_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(None, 'user_roles', 'users', ['user_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.alter_column('uploads', 'description',
               existing_type=sa.TEXT(),
               nullable=False)
    op.add_column('posts', sa.Column('timestamp', sa.DATETIME(), nullable=True))
    op.add_column('posts', sa.Column('ghost', sa.VARCHAR(length=512), nullable=True))
    op.add_column('posts', sa.Column('author_id', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.create_foreign_key(None, 'posts', 'users', ['author_id'], ['id'])
    op.drop_column('posts', 'last_updated')
    op.drop_column('posts', 'ghosted_id')
    op.add_column('pages', sa.Column('timestamp', sa.DATETIME(), nullable=True))
    op.add_column('pages', sa.Column('ghost', sa.VARCHAR(length=512), nullable=True))
    op.add_column('pages', sa.Column('is_root', sa.BOOLEAN(), nullable=True))
    op.add_column('pages', sa.Column('base_route', sa.VARCHAR(length=255), nullable=False))
    op.add_column('pages', sa.Column('slug', sa.VARCHAR(length=255), nullable=False))
    op.drop_constraint(None, 'pages', type_='foreignkey')
    op.alter_column('pages', 'mini',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.drop_column('pages', 'last_updated')
    op.drop_column('pages', 'ghosted_id')
    op.drop_table('user_posts')
    # ### end Alembic commands ###
