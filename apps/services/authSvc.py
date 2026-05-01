"""Authentication service for registration, login, and MFA."""

import os
from typing import Any

from apps.repositories.userRepo import UserRepository
from apps.security.passHash import PasswordHasher
from apps.services.auditLogger import AuditLogger
from apps.services.mfaSvc import MFAService


class AuthService:
    """Service responsible for registration, login, MFA, and audit logging."""

    def __init__(self) -> None:
        """Create authentication service dependencies."""
        self.user_repository = UserRepository()
        self.password_hasher = PasswordHasher()
        self.mfa_service = MFAService()
        self.audit_logger = AuditLogger()

    def _get_mfa_method(self) -> str:
        """Return the configured MFA method."""
        return os.getenv("MFA_METHOD", "email").strip().lower() or "email"

    def register_user(
        self,
        username: str,
        password: str,
        role: str,
        email: str,
    ) -> dict[str, Any]:
        """Register a user and write the result to the audit log."""
        if not username or not password or not role or not email:
            self.audit_logger.log_event(
                "registration_missing_fields",
                username or "unknown",
                "failure",
            )
            return {
                "status": "error",
                "message": "Username, password, role, and email are required.",
            }

        existing_user = self.user_repository.find_by_username(username)

        if existing_user is not None:
            self.audit_logger.log_event(
                "registration_duplicate_username",
                username,
                "failure",
            )
            return {
                "status": "error",
                "message": "Username already exists.",
            }

        try:
            self.user_repository.create_user(
                username=username,
                password=password,
                role=role,
                email=email,
            )
        except ValueError as error:
            self.audit_logger.log_event(
                "registration_failed",
                username,
                "failure",
            )
            return {
                "status": "error",
                "message": str(error),
            }

        self.audit_logger.log_event(
            "registration_success",
            username,
            "success",
        )

        return {
            "status": "success",
            "message": "Account created. You can now log in.",
            "username": username,
            "role": role,
        }

    def authenticate(
        self,
        username: str,
        password: str,
        role: str,
    ) -> dict[str, Any]:
        """Authenticate a user, send MFA, and write the result to the audit log."""
        user = self.user_repository.find_by_username(username)

        if user is None:
            self.audit_logger.log_event(
                "login_unknown_user",
                username,
                "failure",
            )
            return {
                "status": "error",
                "message": "Invalid username or password.",
            }

        if user.role != role:
            self.audit_logger.log_event(
                "login_role_mismatch",
                username,
                "failure",
            )
            return {
                "status": "error",
                "message": "Selected role does not match this user.",
            }

        if not self.password_hasher.verify_password(
            password,
            user.password_hash,
        ):
            self.audit_logger.log_event(
                "login_bad_password",
                username,
                "failure",
            )
            return {
                "status": "error",
                "message": "Invalid username or password.",
            }

        method = self._get_mfa_method()
        self.mfa_service.send_mfa_code(user, method)

        self.audit_logger.log_event(
            "login_mfa_sent",
            username,
            "success",
        )

        return {
            "status": "pending",
            "message": f"Login successful. MFA code sent using {method}.",
            "username": username,
            "role": role,
        }

    def verify_mfa(self, username: str, code: str) -> dict[str, Any]:
        """Verify MFA and write the result to the audit log."""
        user = self.user_repository.find_by_username(username)

        if user is None:
            self.audit_logger.log_event(
                "mfa_unknown_user",
                username,
                "failure",
            )
            return {
                "status": "error",
                "message": "User not found.",
            }

        method = self._get_mfa_method()
        verified = self.mfa_service.verify_mfa_code(user, code, method)

        if not verified:
            self.audit_logger.log_event(
                "mfa_failed",
                username,
                "failure",
            )
            return {
                "status": "error",
                "message": "Invalid MFA code.",
            }

        self.audit_logger.log_event(
            "mfa_success",
            username,
            "success",
        )

        return {
            "status": "success",
            "message": "MFA verified. Login complete.",
            "username": username,
            "role": user.role,
        }

    def logout(self, username: str) -> dict[str, str]:
        """Log out a user and write the action to the audit log."""
        if not username:
            self.audit_logger.log_event(
                "logout_missing_username",
                "unknown",
                "failure",
            )
            return {
                "status": "error",
                "message": "Username is required.",
            }

        self.audit_logger.log_event(
            "logout",
            username,
            "success",
        )

        return {
            "status": "success",
            "message": f"{username} logged out.",
        }
