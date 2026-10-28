"""Settings used by pytest: the dev values, on the dedicated test database."""
import os

from .dev import *  # noqa: F401,F403

_test_db_name = os.getenv("TEST_DB_NAME")
if not _test_db_name:
    raise RuntimeError("TEST_DB_NAME is required to run tests (see .env.example)")

DATABASES["default"]["NAME"] = _test_db_name  # noqa: F405
DATABASES["default"]["TEST"] = {"NAME": _test_db_name}  # noqa: F405
