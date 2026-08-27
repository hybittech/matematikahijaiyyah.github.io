"""Core layer: Master Table, codex types, guards, and constants."""

from .codex_entry import CodexEntry
from .constants import H28_ALPHABET, V14_SLOTS, V18_SLOTS
from .exceptions import (
    EBNFSemanticError,
    GuardViolation,
    HijaiyyahError,
    SealMismatch,
)
from .exomatrix import build_exomatrix
from .guards import guard_check, guard_detail
from .master_table import MASTER_TABLE, MasterTable
from .rom import pack_rom, unpack_rom
