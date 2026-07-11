"""Policy enforcement point: deny by default."""

from .authorization import GovernanceAuthorizationToken


def authorize_execution(token: GovernanceAuthorizationToken | None) -> bool:
    """Return True only when presented with an active PASS token."""
    return bool(token and token.is_active())
