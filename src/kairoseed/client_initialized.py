"""KAIROSEED client initialization boundary.

Initialization establishes a client identity and session context only.
It does not authenticate the client and does not grant authorization.
"""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ClientIdentity:
    """Stable client identifier paired with a unique session identifier."""

    client_id: str
    session_id: UUID


@dataclass(frozen=True)
class InitializedClient:
    """Result of client initialization.

    ``initialized`` is intentionally not an authentication or authorization
    signal. Downstream authentication and governance layers must verify those
    properties independently.
    """

    identity: ClientIdentity
    initialized: bool = True


def initialize_client(client_id: str) -> InitializedClient:
    """Initialize a client with a validated identifier and fresh session ID."""
    if not isinstance(client_id, str) or not client_id.strip():
        raise ValueError("client_id must be a non-empty string")

    return InitializedClient(
        identity=ClientIdentity(
            client_id=client_id.strip(),
            session_id=uuid4(),
        )
    )
