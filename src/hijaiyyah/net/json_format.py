"""HC18DC JSON format."""

import json

from ..core.guards import guard_check
from ..crypto.hashing import sha256_vector


def to_json(v: list, letter: str = "") -> str:
    return json.dumps(
        {
            "format": "HC18DC",
            "version": "1.0",
            "letter": letter,
            "v18": v,
            "guard": "PASS" if guard_check(v) else "FAIL",
            "hash": sha256_vector(v),
        },
        ensure_ascii=False,
        indent=2,
    )
