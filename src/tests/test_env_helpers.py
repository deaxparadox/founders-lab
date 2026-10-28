import pytest

from backend.env import require_env, require_env_list


def test_require_env_returns_the_trimmed_value(monkeypatch):
    monkeypatch.setenv("X_VAR", "  value ")
    assert require_env("X_VAR") == "value"


@pytest.mark.parametrize("raw", [None, "", "   ", "\t\n"], ids=["unset", "empty", "spaces", "whitespace"])
def test_require_env_fails_naming_the_variable(monkeypatch, raw):
    monkeypatch.delenv("X_VAR", raising=False)
    if raw is not None:
        monkeypatch.setenv("X_VAR", raw)
    with pytest.raises(RuntimeError, match="X_VAR is required"):
        require_env("X_VAR")


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("a.com", ["a.com"]),
        ("a.com,b.com", ["a.com", "b.com"]),
        (" a.com , b.com ,", ["a.com", "b.com"]),
        ("a.com,a.com,b.com", ["a.com", "b.com"]),
        ("münchen.example,例え.jp", ["münchen.example", "例え.jp"]),
        (",".join(f"h{i}.example" for i in range(500)), [f"h{i}.example" for i in range(500)]),
    ],
    ids=["single", "two", "spaces-trailing-comma", "duplicates", "unicode", "oversized"],
)
def test_require_env_list_splits_trims_and_dedupes(monkeypatch, raw, expected):
    monkeypatch.setenv("X_LIST", raw)
    assert require_env_list("X_LIST") == expected


@pytest.mark.parametrize("raw", [None, "", " , ,", ","], ids=["unset", "empty", "only-separators", "comma"])
def test_require_env_list_fails_when_nothing_is_left(monkeypatch, raw):
    monkeypatch.delenv("X_LIST", raising=False)
    if raw is not None:
        monkeypatch.setenv("X_LIST", raw)
    with pytest.raises(RuntimeError, match="X_LIST is required"):
        require_env_list("X_LIST")
