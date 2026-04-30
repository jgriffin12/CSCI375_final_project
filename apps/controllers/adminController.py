"""Controller for admin-only audit log features."""

from typing import Any

from apps.repositories.userRepo import UserRepository
from apps.services.accessControlSvc import AccessControlService
from apps.services.auditLogger import AuditLogger


class AdminController:
    """Controller for admin-only features such as viewing audit logs."""

    def __init__(self) -> None:
        """Create controller dependencies."""
        self.user_repository = UserRepository()
        self.access_control_service = AccessControlService()
        self.audit_logger = AuditLogger()

    def _event_to_dict(self, event: Any) -> dict[str, Any]:
        """Convert an audit event object into dictionary format."""
        if hasattr(event, "to_dict"):
            return event.to_dict()

        return {
            "event_id": getattr(event, "event_id", None),
            "timestamp": str(getattr(event, "timestamp", "")),
            "event_type": getattr(event, "event_type", ""),
            "username": getattr(event, "username", ""),
            "status": getattr(event, "status", ""),
        }

    def get_audit_logs(self, username: str) -> dict[str, Any]:
        """Return structured audit logs for authorized admin users."""
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {"status": "failure", "message": "User not found"}

        if not self.access_control_service.is_authorized(user, "review_logs"):
            self.audit_logger.log_event("audit_access_denied", username, "failure")
            return {"status": "failure", "message": "Access denied"}

        self.audit_logger.log_event("audit_logs_viewed", username, "success")
        events = self.audit_logger.get_all_events()

        return {
            "status": "success",
            "logs": [self._event_to_dict(event) for event in events],
        }

    def get_audit_log_text(self, username: str) -> dict[str, str]:
        """Return readable audit log text for frontend display."""
        user = self.user_repository.find_by_username(username)

        if user is None:
            return {"status": "failure", "message": "User not found"}

        if not self.access_control_service.is_authorized(user, "review_logs"):
            self.audit_logger.log_event("audit_text_access_denied", username, "failure")
            return {"status": "failure", "message": "Access denied"}

        self.audit_logger.log_event("audit_text_viewed", username, "success")

        return {
            "status": "success",
            "audit_text": self.audit_logger.get_log_text(),
        }
