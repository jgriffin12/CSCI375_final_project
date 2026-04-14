from apps.security.mfaFactory import MFAFactory


class MFAService:
    """
    Service responsible for coordinating MFA operations.

    This service hides the details of strategy creation from the rest of
    the application. AuthService can simply ask MFAService to send or
    verify a second factor.
    """

    def __init__(self) -> None:
        self.mfa_factory = MFAFactory()

    def send_mfa_code(self, user, method: str = "email") -> None:
        """
        Create the correct MFA strategy and send the code or challenge.
        """
        strategy = self.mfa_factory.create_strategy(method)
        strategy.send_code(user)

    def verify_mfa_code(self, user, code: str, method: str = "email") -> bool:
        """
        Create the correct MFA strategy and verify the submitted code.
        """
        strategy = self.mfa_factory.create_strategy(method)
        return strategy.verify_code(user, code)