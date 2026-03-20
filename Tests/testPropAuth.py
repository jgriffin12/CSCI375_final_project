from hypothesis import given, strategies as st
from app.services.auth_service import AuthService


@given(st.text(min_size=1), st.text(min_size=1))
def test_authenticate_returns_known_status(username: str, password: str):
    """
    Property-based test.

    Instead of checking only a few hardcoded inputs, Hypothesis generates
    many input combinations automatically. This helps test edge cases.

    Here we verify that the authenticate method always returns a recognized status.
    """
    service = AuthService()
    result = service.authenticate(username, password)
    assert result["status"] in {"failure", "pending"}