"""
The package version is declared in three places that no build step reconciles.

pyproject.toml drove the wheel, src/hijaiyyah/version.py drove everything that
imports the package, and hom-gui/package.json drove the published site — and
they had already drifted (1.0.0 vs 1.2.0 vs 1.2.0) with nothing to catch it.

The dataset identifier is deliberately *not* tied to these: __dataset_release__
names the sealed Master Table document and moves independently of the software.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from hijaiyyah.version import __dataset_release__, __release__, __version__

ROOT = Path(__file__).resolve().parents[2]


def _pyproject_version() -> str:
    with open(ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


def _package_json_version() -> str:
    with open(ROOT / "hom-gui" / "package.json", encoding="utf-8") as f:
        return json.load(f)["version"]


def test_pyproject_matches_version_module() -> None:
    assert _pyproject_version() == __version__, (
        f"pyproject.toml={_pyproject_version()} but version.py={__version__}"
    )


def test_gui_package_matches_version_module() -> None:
    assert _package_json_version() == __version__, (
        f"hom-gui/package.json={_package_json_version()} but version.py={__version__}"
    )


def test_release_tag_carries_the_software_version() -> None:
    """__release__ is the software tag, so it must track __version__."""
    major_minor = ".".join(__version__.split(".")[:2])
    assert f"v{major_minor}" in __release__, (
        f"__release__={__release__} does not carry version {major_minor}"
    )


def test_dataset_release_is_the_sealed_identifier() -> None:
    """
    The sealed dataset is fixed by the canonical document and must not be
    dragged along when the software version moves.
    """
    assert __dataset_release__ == "HM-28-v.1.0-HC18D"

    with open(ROOT / "data" / "hm28.json", encoding="utf-8") as f:
        assert json.load(f)["release_id"] == __dataset_release__

    with open(ROOT / "data" / "hm28_manifest.json", encoding="utf-8") as f:
        assert json.load(f)["dataset"] == __dataset_release__
