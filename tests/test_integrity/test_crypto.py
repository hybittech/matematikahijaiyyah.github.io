"""
The crypto module, which had no tests at all.

Two faults, one of them a real weakness.

HybitCertificate.sign_with built its payload and then signed
`list(payload[:18])` — the first eighteen bytes, reinterpreted as a hybit
vector. Any subject and issuer summing to eighteen characters pushed the
dataset seal entirely outside the signed range, so two certificates attesting
different seals produced identical signatures. Binding the seal is the only
reason the certificate exists.

And vectors were encoded as `bytes(v[0:18])`, one byte per component, which
raises the moment a component leaves 0..255. That is not exotic: a string
integral of roughly 110 letters already reaches Θ̂ = 210, and any difference
vector can be negative.
"""

from __future__ import annotations

import pytest

from hijaiyyah.algebra.aggregametric import string_integral
from hijaiyyah.core.master_table import MASTER_TABLE
from hijaiyyah.crypto.certificate import HybitCertificate
from hijaiyyah.crypto.hashing import (
    VectorRangeError,
    canonical_digest,
    encode_vector,
    sha256_bytes,
    sha256_vector,
)
from hijaiyyah.crypto.signing import sign, sign_bytes, verify, verify_bytes

KEY = b"a-test-key-not-a-secret"


def _letter(char: str) -> list:
    entry = MASTER_TABLE.get_by_char(char)
    assert entry is not None
    return list(entry.vector)


# ── Certificates ─────────────────────────────────────────────────

def test_certificates_with_different_seals_get_different_signatures() -> None:
    """
    The failure that prompted these tests. Subject and issuer here total
    eighteen characters, so under the old encoding the seal was never signed.
    """
    real = HybitCertificate("HMCL-Release-Auth", "HMCL", "HM-28-v.1.0-HC18D")
    forged = HybitCertificate("HMCL-Release-Auth", "HMCL", "FORGED-SEAL-VALUE")

    real.sign_with(KEY)
    forged.sign_with(KEY)

    assert real.signature != forged.signature


def test_a_signature_does_not_transfer_to_another_seal() -> None:
    real = HybitCertificate("HMCL-Release-Auth", "HMCL", "HM-28-v.1.0-HC18D")
    signature = real.sign_with(KEY)

    forged = HybitCertificate(
        "HMCL-Release-Auth", "HMCL", "FORGED-SEAL-VALUE", signature
    )
    assert forged.verify_with(KEY) is False


@pytest.mark.parametrize("field", ["subject", "issuer", "dataset_seal"])
def test_every_field_is_covered_by_the_signature(field: str) -> None:
    cert = HybitCertificate("subject-value", "issuer-value", "seal-value")
    cert.sign_with(KEY)

    setattr(cert, field, "tampered")
    assert cert.verify_with(KEY) is False, f"{field} is outside the signature"


def test_verification_rejects_the_wrong_key() -> None:
    cert = HybitCertificate("s", "i", "seal")
    cert.sign_with(KEY)
    assert cert.verify_with(b"another-key") is False


def test_unsigned_certificate_does_not_verify() -> None:
    assert HybitCertificate("s", "i", "seal").verify_with(KEY) is False


# ── Vector encoding ──────────────────────────────────────────────

def test_canonical_letters_encode() -> None:
    for entry in MASTER_TABLE.all_entries():
        assert len(encode_vector(list(entry.vector))) == 18 * 4


def test_a_large_string_integral_encodes() -> None:
    """`bytes(v)` raised here; roughly 110 letters is enough to pass 255."""
    codex = string_integral("بسم الله الرحمن الرحيم " * 12)["cod18"]
    assert max(codex) > 255
    assert sha256_vector(codex)


def test_a_negative_component_encodes() -> None:
    """Difference vectors are signed, and used to be unhashable."""
    assert sha256_vector([-5] + [0] * 17)


def test_encoding_distinguishes_sign() -> None:
    assert sha256_vector([5] + [0] * 17) != sha256_vector([-5] + [0] * 17)


def test_encoding_distinguishes_every_position() -> None:
    """A component moving between slots must change the digest."""
    base = [0] * 18
    digests = set()
    for i in range(18):
        v = list(base)
        v[i] = 7
        digests.add(sha256_vector(v))
    assert len(digests) == 18


def test_out_of_range_component_is_rejected_clearly() -> None:
    with pytest.raises(VectorRangeError, match="signed 32-bit"):
        encode_vector([2**40] + [0] * 17)


def test_short_vector_is_rejected_rather_than_padded() -> None:
    with pytest.raises(VectorRangeError, match="expected at least 18"):
        encode_vector([1, 2, 3])


def test_non_integer_component_is_rejected() -> None:
    with pytest.raises(VectorRangeError, match="expected int"):
        encode_vector([1.5] + [0] * 17)


# ── Signing ──────────────────────────────────────────────────────

def test_sign_and_verify_round_trip() -> None:
    ba = _letter("ب")
    assert verify(ba, KEY, sign(ba, KEY))


def test_verify_rejects_a_different_vector() -> None:
    assert not verify(_letter("س"), KEY, sign(_letter("ب"), KEY))


def test_verify_rejects_a_different_key() -> None:
    ba = _letter("ب")
    assert not verify(ba, b"other-key", sign(ba, KEY))


def test_byte_signing_round_trip() -> None:
    assert verify_bytes(b"payload", KEY, sign_bytes(b"payload", KEY))
    assert not verify_bytes(b"payload ", KEY, sign_bytes(b"payload", KEY))


# ── Digests ──────────────────────────────────────────────────────

def test_canonical_digest_ignores_key_order() -> None:
    assert canonical_digest({"a": 1, "b": 2}) == canonical_digest({"b": 2, "a": 1})


def test_canonical_digest_notices_a_value_change() -> None:
    assert canonical_digest({"a": 1}) != canonical_digest({"a": 2})


def test_sha256_bytes_matches_hashlib() -> None:
    import hashlib

    assert sha256_bytes(b"abc") == hashlib.sha256(b"abc").hexdigest()
