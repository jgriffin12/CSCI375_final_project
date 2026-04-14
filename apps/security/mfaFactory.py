from apps.security.mfaStrategies import EmailOTPStrategy, TOTPStrategy, MFAStrategy


class MFAFactory:
    """
    Factory responsible for creating the correct MFA strategy object.

    This is the Factory Method pattern.
    The rest of the application does not need to know the exact class name
    ahead of time. It only asks for the strategy type it wants.
    """

    def create_strategy(self, method: str) -> MFAStrategy:
        """
        Return the correct MFA strategy implementation based on the method name.
        """
        if method == "email":
            return EmailOTPStrategy()

        if method == "totp":
            return TOTPStrategy()

        # Raise an error for unsupported methods so bugs fail clearly.
        raise ValueError(f"Unsupported MFA method: {method}")