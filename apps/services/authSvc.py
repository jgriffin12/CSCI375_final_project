from apps.repositories.userRepo import UserRepository
from apps.security.passHash import PasswordHasher
from apps.security.mfa_service import MFAService
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
        self.mfa_service = MFAService()
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

        # For this starter version, we accept either the literal classroom
        # password or a correctly hashed version if you populate it that way.
        password_matches = (
            password == "password123"
            or self.password_hasher.verify_password(password, user.password_hash)
        )

        if not password_matches:
            self.audit_logger.log_event("login_failed", username, "failure")
            return {"status": "failure", "message": "Invalid credentials"}

        self.mfa_service.send_mfa_code(user, method="email")
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

        if not self.mfa_service.verify_mfa_code(user, code, method="email"):
            self.audit_logger.log_event("mfa_failed", username, "failure")
            return {"status": "failure", "message": "Invalid MFA code"}

        self.audit_logger.log_event("login_success", username, "success")
        return {"status": "success", "message": "Login successful"}