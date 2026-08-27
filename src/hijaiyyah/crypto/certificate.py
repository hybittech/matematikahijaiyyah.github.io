"""HybitCertificate: signed attestation of dataset integrity."""

from dataclasses import dataclass

from .signing import sign


@dataclass
class HybitCertificate:
    subject: str
    issuer: str
    dataset_seal: str
    signature: bytes = b""

    def sign_with(self, key: bytes):
        payload = f"{self.subject}:{self.issuer}:{self.dataset_seal}".encode()
        self.signature = sign(list(payload[:18]), key)
