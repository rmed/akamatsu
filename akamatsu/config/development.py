"""Development configuration."""
import os

SQLALCHEMY_DATABASE_URI = "sqlite:////%s" % os.path.join(os.getcwd(), "testdb.sqlite")
SECRET_KEY = "potato"
DEBUG = True

# Site name
SITENAME = "akamatsu"


# Active theme
THEME = "akamatsu"


# Footer
FOOTER_LEFT = "Copyright (C) akamatsu"
FOOTER_RIGHT = "Built with akamatsu"


# Comments
COMMENT_SYSTEM = "disqus" # 'isso' or 'disqus'

# When COMMENT_SYSTEM is "disqus"
DISQUS_SHORTNAME = ""

# When COMMENT_SYSTEM is "isso" (all values are strings!)
ISSO_URL = ""
ISSO_REPLY_SELF = "true"
ISSO_REQUIRE_AUTHOR = "true"
ISSO_REQUIRE_EMAIL = "true"
ISSO_VOTING = "false"


# humans.txt text
HUMANS_TXT = ""

# robots.txt text
ROBOTS_TXT = ""


# Anayltics (Piwik)
ANALYTICS = {}


# Uploads
UPLOAD_DIR = '/tmp'
UPLOAD_SERVING_ROUTE = '/tmp'
ALLOWED_EXTENSIONS = set()
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB


# Celery
USE_CELERY = False
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'


# Flask-User
USER_APP_NAME = SITENAME


# Flask-Mail
MAIL_SERVER = ""
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = ""
MAIL_USERNAME = ""
MAIL_PASSWORD = ""

# Social links
SOCIAL = [
    {
        "link": "https://github.com/rmed/akamatsu",
        "glyph": "github"
    },
]

# Navigation bar
NAVBAR = [
    {
        "link": "/",
        "text": "Home"
    },
    {
        "link": "/blog",
        "text": "Blog"
    },
]
