import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1]
PROBE = (
    "import importlib, json, sys;"
    "m = importlib.import_module(sys.argv[1]);"
    "db = m.DATABASES['default'];"
    "print(json.dumps({'urlconf': m.ROOT_URLCONF, 'media': str(m.MEDIA_ROOT),"
    " 'db': db['NAME'], 'apps': m.INSTALLED_APPS[-2:]}))"
)


def run(args, **env):
    full_env = {**os.environ, "PYTHONPATH": str(SRC), **env}
    return subprocess.run([sys.executable, *args], cwd=SRC, env=full_env, capture_output=True, text=True)


@pytest.mark.parametrize("module", ["dev", "prod", "test"])
def test_each_settings_module_loads_with_the_shared_values(module):
    result = run(["-c", PROBE, f"backend.settings.{module}"])
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["urlconf"] == "backend.urls"
    assert data["media"].endswith("src/media")
    assert data["apps"] == ["ai.apps.AiConfig", "bubbleio.apps.BubbleioConfig"]


def test_test_settings_use_the_dedicated_test_database():
    result = run(["-c", PROBE, "backend.settings.test"])
    assert json.loads(result.stdout)["db"] == os.environ["TEST_DB_NAME"]


@pytest.mark.parametrize("module", ["dev", "prod"])
def test_dev_and_prod_use_the_main_database(module):
    result = run(["-c", PROBE, f"backend.settings.{module}"])
    assert json.loads(result.stdout)["db"] == os.environ["DBNAME"]


def test_test_settings_fail_without_a_test_database_name():
    result = run(["-c", PROBE, "backend.settings.test"], TEST_DB_NAME="")
    assert result.returncode != 0
    assert "TEST_DB_NAME is required" in result.stderr


def test_unknown_settings_module_fails_with_an_import_error():
    result = run(["-c", PROBE, "backend.settings.nope"])
    assert result.returncode != 0
    assert "ModuleNotFoundError" in result.stderr


@pytest.mark.parametrize(
    "args",
    [["manage.py", "check"], ["-c", "import backend.asgi"], ["-c", "import backend.wsgi"]],
    ids=["manage", "asgi", "wsgi"],
)
def test_entry_points_require_the_settings_module(args):
    result = run(args, DJANGO_SETTINGS_MODULE="")
    assert result.returncode != 0
    assert "DJANGO_SETTINGS_MODULE is required" in result.stderr
