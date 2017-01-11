# ![akamatsu](logo.png)

My small CMS made in Flask

  * [Installation](#installation)
  * [Dashboard](#dashboard)
  * [Configuration variables](#configuration-variables)
  * [Database migrations](#database-migrations)
  * [Acknowledgements](#acknowledgements)


## Installation

It is recommended to use `virtualenv` to managed the dependencies for akamatsu:

```
$ virtualenv -p python3 /path/to/venv
$ . /path/to/venv/bin/activate
$ pip install -r requirements.txt
```

## Dashboard

Through the dashboard you can create new pages and blog posts. It can be
accessed through the `/dashboard` route.

You can specify roles for existing users:

- `admin`: can manage blog, pages, files and users
- `editor`: can manage pages
- `blogger`: can manage their own blog posts
- `uploader`: can manage their own files (future)
- `superblogger`: can manage all blog posts
- `superuploader`: can manage all files (future)

## Configuration variables

In development environment, the application loads the `config/development.py`
configuration file. However, in production environments you should provide the
path to your configuration file by means of the `AKAMATSU_CONFIG_FILE`
environment variable.

Below is a list of settings specific to the application (the rest of them
belong to Flask extensions).

**Note that most of them can be modified during runtime using the
Flask-WaffleConf extension through the dashboard**.

### `SITENAME`

This defines the name of the site used in several templates, defaults to
`'akamatsu'`.

### `THEME`

It is virtually possible to use other templates rather than the ones provided
by default. This can be achieved by placing custom templates in a directory
such as `templates/my_theme` and changing the value of `THEME` to `'my_theme'`.
This defaults to the `'akamatsu'` theme.

### `FOOTER_LEFT` and `FOOTER_RIGHT`

Content (html) that appears in the bottom left and right parts of the page in
the akamatsu templates.

### `DISQUS_SHORTNAME`

Shortname to enable Disqus comments in blog and pages.

### `HUMANS_TXT` and `ROBOTS_TXT`

Plain text content for the `/humans.txt` and `/robots.txt` pages.

### `UPLOAD_DIR`

Directory in which files will be uploaded. It should exist and be accessible to
the user executing the application.

### `UPLOAD_SERVING_ROUTE`

Route used to serve the files. The application does not actually serve the
files, so this setting is only used to create routes to files.

The recommended whay of serving files is to configure your web server to do so
automatically.

### `ALLOWED_EXTENSIONS`

File extensions that can be uplodaded to the server.

**This should be set through the dashboard**.

### `MAX_CONTENT_LENGTH`

Maximum filesize allowed. Note the default example:

```
16 * 1024 * 1024 = 16 MB
```

### `SOCIAL`

List that contains links, and the Entypo glyphs representing those links, shown
in the top right part of the page in the akamatsu theme.

**This should be set through the dashboard**.

### `NAVBAR`

List that contains links, and the text representing those links, shown in the
top bar of the akamatsu theme.

**This should be set through the dashboard**.

## Database migrations

Database versioning is done through `Flask-Migrate` / `alembic`. Note that the
first migration also creates a default administrator user with the email
`admin@example.com`. In order to override it, the migration should be preceded
by the `AKAMATSU_EMAIL` environment variable:

```
$ AKAMATSU_EMAIL=my@email.com python app.py db upgrade
```

This way, the user will be created using the email account provided and you
will be able to reset your password.

**Note that you need to configure Flask-Mail in order to use the password reset
functionality**.

## Acknowledgements

- [Entypo](http://entypo.com) by Daniel Bruce (Creative Commons BY-SA 4.0)
- [Fira](https://github.com/mozilla/Fira) by Mozilla (SIL OPEN FONT LICENSE
  Version 1.1)
- [highlight.js](https://highlightjs.org) by [highlight.js
  contributors](https://github.com/isagalaev/highlight.js/blob/master/AUTHORS.en.txt) (BSD License)
- [Normalize.css](https://github.com/nercolas/normalize.css) by Nicolas
  Gallagher and Jonathan Neal (MIT License)
- [Simple-Grid](https://github.com/ThisIsDallas/Simple-Grid) by Dallas Bass
  (MIT License)
- [Zepto.js](http://zeptojs.com) by Thomas Fuchs (MIT License)
