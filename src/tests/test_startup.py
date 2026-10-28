import os
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
STARTUP = (
    "import django, sys; django.setup();"
    "print('llm-stack-imported' if 'services.clients' in sys.modules else 'clean')"
)


def test_django_starts_without_openai_or_pinecone_keys():
    env = {
        **os.environ,
        "PYTHONPATH": str(SRC),
        "DJANGO_SETTINGS_MODULE": "backend.settings.dev",
        "OPENAI_API_KEY": "",
        "PINECONE_API_KEY": "",
        "PINECONE_INDEX_NAME": "",
    }
    result = subprocess.run([sys.executable, "-c", STARTUP], cwd=SRC, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "clean"
