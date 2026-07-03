"""Guard against pyproject.toml / kumiho.__version__ drift.

A release that bumps one but not the other is otherwise invisible: the
publish workflow only checks the git tag against pyproject.toml, never
against the runtime __version__ string (used in User-Agent headers and
by dependents like kumiho-memory).
"""

from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

import kumiho


def test_version_matches_pyproject() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "python" / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    pyproject_version = data["project"]["version"]

    assert kumiho.__version__ == pyproject_version, (
        f"kumiho.__version__ ({kumiho.__version__!r}) does not match "
        f"pyproject.toml's version ({pyproject_version!r}) — bump both "
        "together in kumiho/__init__.py and pyproject.toml."
    )
