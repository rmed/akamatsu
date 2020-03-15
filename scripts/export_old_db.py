# -*- coding: utf-8 -*-

"""Old database schema export script.

Use this script to export Akamatsu 1.x database records to a JSON file which
can then be imported by Akamatsu 2.x.

Modify database connection accordingly.
"""

import json
import sys

import records


NEW_ROLES = ('administrator', 'editor', 'blogger')

QUERY_USERS = 'SELECT * FROM users'
QUERY_USER_ROLES = (
    'SELECT ro.name FROM roles ro '
    'JOIN user_roles ur ON ro.id=ur.role_id '
    'WHERE ur.user_id=:user_id'
)
QUERY_PAGES = 'SELECT * FROM pages'
QUERY_POSTS = (
    'SELECT p.*, u.username FROM posts p '
    'JOIN users u ON u.id=p.author_id'
)
QUERY_POST_TAGS = (
    'SELECT t.name FROM tags t '
    'JOIN post_tags pt ON pt.tag_id=t.id '
    'WHERE pt.post_id=:post_id'
)
QUERY_UPLOADS = 'SELECT * FROM uploads'



def export(db, output='./backup_akamatsu.json'):
    result = {
        'users': [],
        'pages': [],
        'posts': [],
        'uploads': []
    }

    out = open(output, 'w', encoding='utf-8')

    # Backup users
    for r in db.query(QUERY_USERS):
        user = {
            'username': r['username'],
            'password': r['password'],
            'reset_password_token': r['reset_password_token'],
            'email': r['email'],
            'is_active': r['is_enabled'],
            'first_name': r['first_name'],
            'last_name': r['last_name'],
            'personal_bio': r['personal_bio'],
            'notify_login': r['notify_login'],
            'roles': []
        }

        # Roles
        for role in db.query(QUERY_USER_ROLES, user_id=r['id']):
            if role['name'] == 'admin':
                user['roles'].append('administrator')

            elif role['name'] in NEW_ROLES:
                user['roles'].append(role['name'])


        out.write(json.dumps({'entity': 'user', 'data': user})+'\n')


    # Backup pages
    for r in db.query(QUERY_PAGES):
        page = {
            'title': r['title'],
            'mini': r['mini'],
            'route': r['route'],
            'custom_head': r['custom_head'],
            'content': r['content'],
            'is_published': r['is_published'],
            'comments_enabled': r['comments_enabled'],
            'ghosted': None, # Should be route
            'last_updated': r['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Shim
        if r['ghost']:
            page['content'] = '[GHOST: {}]\n\n{}'.format(
                r['ghost'],
                page['content']
            )


        out.write(json.dumps({'entity': 'page', 'data': page})+'\n')

    # Backup posts
    for r in db.query(QUERY_POSTS):
        post = {
            'title': r['title'],
            'slug': r['slug'],
            'content': r['content'],
            'is_published': r['is_published'],
            'comments_enabled': r['comments_enabled'],
            'last_updated': r['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'authors': [r['username'],],
            'ghosted': None, # Should be slug
            'tags': []
        }

        # Shim
        if r['ghost']:
            post['content'] = '[GHOST: {}]\n\n{}'.format(
                r['ghost'],
                post['content']
            )

        # Tags
        for tag in db.query(QUERY_POST_TAGS, post_id=r['id']):
            post['tags'].append(tag['name'])


        out.write(json.dumps({'entity': 'post', 'data': post})+'\n')

    # Backup uploads
    for r in db.query(QUERY_UPLOADS):
        upload = {
            'path': r['path'],
            'description': r['description'],
            'mime': 'UNKOWN',
            'uploaded_at': r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        }

        out.write(json.dumps({'entity': 'upload', 'data': upload})+'\n')


    out.close()


def main():
    if len(sys.argv) != 3:
        print('Usage: export_old_db.py <DB_URI> <OUT>')
        return

    db = records.Database(sys.argv[1])
    out_path = sys.argv[2]

    export(db, out_path)


if __name__ == '__main__':
    main()
