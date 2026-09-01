"""HybitCertificate: signed attestation of dataset integrity."""

from __future__ import annotations

from dataclasses import dataclass

from .signing import sign_bytes, verify_bytes


@dataclass
class HybitCertificate:
    """
    An attestation that a named issuer vouches for a dataset seal.

    sign_with used to build the payload and then sign `list(payload[:18])` —
    the first eighteen bytes, reinterpreted as a hybit vector. Any subject and
    issuer summing to eighteen characters pushed the dataset seal entirely
    outside the signed range, so two certificates attesting different seals
    produced identical signatures. The seal is the one field a certificate
    exists to bind, so the payload is now signed whole.
    """

    subject: str
    issuer: str
    dataset_seal: str
    signature: bytes = b""

    def payload(self) -> bytes:
        """The exact bytes covered by the signature."""
        return f"{self.subject}:{self.issuer}:{self.dataset_seal}".encode("utf-8")

    def sign_with(self, key: bytes) -> bytes:
        """Sign the whole payload and store the result."""
        self.signature = sign_bytes(self.payload(), key)
        return self.signature

    def verify_with(self, key: bytes) -> bool:
        """True if the stored signature covers this certificate's fields."""
        if not self.signature:
            return False
        return verify_bytes(self.payload(), key, self.signature)
