"""Release sync: manifest loading and verification."""

import json
import os


class SyncSynchronizer:
    def __init__(self, release_dir: str = "release/HL-18E-v1.0"):
        self.release_dir = release_dir
        self.manifest: dict = {}

    def load_manifest(self) -> dict:
        path = os.path.join(self.release_dir, "MANIFEST.json")
        if os.path.exists(path):
            with open(path) as f:
                self.manifest = json.load(f)
        return self.manifest

    def verify(self, sha256: str) -> bool:
        return bool(self.manifest.get("sha256", "") == sha256)
