"""
Documents that quote the synthesis report must quote the current one.

hcpu_synth_report.txt is written by hand from `yosys -s synth_hcpu.ys`, and
Bab III §10.1.3 and README.md both cite its figures. That is three copies of
one measurement, kept in step by memory — the shape behind every divergence
this project has had.

It had already gone wrong once. Bab III quoted 28,200 gates and ~113,000 um²
as measured results when the first column of the report headed them "Prior
estimate" and the caveats said no area figure could be derived at all. Then the
report itself went stale: it predated the memory rewrite, so its 480,795 cells
described a design that no longer existed while the book went on citing it.

Synthesis takes minutes, so this does not re-run it. It checks that every
figure the prose quotes is a figure the report actually contains.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Set

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "rtl" / "mpw" / "hcpu_synth_report.txt"
BAB_III = ROOT / "Hybit" / "Bab_III_Hybit_Paradigma_Komputasi_Ketiga.md"
README = ROOT / "README.md"

# Figures large enough to be a synthesis result rather than a section number.
_BIG_NUMBER = re.compile(r"\b(\d{1,3}(?:[.,]\d{3})+)\b")


def _figures(text: str) -> Set[int]:
    out: Set[int] = set()
    for match in _BIG_NUMBER.finditer(text):
        value = int(match.group(1).replace(".", "").replace(",", ""))
        if value >= 1000:
            out.add(value)
    return out


REPORT_TEXT = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
REPORT_FIGURES = _figures(REPORT_TEXT)


def test_the_report_exists_and_carries_figures() -> None:
    assert REPORT.exists(), f"missing {REPORT}"
    assert len(REPORT_FIGURES) >= 5, (
        f"only {len(REPORT_FIGURES)} figures parsed — the report format changed"
    )


@pytest.mark.parametrize(
    "path", [BAB_III, README], ids=["Bab III", "README"]
)
def test_quoted_synthesis_figures_appear_in_the_report(path: Path) -> None:
    """
    Every large number in the prose's synthesis section must be one the report
    contains. A figure that has drifted out of the report is a figure nobody
    measured.
    """
    text = path.read_text(encoding="utf-8")

    # Only the passage that discusses synthesis; the rest of both documents is
    # full of unrelated numbers.
    section = re.search(
        r"(hcpu_dataram|Sintesis generik)(.{0,2600})", text, re.S
    )
    assert section, f"{path.name} no longer has a synthesis passage"

    quoted = _figures(section.group(0))
    # The hand estimate this project has since superseded is quoted on purpose,
    # as the column it is compared against.
    allowed = REPORT_FIGURES | {28200, 113000}

    unknown = sorted(quoted - allowed)
    assert not unknown, (
        f"{path.name} quotes figures the report does not contain: {unknown}\n"
        "Either the report was regenerated and the prose was not updated, "
        "or the prose invented a number."
    )


def test_the_report_states_what_it_cannot_measure() -> None:
    """
    The caveat is the load-bearing part: generic gates yield no um² and no
    timing. Bab III once quoted a die area anyway.
    """
    lowered = REPORT_TEXT.lower()
    assert "no sky130 pdk is installed" in lowered
    assert "um^2" in lowered or "um²" in lowered


def test_bab_iii_still_withholds_the_die_area_claim() -> None:
    text = BAB_III.read_text(encoding="utf-8")
    assert "tidak dapat diturunkan" in text, (
        "§10.1.3 must keep saying the die area cannot be derived"
    )
    assert "ditahan" in text, "the MPW-readiness claim must stay withheld"


def test_the_rtl_assertion_count_is_quoted_correctly() -> None:
    """
    Bab III quotes the testbench total. Programme 8 took it from 204 to 205,
    and a stale figure here is the same class of drift as a stale cell count.
    """
    text = BAB_III.read_text(encoding="utf-8")
    match = re.search(r"\*\*(\d+) assertion PASS", text)
    assert match, "§10.1.3 no longer quotes an assertion count"

    quoted = int(match.group(1))
    breakdown = re.search(
        r"ROM (\d+), Guard (\d+), Codex ALU (\d+), HISAB (\d+), "
        r"integrasi _top-level_ (\d+)",
        text,
    )
    assert breakdown, "the per-testbench breakdown is missing"
    assert sum(int(g) for g in breakdown.groups()) == quoted, (
        "the quoted total does not match its own breakdown"
    )


def test_synthesis_artefacts_are_not_tracked() -> None:
    """
    The netlist and JSON are hundreds of megabytes and regenerate from the
    script. .gitignore lists them; this fails if that stops being true.
    """
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for artefact in ("rtl/mpw/hcpu_synth.json", "rtl/mpw/hcpu_synth_netlist.v"):
        assert artefact in ignored, f"{artefact} is no longer ignored"
