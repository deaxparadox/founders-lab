import os

from dotenv import load_dotenv


def require_settings_module() -> None:
    """Load .env, then fail loudly if DJANGO_SETTINGS_MODULE is not set (no silent default)."""
    load_dotenv()
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        raise RuntimeError(
            "DJANGO_SETTINGS_MODULE is required, e.g. backend.settings.dev (set it in .env)"
        )


def require_env(name: str) -> str:
    """Return the trimmed value of a required environment variable, or fail naming it."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required (see .env.example)")
    return value


def require_env_list(name: str) -> list[str]:
    """Return a required comma-separated variable as a de-duplicated list, or fail naming it."""
    items = [item.strip() for item in os.environ.get(name, "").split(",")]
    result = list(dict.fromkeys(item for item in items if item))
    if not result:
        raise RuntimeError(f"{name} is required (see .env.example)")
    return result
