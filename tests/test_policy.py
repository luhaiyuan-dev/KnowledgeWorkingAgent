from app.auth.policy import PolicyEngine
from app.core.schemas import UserContext


def test_guest_has_limited_tools() -> None:
    policy = PolicyEngine()
    guest = UserContext(roles=["guest"])
    assert policy.can_use_tool(guest, "calculator")
    assert not policy.can_use_tool(guest, "data_query")


def test_admin_can_use_registered_tools() -> None:
    policy = PolicyEngine()
    admin = UserContext(roles=["admin"])
    assert policy.can_use_tool(admin, "future_enterprise_tool")
