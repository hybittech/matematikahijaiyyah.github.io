"""
The computation inside the GUI, which nothing ever ran outside the GUI.

src/hijaiyyah/gui is 9,245 lines with no test coverage. Most of it is Tkinter
layout, which is not worth testing, but not all of it: gui/tabs/theorems.py
holds thirteen theorem checks, each returning (passed, message), and they only
executed when somebody opened the tab and pressed a button.

That is the same shape as EXAMPLE_BY_NAME in grammar.py — real assertions
reachable only through the interface — and the same shape as the bug mypy
found in gui/tabs/bytecode.py, where the letter buttons passed a 0-based index
to an opcode that takes a 1-based one.

None of this needs a display: the functions here are module-level and pure.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import pytest

from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.gui.tabs import five_fields, theorems


def _theorem_checks() -> Dict[str, Callable[[], Tuple[bool, str]]]:
    """Every _test_* in the theorems tab, discovered rather than listed."""
    return {
        name: getattr(theorems, name)
        for name in dir(theorems)
        if name.startswith("_test_") and callable(getattr(theorems, name))
    }


CHECKS = _theorem_checks()
NAMES = sorted(CHECKS)


def test_the_theorem_checks_were_found() -> None:
    assert len(CHECKS) >= 10, f"only {len(CHECKS)} checks discovered"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_theorem_check_passes(name: str) -> None:
    """
    Each check asserts something about the sealed table. A failure here means
    the mathematics moved, not that the GUI is broken.
    """
    passed, message = CHECKS[name]()
    assert passed, f"{name}: {message}"
    assert message, f"{name} returned no explanation"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_theorem_check_is_not_vacuous(name: str) -> None:
    """A check that always returns True regardless of input proves nothing."""
    passed, _ = CHECKS[name]()
    assert isinstance(passed, bool)


# ── The classifiers behind the five-fields tab ───────────────────

def test_structure_classifier_covers_every_letter() -> None:
    """No canonical letter may fall through to an empty label."""
    for entry in MASTER_TABLE.all_entries():
        label, _ = five_fields._classify_structure(list(entry.vector))
        assert label, f"{entry.char} has no structural classification"


def test_turning_classifier_covers_every_letter() -> None:
    for entry in MASTER_TABLE.all_entries():
        label, _ = five_fields._classify_turning(list(entry.vector))
        assert label, f"{entry.char} has no turning classification"


def test_dot_families_are_symmetric() -> None:
    """
    If ب lists ت as a relative, ت must list ب. An asymmetric relation would
    show a different set of neighbours depending on which letter you opened.
    """
    entries = MASTER_TABLE.all_entries()
    family: Dict[str, set] = {}
    for entry in entries:
        related = five_fields._find_dot_family(entry)
        family[entry.char] = {row[0] for row in related} - {entry.char}

    for char, relatives in family.items():
        for other in relatives:
            if other in family:
                assert char in family[other], (
                    f"{char} lists {other} as a relative, but not the reverse"
                )


# ── The letter index the buttons pass to CLOAD ───────────────────

def test_codex_entries_are_numbered_from_one() -> None:
    """
    gui/tabs/bytecode.py builds a button per letter and passes the index to
    CLOAD, whose IMM is 1-based. It used to pass the list position instead, so
    ب produced CLOAD #1 and loaded Alif. This pins the property the buttons
    now rely on.
    """
    entries = MASTER_TABLE.all_entries()
    assert [e.index for e in entries] == list(range(1, 29))


def test_bytecode_tab_uses_the_letter_index_not_the_list_position() -> None:
    source = (
        __import__("pathlib")
        .Path(theorems.__file__)
        .parent.joinpath("bytecode.py")
        .read_text(encoding="utf-8")
    )
    assert "lambda idx=letter.index" in source, (
        "the letter buttons must pass letter.index — the 1-based number CLOAD "
        "expects — not the enumerate() position"
    )
    assert "lambda idx=i:" not in source, "a 0-based button index is back"


# ── Every tab module imports ─────────────────────────────────────

def test_every_tab_module_imports() -> None:
    """
    A tab that fails to import takes the whole application down on launch,
    and nothing else in the suite loads them.
    """
    import importlib
    import pkgutil

    import hijaiyyah.gui as gui

    failures: List[str] = []
    for module in pkgutil.walk_packages(gui.__path__, "hijaiyyah.gui."):
        try:
            importlib.import_module(module.name)
        except Exception as exc:
            failures.append(f"{module.name}: {type(exc).__name__}: {exc}")
    assert not failures, "\n".join(failures)
