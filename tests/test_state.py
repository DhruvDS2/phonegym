from phonegym.core.state import PhoneState


def test_state_hash_is_deterministic() -> None:
    a = PhoneState(apps={"messages": {"threads": []}})
    b = PhoneState(apps={"messages": {"threads": []}})
    assert a.state_hash() == b.state_hash()


def test_state_hash_changes_with_state() -> None:
    a = PhoneState()
    b = PhoneState(clock_ms=1)
    assert a.state_hash() != b.state_hash()
