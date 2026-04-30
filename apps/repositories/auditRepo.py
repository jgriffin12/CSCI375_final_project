"""Repository for storing and loading audit log events."""

import json
from pathlib import Path

from apps.models.secEvent import SecurityEvent


class AuditRepository:
    """Stores audit events in memory and persists them to a text file.

    The file uses JSON lines format. Each line is one event. This keeps the
    file readable for the demo while still allowing the backend to reload it.
    """

    def __init__(self, file_path: str = "data/audit_log.txt") -> None:
        """Initialize the repository and load existing audit events."""
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.events: list[SecurityEvent] = self._load_events()

    def save(self, event: SecurityEvent) -> None:
        """Store a security event in memory and append it to the log file."""
        self.events.append(event)

        with self.file_path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(event.to_dict()) + "\n")

    def get_all(self) -> list[SecurityEvent]:
        """Return all stored audit events."""
        return list(self.events)

    def get_log_text(self) -> str:
        """Return audit events as readable text for frontend display."""
        if not self.events:
            return "No audit events have been recorded yet."

        return "\n".join(
            (
                f"[{event.timestamp.isoformat()}] "
                f"event_id={event.event_id} "
                f"type={event.event_type} "
                f"user={event.username} "
                f"status={event.status}"
            )
            for event in self.events
        )

    def _load_events(self) -> list[SecurityEvent]:
        """Load previously saved events from the audit log file."""
        if not self.file_path.exists():
            return []

        loaded_events: list[SecurityEvent] = []

        for line in self.file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue

            try:
                event_data = json.loads(line)
                loaded_events.append(SecurityEvent.from_dict(event_data))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue

        return loaded_events
