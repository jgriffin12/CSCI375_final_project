from app.services.auth_service import AuthService


class LoginController:
    """
    Controller for login-related requests.

    The controller acts as the middle layer between the Flask routes
    and the business logic in AuthService.
    """

    def __init__(self) -> None:
        # Create the auth service that performs the real login and MFA work.
        self.auth_service = AuthService()

    def login_request(self, data: dict) -> dict:
        """
        Handle an incoming login request.

        The controller extracts relevant fields from the input dictionary
        and forwards them to the authentication service.
        """
        username = data.get("username", "")
        password = data.get("password", "")
        return self.auth_service.authenticate(username, password)

    def verify_mfa_request(self, data: dict) -> dict:
        """
        Handle an incoming MFA verification request.

        The controller extracts the username and MFA code and asks
        the authentication service to verify the second factor.
        """
        username = data.get("username", "")
        code = data.get("code", "")
        return self.auth_service.verify_mfa(username, code)

    def logout_request(self, data: dict) -> dict:
        """
        Handle logout requests.

        Right now this is only a placeholder response.
        Later it can clear session data or revoke a token.
        """
        username = data.get("username", "")
        return {"status": "success", "message": f"{username} logged out"}