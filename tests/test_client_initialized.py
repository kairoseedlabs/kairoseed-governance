import pytest

from kairoseed.client_initialized import initialize_client


def test_initialize_client_establishes_identity_only() -> None:
    client = initialize_client("agent-01")

    assert client.initialized is True
    assert client.identity.client_id == "agent-01"
    assert client.identity.session_id is not None


def test_initialize_client_strips_client_id() -> None:
    client = initialize_client("  agent-01  ")

    assert client.identity.client_id == "agent-01"


@pytest.mark.parametrize("client_id", ["", "   ", None])
def test_initialize_client_rejects_invalid_identifier(client_id: object) -> None:
    with pytest.raises(ValueError):
        initialize_client(client_id)  # type: ignore[arg-type]


def test_initialization_does_not_expose_authorization() -> None:
    client = initialize_client("agent-01")

    assert not hasattr(client, "authorized")
    assert not hasattr(client, "authenticated")
