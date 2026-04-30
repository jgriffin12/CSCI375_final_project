"""Role-based access control service."""


class AccessControlService:
    """Service responsible for enforcing role-based access control.

    CJ Secure uses role-based permissions to control what each type of user
    can access after MFA is verified.

    Role behavior:
    - Providers can retrieve the assigned protected patient record.
    - Patients can only view their own patient dashboard message.
    - Admins can only review audit logs.
    """

    def __init__(self) -> None:
        """Create the role-to-permission mapping."""
        self.role_permissions: dict[str, set[str]] = {
            "provider": {"view_masked_record"},
            "patient": {"view_own_record"},
            "admin": {"review_logs"},
        }

    def is_authorized(self, user, action: str) -> bool:
        """Return True if the user's role is allowed to perform the action."""
        allowed_actions = self.role_permissions.get(user.role, set())
        return action in allowed_actions
