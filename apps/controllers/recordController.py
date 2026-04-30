"""Controller for protected patient record requests."""

from typing import Any

from apps.repositories.userRepo import UserRepository
from apps.services.accessControlSvc import AccessControlService
from apps.services.auditLogger import AuditLogger
from apps.services.recordSvc import RecordService


class RecordController:
    """Controller for protected record requests.

    The controller accepts data from the route layer, verifies the requesting
    user, applies role-based access control, records audit events, and delegates
    approved provider record retrieval to the service layer.

    Role behavior:
    - Providers can retrieve Jane Doe's protected asthma record.
    - Patients only receive their own patient dashboard message.
    - Admins cannot retrieve patient records and should only view audit logs.
    """

    def __init__(self) -> None:
        """Create controller dependencies."""
        self.record_service = RecordService()
        self.user_repository = UserRepository()
        self.access_control_service = AccessControlService()
        self.audit_logger = AuditLogger()

    def get_record(self, record_id: int, username: str) -> dict[str, Any]:
        """Return record access results based on the authenticated user's role."""
        user = self.user_repository.find_by_username(username)

        if user is None:
            self.audit_logger.log_event(
                "record_access_unknown_user",
                username,
                "failure",
            )
            return {"status": "failure", "message": "User not found"}

        if user.role == "patient":
            self.audit_logger.log_event(
                "patient_record_viewed",
                username,
                "success",
            )
            return {
                "status": "success",
                "role": "patient",
                "records": [],
                "appointments": [],
                "message": (
                    "No appointments, please book one by calling "
                    "12345678910 to schedule."
                ),
            }

        if user.role == "admin":
            self.audit_logger.log_event(
                "admin_record_access_denied",
                username,
                "failure",
            )
            return {
                "status": "failure",
                "message": (
                    "Admin access is limited to audit logs. "
                    "Admins cannot retrieve patient records."
                ),
            }

        if not self.access_control_service.is_authorized(
            user,
            "view_masked_record",
        ):
            self.audit_logger.log_event(
                "record_access_denied",
                username,
                "failure",
            )
            return {
                "status": "failure",
                "message": "Only providers can retrieve Jane Doe's protected record.",
            }

        self.audit_logger.log_event(
            "provider_record_access_requested",
            username,
            "success",
        )

        return self.record_service.get_masked_record(user, record_id)
