from .base import *  # noqa

DEBUG = True

INTERNAL_IPS = ["127.0.0.1"]

SECRET_KEY = "django-insecure-txsqk2w&9@$v_xo2pc0129!30@)khf3y%*+p62y1(kd#_500$a"

# DATABASE SETTINGS
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


try:
    from local_settings import * # noqa
except ImportError:
    pass
