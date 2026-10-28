"""Production settings. Everything secret or host-specific comes from the environment and is required."""
from backend.env import require_env, require_env_list

from .base import *  # noqa: F401,F403

SECRET_KEY = require_env("SECRET_KEY")
if SECRET_KEY.startswith("django-insecure-"):
    raise RuntimeError("SECRET_KEY must not be a django-insecure- key")
if len(SECRET_KEY) < 50:
    raise RuntimeError("SECRET_KEY must be at least 50 characters")

# Login tokens are signed with their own key, so a leaked SECRET_KEY cannot forge them.
JWT_SIGNING_KEY = require_env("JWT_SIGNING_KEY")
if JWT_SIGNING_KEY == SECRET_KEY:
    raise RuntimeError("JWT_SIGNING_KEY must differ from SECRET_KEY")
SIMPLE_JWT = {"SIGNING_KEY": JWT_SIGNING_KEY}

DEBUG = False

ALLOWED_HOSTS = require_env_list("ALLOWED_HOSTS")
if "*" in ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must not contain '*'")


def _https_origins(name: str) -> list[str]:
    origins = require_env_list(name)
    if not all(origin.lower().startswith("https://") for origin in origins):
        raise RuntimeError(f"{name} must be https:// origins")
    return origins


CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = _https_origins("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = _https_origins("CSRF_TRUSTED_ORIGINS")

# nginx ends TLS in front of Django and must send X-Forwarded-Proto (overwriting any client value).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# Start at one hour; raise once HTTPS is proven stable. Send HSTS from here or from nginx, not both.
SECURE_HSTS_SECONDS = 3600
