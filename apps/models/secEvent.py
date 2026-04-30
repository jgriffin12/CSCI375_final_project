"""Security event model used by the audit logging system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SecurityEvent:
    """Represents one security-relevant event in the system."""

    event_id: int
    timestamp: datetime
    event_type: str
    username: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the event into a serializable dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "username": self.username,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SecurityEvent":
        """Create a security event from stored dictionary data."""
        return cls(
            event_id=int(data["event_id"]),
            timestamp=datetime.fromisoformat(str(data["timestamp"])),
            event_type=str(data["event_type"]),
            username=str(data["username"]),
            status=str(data["status"]),
        )
