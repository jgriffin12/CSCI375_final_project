"""Singleton audit logging service."""

from datetime import datetime, timezone

from apps.models.secEvent import SecurityEvent
from apps.repositories.auditRepo import AuditRepository


class AuditLogger:
    """Centralized singleton service for recording security events."""

    _instance = None
    _initialized = False

    def __new__(cls) -> "AuditLogger":
        """Create or return the shared AuditLogger instance."""
        if cls._instance is None:
            cls._instance = super(AuditLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the audit logger once."""
        if self.__class__._initialized:
            return

        self.audit_repository = AuditRepository()
        existing_events = self.audit_repository.get_all()
        self.next_event_id = (
            max((event.event_id for event in existing_events), default=0) + 1
        )

        self.__class__._initialized = True

    def log_event(
        self,
        event_type: str,
        username: str,
        status: str,
    ) -> SecurityEvent:
        """Create, store, and return a new security event."""
        event = SecurityEvent(
            event_id=self.next_event_id,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            username=username,
            status=status,
        )

        self.audit_repository.save(event)
        self.next_event_id += 1

        return event

    def get_all_events(self) -> list[SecurityEvent]:
        """Return every stored audit event."""
        return self.audit_repository.get_all()

    def get_log_text(self) -> str:
        """Return a readable text version of the audit log."""
        return self.audit_repository.get_log_text()
