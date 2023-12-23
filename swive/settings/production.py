import os
from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = [".needhamswive.com"]

# DATABASE SETTINGS
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# IMPORTANT!:
# You must keep this secret, you can store it in an
# environment variable and set it with:
# export SECRET_KEY="phil-dunphy98!-bananas12"
# https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/#secret-key
SECRET_KEY = os.environ['SECRET_KEY']

# WSGI SETTINGS
# https://docs.djangoproject.com/en/5.0/ref/settings/#wsgi-application
WSGI_APPLICATION = 'swive.wsgi.application'


try:
    from local_settings import * # noqa
except ImportError:
    pass
