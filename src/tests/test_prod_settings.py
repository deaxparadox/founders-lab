import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from prod_env import VALID

SRC = Path(__file__).resolve().parents[1]
PROBE = (
    "import json; from backend.settings import prod as m;"
    "print(json.dumps({'debug': m.DEBUG, 'hosts': m.ALLOWED_HOSTS, 'cors': m.CORS_ALLOWED_ORIGINS,"
    " 'cors_all': m.CORS_ALLOW_ALL_ORIGINS, 'csrf': m.CSRF_TRUSTED_ORIGINS,"
    " 'jwt': m.SIMPLE_JWT['SIGNING_KEY'], 'secret': m.SECRET_KEY, 'hsts': m.SECURE_HSTS_SECONDS,"
    " 'ssl_redirect': m.SECURE_SSL_REDIRECT, 'cookies': [m.SESSION_COOKIE_SECURE, m.CSRF_COOKIE_SECURE],"
    " 'proxy': m.SECURE_PROXY_SSL_HEADER}))"
)
REQUEST = (
    "import django; django.setup();"
    "from django.test import Client;"
    "r = Client().get('/admin/login/', HTTP_HOST='api.example.com'{extra});"
    "print(r.status_code, r.get('Location', ''))"
)


def run(args, **env):
    full_env = {**os.environ, "PYTHONPATH": str(SRC), "DJANGO_SETTINGS_MODULE": "backend.settings.prod", **VALID, **env}
    return subprocess.run([sys.executable, *args], cwd=SRC, env=full_env, capture_output=True, text=True)


def test_prod_loads_with_hardened_values():
    result = run(["-c", PROBE])
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["debug"] is False
    assert data["hosts"] == ["api.example.com", "www.example.com"]
    assert data["cors"] == ["https://app.example.com"]
    assert data["cors_all"] is False
    assert data["csrf"] == ["https://api.example.com"]
    assert data["jwt"] == VALID["JWT_SIGNING_KEY"] != data["secret"]
    assert data["hsts"] == 3600
    assert data["ssl_redirect"] is True
    assert data["cookies"] == [True, True]
    assert data["proxy"] == ["HTTP_X_FORWARDED_PROTO", "https"]


def test_deployment_check_has_none_of_the_flagged_security_warnings():
    result = run(["manage.py", "check", "--deploy"])
    output = result.stdout + result.stderr
    for code in ["security.W004", "security.W008", "security.W009", "security.W012", "security.W016", "security.W018"]:
        assert code not in output, output


def test_plain_http_is_redirected_to_https():
    result = run(["-c", REQUEST.format(extra="")])
    assert result.stdout.split()[0] == "301", result.stdout + result.stderr
    assert result.stdout.split()[1].startswith("https://")


def test_request_marked_https_by_the_proxy_is_served_without_redirect():
    result = run(["-c", REQUEST.format(extra=", HTTP_X_FORWARDED_PROTO='https'")])
    assert result.stdout.split()[0] == "200", result.stdout + result.stderr


@pytest.mark.parametrize("name", list(VALID))
def test_missing_required_variable_stops_startup_and_names_it(name):
    result = run(["-c", PROBE], **{name: ""})
    assert result.returncode != 0
    assert f"{name} is required" in result.stderr


@pytest.mark.parametrize(
    "env, reason",
    [
        ({"SECRET_KEY": "django-insecure-" + VALID["SECRET_KEY"]}, "SECRET_KEY must not"),
        ({"SECRET_KEY": "short"}, "SECRET_KEY must be at least 50"),
        ({"JWT_SIGNING_KEY": VALID["SECRET_KEY"]}, "JWT_SIGNING_KEY must differ"),
        ({"ALLOWED_HOSTS": "*"}, "ALLOWED_HOSTS must not contain"),
        ({"ALLOWED_HOSTS": "api.example.com,*"}, "ALLOWED_HOSTS must not contain"),
        ({"CORS_ALLOWED_ORIGINS": "http://app.example.com"}, "CORS_ALLOWED_ORIGINS must be https"),
        ({"CORS_ALLOWED_ORIGINS": "app.example.com"}, "CORS_ALLOWED_ORIGINS must be https"),
        ({"CSRF_TRUSTED_ORIGINS": "HTTP://api.example.com"}, "CSRF_TRUSTED_ORIGINS must be https"),
    ],
    ids=["insecure-prefix", "short-key", "same-jwt-key", "star-host", "star-in-list", "http-cors", "no-scheme", "http-csrf"],
)
def test_insecure_values_are_rejected_with_the_specific_reason(env, reason):
    result = run(["-c", PROBE], **env)
    assert result.returncode != 0
    assert reason in result.stderr


def test_origin_scheme_check_ignores_case_and_surrounding_spaces():
    result = run(["-c", PROBE], CORS_ALLOWED_ORIGINS=" HTTPS://app.example.com , https://b.example.com ")
    assert result.returncode == 0, result.stderr
