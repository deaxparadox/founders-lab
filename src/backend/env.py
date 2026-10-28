import os

from dotenv import load_dotenv


def require_settings_module() -> None:
    """Load .env, then fail loudly if DJANGO_SETTINGS_MODULE is not set (no silent default)."""
    load_dotenv()
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        raise RuntimeError(
            "DJANGO_SETTINGS_MODULE is required, e.g. backend.settings.dev (set it in .env)"
        )
