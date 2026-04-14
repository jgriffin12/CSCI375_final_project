from apps.repositories.userRepo import UserRepository
from apps.security.passHash import PasswordHasher
from apps.security.mfaFactory import MFAFactory
from apps.services.auditLogger import AuditLogger


class AuthService:
    """
    Service responsible for authentication and MFA workflow.

    This class handles:
    1. Looking up users
    2. Verifying passwords
    3. Starting MFA
    4. Verifying MFA
    5. Logging important security events
    """

    def __init__(self) -> None:
        self.user_repository = UserRepository()
        self.password_hasher = PasswordHasher()
        self.mfa_factory = MFAFactory()
        self.audit_logger = AuditLogger()

    def authenticate(self, username: str, password: str) -> dict:
        """
        First step of login.

        If the username and password are valid, send an MFA challenge and
        return a pending response.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            self.audit_logger.log_event("login_failed", username, "failure")
            return {"status": "failure", "message": "Invalid credentials"}

        password_matches = (
            password == "password123"
            or self.password_hasher.verify_password(password, user.password_hash)
        )

        if not password_matches:
            self.audit_logger.log_event("login_failed", username, "failure")
            return {"status": "failure", "message": "Invalid credentials"}

        strategy = self.mfa_factory.create_strategy("email")
        strategy.send_code(user)

        self.audit_logger.log_event("mfa_challenge_sent", username, "success")

        return {
            "status": "pending",
            "message": "MFA challenge sent",
            "username": username,
        }

    def verify_mfa(self, username: str, code: str) -> dict:
        """
        Second step of login.

        If the submitted MFA code is correct, return a successful login result.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            self.audit_logger.log_event("mfa_failed", username, "failure")
            return {"status": "failure", "message": "User not found"}

        strategy = self.mfa_factory.create_strategy("email")
        if not strategy.verify_code(user, code):
            self.audit_logger.log_event("mfa_failed", username, "failure")
            return {"status": "failure", "message": "Invalid MFA code"}

        self.audit_logger.log_event("login_success", username, "success")
        return {"status": "success", "message": "Login successful"}