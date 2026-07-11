"""Tamper-evident audit record primitives."""

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class AuditRecord:
    event: str
    packet_id: str
    payload: dict[str, Any]
    previous_hash: str = ""

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            asdict(self),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def digest(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()
