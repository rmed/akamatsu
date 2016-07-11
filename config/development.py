# SQLALCHEMY_DATABASE_URI = "sqlite:///testdb.sqlite"
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/testdb.sqlite"
SECRET_KEY = "potato"
DEBUG = True

# Site name
SITENAME = "akamatsu"


# Active theme
THEME = "akamatsu"


# Footer
FOOTER_LEFT = "Copyright (C) akamatsu"
FOOTER_RIGHT = "Built with akamatsu"


# Disqus
DISQUS_SHORTNAME = ""


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


# Flask-User
USER_APP_NAME               = SITENAME
USER_ENABLE_EMAIL           = True
USER_ENABLE_REGISTRATION    = False
USER_ENABLE_FORGOT_PASSWORD = True

USER_CHANGE_PASSWORD_TEMPLATE = "akamatsu/dashboard/flask_user/change_password.html"
USER_FORGOT_PASSWORD_TEMPLATE = "akamatsu/dashboard/flask_user/forgot_password.html"
USER_LOGIN_TEMPLATE           = "akamatsu/dashboard/flask_user/login.html"
USER_RESET_PASSWORD_TEMPLATE  = "akamatsu/dashboard/flask_user/reset_password.html"

USER_CHANGE_PASSWORD_URL      = '/dashboard/profile/change-password'
USER_EMAIL_ACTION_URL         = '/dashboard/users/email/<id>/<action>'
USER_FORGOT_PASSWORD_URL      = '/dashboard/forgot-password'
USER_LOGIN_URL                = '/dashboard/login'
USER_LOGOUT_URL               = '/dashboard/logout'
USER_RESET_PASSWORD_URL       = '/dashboard/reset-password/<token>'

USER_AFTER_CHANGE_PASSWORD_ENDPOINT = 'dashboard.profile_edit'
USER_AFTER_FORGOT_PASSWORD_ENDPOINT = 'user.login'
USER_AFTER_LOGIN_ENDPOINT           = 'dashboard.home'
USER_AFTER_RESET_PASSWORD_ENDPOINT  = 'dashboard.home'
USER_UNAUTHORIZED_ENDPOINT          = 'dashboard.home'

USER_PASSWORD_HASH = 'sha512_crypt'


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

# Waffle Conf
WAFFLE_CONFS = {
    "SITENAME": {
        "desc": "Site name",
        "default": "akamatsu"
    },

    "FOOTER_LEFT": {
        "desc": "Left footer",
        "default": ""
    },

    "FOOTER_RIGHT": {
        "desc": "Right footer",
        "default": ""
    },

    "DISQUS_SHORTNAME": {
        "desc": "Disqus shortname",
        "default": ""
    },

    "SOCIAL": {
        "desc": "Social links",
        "default": []
    },

    "NAVBAR": {
        "desc": "Navigation bar",
        "default": []
    },

    "ALLOWED_EXTENSIONS": {
        "desc": "Allowed file extensions",
        "default": set()
    },

    "HUMANS_TXT": {
        "desc": "Text for humans.txt resource",
        "default": ""
    },

    "ROBOTS_TXT": {
        "desc": "Text for robots.txt resource",
        "default": ""
    }
}

# WAFFLE_MULTIPROC = True
