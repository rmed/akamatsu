"""This file contains celery tasks."""

from akamatsu import celery
from flask_user.emails import send_email

@celery.task()
def async_mail(*args):
    """Send email asynchronously."""
    send_email(*args)
