"""Guard against a test directory existing that no workflow collects.

This is the invariant kumiho-SDKs#153 was filed about. `python/tests/` held 21
files — including the pyproject/__version__ drift guard and an MCP edge-ontology
guard written specifically to catch a regression — and never ran once, because
both sdk-ci.yml and sdk-publish.yml invoke pytest with
`working-directory: python/python`, which resolves `tests/` to
`python/python/tests/`. Nothing failed; the files simply were not collected, so
nobody noticed for months. The 0.12.1 fix had to write a *second* copy of a test
that already existed, under the directory CI could see.

A missing test that looks present is worse than an absent one, and the failure
mode is silent by construction — no red build announces it. So assert the
layout: every directory under `python/` that contains test files must be one CI
actually runs. Adding a new one is fine; wiring it into a workflow and listing
it here is the price.
"""

from pathlib import Path

import pytest

# python/python/tests/ -> python/python -> python
PYTHON_ROOT = Path(__file__).resolve().parents[2]

# Directories holding pytest files, each mapped to the workflow job that runs
# them. Keep in step with .github/workflows/sdk-ci.yml; sdk-publish.yml gates
# the PyPI upload on the kumiho suite only.
COLLECTED_TEST_DIRS = {
    "python/tests": "sdk-ci.yml: python (working-directory: python/python)",
    "kumiho-cli/tests": "sdk-ci.yml: python-cli (working-directory: python/kumiho-cli)",
}


pytestmark = pytest.mark.skipif(
    not (PYTHON_ROOT / "python" / "pyproject.toml").exists(),
    reason="not running from a source checkout; there is no layout to inspect",
)


def _relative(path: Path) -> str:
    return path.relative_to(PYTHON_ROOT).as_posix()


def test_every_test_directory_is_collected_by_ci() -> None:
    found = {
        _relative(p.parent)
        for p in PYTHON_ROOT.rglob("test_*.py")
        if ".venv" not in p.parts
        and "build" not in p.parts
        and "site-packages" not in p.parts
    }

    orphaned = sorted(found - set(COLLECTED_TEST_DIRS))
    assert not orphaned, (
        "These directories under python/ contain tests that no CI job runs: "
        + ", ".join(orphaned)
        + ". Either wire them into .github/workflows/sdk-ci.yml and add them to "
        "COLLECTED_TEST_DIRS here, or delete them. A directory that looks like a "
        "test suite and never runs is the failure kumiho-SDKs#153 describes."
    )


def test_collected_test_directories_still_exist() -> None:
    """The other direction: this list must not rot into fiction either."""
    missing = sorted(
        name for name in COLLECTED_TEST_DIRS if not (PYTHON_ROOT / name).is_dir()
    )
    assert not missing, (
        "COLLECTED_TEST_DIRS names directories that no longer exist: "
        + ", ".join(missing)
        + ". Drop them here and from the workflow job that referenced them."
    )
