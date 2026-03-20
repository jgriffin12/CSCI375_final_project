from abc import ABC, abstractmethod


class MFAStrategy(ABC):
    """
    Abstract base class for MFA strategies.

    This is the Strategy Pattern.
    Different MFA methods implement the same interface so the auth service
    can use them interchangeably.
    """

    @abstractmethod
    def send_code(self, user) -> None:
        """Send or generate the MFA code for the user."""
        pass

    @abstractmethod
    def verify_code(self, user, code: str) -> bool:
        """Return True only when the submitted code is valid."""
        pass


class EmailOTPStrategy(MFAStrategy):
    """
    MFA strategy that simulates sending a one-time password by email.
    """

    def send_code(self, user) -> None:
        # Placeholder behavior. Later this could send a real email.
        print(f"Sending email OTP to {user.email}")

    def verify_code(self, user, code: str) -> bool:
        # Placeholder verification.
        # Later this should compare against a generated, time-limited code.
        return code == "123456"


class TOTPStrategy(MFAStrategy):
    """
    MFA strategy for time-based one-time passwords.

    This is another interchangeable implementation of MFAStrategy.
    """

    def send_code(self, user) -> None:
        # TOTP typically does not send a code directly.
        # Instead, the user reads it from an authenticator app.
        print(f"TOTP ready for user {user.username}")

    def verify_code(self, user, code: str) -> bool:
        # Placeholder verification for the prototype.
        return code == "654321"