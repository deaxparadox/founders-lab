import pytest
from django.conf import settings
from django.db import connection
from django.db.backends.postgresql.base import DatabaseWrapper
from django.db.utils import OperationalError


@pytest.mark.django_db
def test_round_trip_uses_the_dedicated_test_database():
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        (name,) = cursor.fetchone()
    assert name == settings.DATABASES["default"]["TEST"]["NAME"]
    assert name != "founders_lab"


def test_unreachable_database_fails_with_a_clear_error(django_db_blocker):
    bad = {**settings.DATABASES["default"], "PORT": 1}
    wrapper = DatabaseWrapper(bad, "unreachable")
    with django_db_blocker.unblock(), pytest.raises(OperationalError, match="Connection refused"):
        wrapper.ensure_connection()
