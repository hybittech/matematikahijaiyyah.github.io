"""Authorship attribution must be identical everywhere it appears.

The name of record travels through source code, documentation, a proprietary
LICENSE, patent release declarations, certificates, and release manifests. Each
of those is edited by hand at some point, and a name that drifts in one of them
is invisible until someone reads that file — which, for a legal instrument, may
be long after it matters.

These tests pin every occurrence to the canonical form in AUTHORS.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

import pytest

ROOT = Path(__file__).resolve().parents[2]

CANONICAL_NAME = "Maulana Amratulloh"
CANONICAL_ROLE = "Inventor & Chief Architect"
CANONICAL_KEY_ID = "MA-SIG"
INSTITUTION = "Hijaiyyah Mathematics Computational Laboratory (HMCL)"
DATASET_SEAL = "f82d385917ffe32ae2b5711409b1341e90934c52172ae9d0fa68888e3b9c51c8"

# Directories that are vendored, generated, or otherwise not ours to police.
SKIP_DIRS = {
    ".git", "node_modules", "dist", ".vite", "__pycache__",
    ".venv", ".venv2", ".venv-mac", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "three.js-master", "build",
}
SKIP_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".ico", ".ttf", ".woff",
                 ".woff2", ".zip", ".rom", ".vvp", ".vcd", ".pyc", ".bin"}


def repo_text_files() -> List[Path]:
    """Every text file in the repo we are responsible for."""
    out: List[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if "egg-info" in str(path):          # regenerated from pyproject.toml
            continue
        out.append(path)
    return out


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


# ── the canonical record itself ──────────────────────────────────

def test_authors_file_exists_and_declares_the_canonical_form() -> None:
    text = read(ROOT / "AUTHORS")
    assert CANONICAL_NAME in text
    assert CANONICAL_ROLE in text
    assert INSTITUTION in text


def test_notice_file_exists_and_carries_attribution() -> None:
    text = read(ROOT / "NOTICE")
    assert CANONICAL_NAME in text
    assert CANONICAL_ROLE in text
    assert DATASET_SEAL in text, "NOTICE must cite the canonical dataset seal"


# ── no superseded name may survive anywhere ──────────────────────

# Case-sensitive, and the given name alone is not enough: "firman" is an
# ordinary Indonesian word (as in "Allah berfirman"), so matching it loosely
# flags devotional prose as an authorship defect.
SUPERSEDED = re.compile(r"Firman\s+Arief|Hidayatullah")


def test_no_superseded_author_name_remains() -> None:
    offenders = [
        str(p.relative_to(ROOT))
        for p in repo_text_files()
        if p.name != Path(__file__).name and SUPERSEDED.search(read(p))
    ]
    assert not offenders, f"superseded author name still present in: {offenders}"


# ── the canonical spelling must not drift ────────────────────────

# Any "Maulana …" that is not exactly the canonical name is a drifted variant
# (extra letters, dropped letters, different transliteration).
MAULANA_ANY = re.compile(r"Maulana\s+[A-Za-z]+")


def test_no_variant_spelling_of_the_canonical_name() -> None:
    bad = []
    for path in repo_text_files():
        if path.name == Path(__file__).name:
            continue
        for match in MAULANA_ANY.finditer(read(path)):
            if match.group(0) != CANONICAL_NAME:
                bad.append(f"{path.relative_to(ROOT)}: {match.group(0)!r}")
    assert not bad, f"variant spelling of the name of record: {bad}"


# ── legal instruments carry name and role ────────────────────────

LEGAL_DOCS = [
    "LICENSE",
    "NOTICE",
    "AUTHORS",
    "Matematika Hijaiyyah/OFFICIAL_PATENT_RELEASE/PATENT_RELEASE_DECLARATION_ID.md",
    "Matematika Hijaiyyah/OFFICIAL_PATENT_RELEASE/PATENT_RELEASE_DECLARATION_EN.md",
    "Matematika Hijaiyyah/OFFICIAL_PATENT_RELEASE/README.md",
    "release/HL-18E-v1.0/PATENT_RELEASE.md",
]


@pytest.mark.parametrize("relpath", LEGAL_DOCS)
def test_legal_document_names_the_inventor(relpath: str) -> None:
    path = ROOT / relpath
    if not path.exists():                                     # pragma: no cover
        pytest.skip(f"{relpath} not present")
    assert CANONICAL_NAME in read(path), f"{relpath} does not name the inventor"


def test_license_states_the_role() -> None:
    assert CANONICAL_ROLE in read(ROOT / "LICENSE")


# ── signing key id ───────────────────────────────────────────────

# The key id is derived from the name of record, so it drifts for the same
# reason the name does — and it appears in signature blocks that are read as
# provenance. "FAH-SIG" carried the superseded initials.
SUPERSEDED_KEY_ID = "FAH-SIG"

KEY_ID_SITES = [
    "LICENSE",
    "CHANGELOG.md",
    "src/hijaiyyah/gui/tabs/release.py",
]


@pytest.mark.parametrize("relpath", KEY_ID_SITES)
def test_signature_key_id_is_canonical(relpath: str) -> None:
    text = read(ROOT / relpath)
    assert SUPERSEDED_KEY_ID not in text, f"{relpath} still carries {SUPERSEDED_KEY_ID}"
    assert CANONICAL_KEY_ID in text, f"{relpath} does not carry {CANONICAL_KEY_ID}"


def test_release_tab_key_id_constant() -> None:
    from hijaiyyah.gui.tabs.release import AUTHOR_KEY_ID, AUTHOR_NAME

    assert AUTHOR_KEY_ID == CANONICAL_KEY_ID
    assert AUTHOR_NAME == CANONICAL_NAME


# ── machine-readable records carry name and role ─────────────────

CERTIFICATES = [
    ("Matematika Hijaiyyah/OFFICIAL_PATENT_RELEASE/CERTIFICATE.json", "inventor"),
    ("release/HL-18E-v1.0/CERTIFICATE.json", "author"),
    ("release/HL-18E-v1.0/MANIFEST.json", "author"),
]


@pytest.mark.parametrize("relpath,key", CERTIFICATES)
def test_certificate_records_name_and_role(relpath: str, key: str) -> None:
    path = ROOT / relpath
    if not path.exists():                                     # pragma: no cover
        pytest.skip(f"{relpath} not present")
    doc = json.loads(read(path))
    assert doc.get(key) == CANONICAL_NAME, f"{relpath}: {key} drifted"
    assert doc.get(f"{key}_role") == CANONICAL_ROLE, f"{relpath}: {key}_role drifted"


# ── package metadata ─────────────────────────────────────────────

def test_package_author_matches() -> None:
    from hijaiyyah import __author__

    assert __author__ == CANONICAL_NAME


def test_pyproject_author_matches() -> None:
    try:
        import tomllib
    except ModuleNotFoundError:                               # pragma: no cover
        pytest.skip("tomllib requires Python 3.11+")
    data = tomllib.loads(read(ROOT / "pyproject.toml"))
    names = [a.get("name") for a in data["project"]["authors"]]
    assert CANONICAL_NAME in names, f"pyproject authors: {names}"
