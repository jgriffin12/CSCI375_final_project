"""Repository for protected patient record data."""

from apps.models.record import Record


class RecordRepository:
    """Repository responsible for protected medical record access.

    CJ Secure currently uses one demo provider-accessible patient record.

    Record behavior:
    - Providers can retrieve record ID 1.
    - Record ID 1 belongs to Jane Doe.
    - Jane Doe's medical note states that she has asthma.
    - Patients and admins should not retrieve this record.
    """

    def __init__(self) -> None:
        """Create the demo patient record set."""
        self.records: dict[int, Record] = {
            1: Record(
                record_id=1,
                patient_name="Jane Doe",
                ssn="123-45-6789",
                medical_notes=(
                    "Patient has asthma. Patient uses an inhaler as needed "
                    "and should avoid known respiratory triggers."
                ),
            ),
        }

    def find_by_id(self, record_id: int) -> Record | None:
        """Return a record by ID if it exists."""
        return self.records.get(record_id)
