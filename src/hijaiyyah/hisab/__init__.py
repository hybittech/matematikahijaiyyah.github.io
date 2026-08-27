"""
HISAB — Hijaiyyah Inter-System Standard for Auditable Bridging.

Public API for the HISAB protocol.
"""

from .digest import (
    compute_digest,
    verify_digest,
)
from .protocol import (
    ALL_GUARDS_PASS,
    DIGEST_SIZE,
    GUARD_SIZE,
    HEADER_SIZE,
    MAGIC,
    NIBBLE_PAIRS,
    VERSION,
    FrameType,
    HisabFrame,
)
from .serialize import (
    deserialize_frame,
    deserialize_letter_payload,
    deserialize_string_payload,
    serialize_letter,
    serialize_matrix,
    serialize_string,
)
from .validate import (
    ValidationReport,
    ValidationResult,
    validate_frame,
)

__all__ = [
    "ALL_GUARDS_PASS",
    "DIGEST_SIZE",
    "GUARD_SIZE",
    "HEADER_SIZE",
    # Protocol
    "MAGIC",
    "NIBBLE_PAIRS",
    "VERSION",
    "FrameType",
    "HisabFrame",
    "ValidationReport",
    # Validation
    "ValidationResult",
    # Digest
    "compute_digest",
    "deserialize_frame",
    "deserialize_letter_payload",
    "deserialize_string_payload",
    # Serialization
    "serialize_letter",
    "serialize_matrix",
    "serialize_string",
    "validate_frame",
    "verify_digest",
]
