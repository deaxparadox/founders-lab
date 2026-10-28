"""Local development settings."""
from .base import *  # noqa: F401,F403

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-na5)h(vh)!gt4=%*--=&qgn1%c7qpp-p29ytl&d1^ux!8eli9z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS Settings
CORS_ALLOW_ALL_ORIGINS: bool = True
