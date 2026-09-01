"""Shared test fixtures for all test modules."""

import pytest

from hijaiyyah.core.codex_entry import CodexEntry
from hijaiyyah.core.master_table import MASTER_TABLE, MasterTable
from hijaiyyah.language.evaluator import HCEvaluator


@pytest.fixture
def table() -> MasterTable:
    return MASTER_TABLE


@pytest.fixture
def all_entries(table):
    return list(table.all_entries())


@pytest.fixture
def evaluator() -> HCEvaluator:
    return HCEvaluator()


@pytest.fixture
def hm(evaluator) -> dict:
    return evaluator.globals.get("hm")


@pytest.fixture
def ba(table) -> CodexEntry:
    return table.get_by_char("ب")


@pytest.fixture
def jim(table) -> CodexEntry:
    return table.get_by_char("ج")


@pytest.fixture
def haa(table) -> CodexEntry:
    return table.get_by_char("هـ")


@pytest.fixture
def alif(table) -> CodexEntry:
    return table.get_by_char("ا")
