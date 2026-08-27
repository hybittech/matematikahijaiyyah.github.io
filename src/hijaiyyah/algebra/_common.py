"""Common helper functions for algebraic operations."""

from typing import Any, List
from ..core.codex_entry import CodexEntry


def _v(h: Any) -> List[int]:
    """Extract vector list from CodexEntry or iterable."""
    return list(h.vector) if isinstance(h, CodexEntry) else list(h)


def _n2(v: List[int]) -> int:
    """Calculate squared norm of a vector."""
    return sum(x * x for x in v[:14])
