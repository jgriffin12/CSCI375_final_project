from app.services.auth_service import AuthService


def test_authenticate_invalid_user():
    """
    Unknown usernames should fail authentication.
    """
    service = AuthService()
    result = service.authenticate("unknown", "password123")
    assert result["status"] == "failure"


def test_authenticate_valid_user_pending_mfa():
    """
    Valid username/password should not immediately log in the user.
    It should move the flow into the MFA step.
    """
    service = AuthService()
    result = service.authenticate("alice", "password123")
    assert result["status"] == "pending"


def test_verify_mfa_success():
    """
    A valid MFA code should complete authentication successfully.
    """
    service = AuthService()
    result = service.verify_mfa("alice", "123456")
    assert result["status"] == "success"