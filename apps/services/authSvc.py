"""Authentication service for login and MFA."""

from typing import Any

from apps.repositories.userRepo import UserRepository
from apps.security.passHash import PasswordHasher
from apps.services.mfaSvc import MFAService


class AuthService:
    """
    Service responsible for authentication.

    This class handles username/password login, starts MFA, and verifies
    MFA codes after the user enters the email code.
    """

    def __init__(self) -> None:
        """Create the dependencies needed for authentication."""
        self.user_repository = UserRepository()
        self.password_hasher = PasswordHasher()
        self.mfa_service = MFAService()

    def authenticate(
        self,
        username: str,
        password: str,
        role: str,
        email: str,
    ) -> dict[str, Any]:
        """
        Authenticate a user and send an MFA code by email.

        The email comes from the frontend and is used by the SendGrid
        MFA strategy.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {
                "status": "error",
                "message": "Invalid username or password.",
            }

        if user.role != role:
            return {
                "status": "error",
                "message": "Selected role does not match this user.",
            }

        if not self.password_hasher.verify_password(password, user.password_hash):
            return {
                "status": "error",
                "message": "Invalid username or password.",
            }

        # Add the frontend email to the user object so SendGrid knows
        # where to send the MFA code.
        user.email = email

        self.mfa_service.send_mfa_code(user, "email")

        return {
            "status": "pending",
            "message": "Login successful. MFA code sent to email.",
            "username": username,
            "role": role,
        }

    def verify_mfa(self, username: str, code: str) -> dict[str, Any]:
        """
        Verify the MFA code entered by the user.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {
                "status": "error",
                "message": "User not found.",
            }

        verified = self.mfa_service.verify_mfa_code(user, code, "email")

        if not verified:
            return {
                "status": "error",
                "message": "Invalid MFA code.",
            }

        return {
            "status": "success",
            "message": "MFA verified. Login complete.",
            "username": username,
            "role": user.role,
        }