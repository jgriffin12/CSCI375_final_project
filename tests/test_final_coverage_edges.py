"""Final edge-case tests to increase coverage."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from apps.models.permission import Permission
from apps.models.record import Record
from apps.models.secEvent import SecurityEvent
from apps.repositories.auditRepo import AuditRepository
from apps.repositories.userRepo import UserRepository
from apps.security.mfaFactory import MFAFactory
from apps.security.mfaStrategies import EmailOTPStrategy
from apps.services.auditLogger import AuditLogger
from apps.services.authSvc import AuthService


def test_permission_model():
    """Permission model should store permission data."""
    permission = Permission("view_masked_record")

    assert permission is not None
    assert "view_masked_record" in repr(permission)


def test_record_model_optional_methods():
    """Record model should expose stored record data."""
    record = Record(
        record_id=1,
        patient_name="Alice Anderson",
        ssn="123-45-6789",
        medical_notes="Patient notes",
    )

    assert record.record_id == 1
    assert record.patient_name == "Alice Anderson"
    assert record.ssn == "123-45-6789"
    assert record.medical_notes == "Patient notes"

    if hasattr(record, "to_dict"):
        assert record.to_dict()["record_id"] == 1


def test_security_event_optional_methods():
    """SecurityEvent model should expose stored event data."""
    event = SecurityEvent(
        event_id=1,
        timestamp=datetime.now(timezone.utc),
        event_type="login_success",
        username="alice",
        status="success",
    )

    assert event.event_id == 1
    assert event.event_type == "login_success"
    assert event.username == "alice"
    assert event.status == "success"

    if hasattr(event, "to_dict"):
        assert event.to_dict()["event_type"] == "login_success"


def test_audit_repository_get_all_events(tmp_path):
    """AuditRepository should return saved events."""
    log_file = tmp_path / "audit_log.txt"
    repository = AuditRepository(file_path=str(log_file))

    event = SecurityEvent(
        event_id=1,
        timestamp=datetime.now(timezone.utc),
        event_type="login_success",
        username="alice",
        status="success",
    )

    if hasattr(repository, "add_event"):
        repository.add_event(event)
    elif hasattr(repository, "save"):
        repository.save(event)
    elif hasattr(repository, "events"):
        repository.events.append(event)

    if hasattr(repository, "get_all_events"):
        events = repository.get_all_events()
    elif hasattr(repository, "get_all"):
        events = repository.get_all()
    else:
        events = repository.events

    assert len(events) == 1
    assert events[0].event_type == "login_success"


def test_audit_logger_get_all_events(tmp_path, monkeypatch):
    """AuditLogger should return logged events."""
    monkeypatch.chdir(tmp_path)

    AuditLogger._instance = None
    AuditLogger._initialized = False

    logger = AuditLogger()
    logger.log_event("login_success", "alice", "success")

    events = logger.get_all_events()

    assert len(events) == 1
    assert events[0].event_type == "login_success"

    AuditLogger._instance = None
    AuditLogger._initialized = False


def test_user_repository_duplicate_create_user(tmp_path, monkeypatch):
    """Creating an existing username should raise ValueError."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    with pytest.raises(ValueError):
        repository.create_user(
            username="alice",
            password="password123",
            role="admin",
            email="alice@example.com",
        )


def test_user_repository_create_user_return_value(tmp_path, monkeypatch):
    """create_user should return the created user."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    user = repository.create_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    assert user.username == "chica"
    assert user.email == "chica@example.com"
    assert user.role == "patient"


def test_mfa_factory_creates_email_strategy():
    """MFAFactory should create the email strategy branch."""
    factory = MFAFactory()

    strategy = factory.create_strategy("email")

    assert isinstance(strategy, EmailOTPStrategy)


def test_auth_service_register_missing_fields(tmp_path, monkeypatch):
    """AuthService registration should reject missing fields."""
    monkeypatch.chdir(tmp_path)

    service = AuthService()

    result = service.register_user(
        username="",
        password="",
        role="",
        email="",
    )

    assert result["status"] == "error"
    assert "required" in result["message"]


def test_auth_service_verify_unknown_user(tmp_path, monkeypatch):
    """AuthService MFA verification should reject unknown users."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MFA_METHOD", "totp")

    service = AuthService()

    result = service.verify_mfa(
        username="missing",
        code="654321",
    )

    assert result["status"] == "error"
    assert result["message"] == "User not found."


def test_email_strategy_verify_missing_code():
    """EmailOTPStrategy should reject users with no active code."""
    strategy = EmailOTPStrategy()
    user = SimpleNamespace(username="alice", email="alice@example.com")

    assert strategy.verify_code(user, "123456") is False


def test_record_get_summary():
    """Record get_summary should return the expected summary string."""
    record = Record(
        record_id=1,
        patient_name="Alice Anderson",
        ssn="123-45-6789",
        medical_notes="Patient notes",
    )

    assert record.get_summary() == "Record 1 for Alice Anderson"


def test_user_repository_find_by_email_existing_and_missing(tmp_path, monkeypatch):
    """UserRepository should find users by stored email."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    existing = repository.find_by_email("DEMO@EXAMPLE.COM")
    missing = repository.find_by_email("missing@example.com")

    assert existing is not None
    assert existing.username == "alice"
    assert missing is None


def test_login_controller_check_email_invalid_new_and_existing(tmp_path, monkeypatch):
    """LoginController should support the email-first account lookup flow."""
    monkeypatch.chdir(tmp_path)

    from apps.controllers.loginController import LoginController

    controller = LoginController()

    invalid = controller.check_email_request({"email": "bad-email"})
    assert invalid["status"] == "error"

    new_user = controller.check_email_request({"email": "new@example.com"})
    assert new_user["status"] == "new_user"

    controller.auth_service.register_user(
        username="chica",
        password="password123",
        role="provider",
        email="chica@example.com",
    )

    existing = controller.check_email_request({"email": "chica@example.com"})
    assert existing["status"] == "existing_user"
    assert existing["username"] == "chica"
    assert existing["role"] == "provider"


def test_check_email_route(monkeypatch):
    """The /check-email route should return the controller lookup result."""
    from apps.main import create_app
    from apps.routes import authRoutes

    class FakeLoginController:
        def check_email_request(self, data):
            return {
                "status": "existing_user",
                "email": data["email"],
                "username": "chica",
                "role": "provider",
            }

    authRoutes.login_controller = FakeLoginController()

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/check-email",
        json={"email": "chica@example.com"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "existing_user"


def test_check_email_route_error(monkeypatch):
    """The /check-email route should return 400 for invalid email data."""
    from apps.main import create_app
    from apps.routes import authRoutes

    class FakeLoginController:
        def check_email_request(self, data):
            return {
                "status": "error",
                "message": "A valid email is required.",
            }

    authRoutes.login_controller = FakeLoginController()

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/check-email",
        json={"email": "bad-email"},
    )

    assert response.status_code == 400
    assert response.get_json()["status"] == "error"


def test_user_repository_next_user_id_empty_list(tmp_path, monkeypatch):
    """_next_user_id should return 1 when no users exist."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    assert repository._next_user_id([]) == 1


def test_user_repository_duplicate_email_create_user(tmp_path, monkeypatch):
    """Creating an existing email should raise ValueError."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()

    with pytest.raises(ValueError):
        repository.create_user(
            username="newalice",
            password="password123",
            role="patient",
            email="demo@example.com",
        )


def test_user_repository_all_users(tmp_path, monkeypatch):
    """all_users should return every stored user model."""
    monkeypatch.chdir(tmp_path)

    repository = UserRepository()
    users = repository.all_users()

    assert len(users) >= 2
    assert users[0].username == "alice"
    assert users[0].user_id == 1


def test_user_repository_read_users_returns_empty_for_invalid_json_shape(
    tmp_path,
):
    """_read_users should return an empty list if JSON is not a list."""
    users_file = tmp_path / "users.json"
    users_file.write_text('{"bad": "shape"}', encoding="utf-8")

    repository = UserRepository(file_path=str(users_file))

    assert repository._read_users() == []


def test_admin_controller_event_to_dict_uses_to_dict():
    """AdminController should use to_dict when the event provides it."""
    from apps.controllers.adminController import AdminController

    class FakeEvent:
        def to_dict(self):
            return {
                "event_id": 99,
                "event_type": "fake_event",
                "username": "alice",
                "status": "success",
            }

    controller = AdminController()
    result = controller._event_to_dict(FakeEvent())

    assert result["event_id"] == 99
    assert result["event_type"] == "fake_event"


def test_audit_repository_empty_and_invalid_lines(tmp_path):
    """AuditRepository should handle empty, blank, and invalid audit files."""
    from apps.repositories.auditRepo import AuditRepository

    missing_file = tmp_path / "missing-audit.txt"
    missing_repository = AuditRepository(file_path=str(missing_file))

    assert missing_repository.get_all() == []
    assert (
        missing_repository.get_log_text()
        == "No audit events have been recorded yet."
    )

    bad_file = tmp_path / "bad-audit.txt"
    bad_file.write_text("\nnot json\n{}\n", encoding="utf-8")

    bad_repository = AuditRepository(file_path=str(bad_file))

    assert bad_repository.get_all() == []
    assert (
        bad_repository.get_log_text()
        == "No audit events have been recorded yet."
    )


def test_user_repository_seed_and_read_bad_files(tmp_path):
    """UserRepository should handle malformed and non-list user files."""
    from apps.repositories.userRepo import UserRepository

    bad_seed_file = tmp_path / "bad-seed-users.json"
    bad_seed_file.write_text("{bad json", encoding="utf-8")

    bad_seed_repository = UserRepository(file_path=str(bad_seed_file))
    assert bad_seed_repository._read_users() == []

    wrong_shape_file = tmp_path / "wrong-shape-users.json"
    wrong_shape_file.write_text(
        '{"alice": {"role": "provider"}}',
        encoding="utf-8",
    )

    wrong_shape_repository = UserRepository(file_path=str(wrong_shape_file))
    assert wrong_shape_repository._read_users() == []

    missing_file = tmp_path / "missing-users.json"
    missing_repository = UserRepository(file_path=str(missing_file))
    missing_file.unlink()

    assert missing_repository._read_users() == []


def test_audit_logger_get_log_text(tmp_path, monkeypatch):
    """AuditLogger should expose readable audit log text."""
    from apps.services.auditLogger import AuditLogger

    monkeypatch.chdir(tmp_path)

    logger = AuditLogger()
    text = logger.get_log_text()

    assert isinstance(text, str)


def test_auth_service_registration_failure_and_logout(tmp_path, monkeypatch):
    """AuthService should cover duplicate registration and logout paths."""
    from apps.services.authSvc import AuthService

    monkeypatch.chdir(tmp_path)

    service = AuthService()

    first = service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )
    assert first["status"] == "success"

    duplicate = service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="different@example.com",
    )
    assert duplicate["status"] == "error"

    missing_logout = service.logout("")
    assert missing_logout["status"] == "error"

    successful_logout = service.logout("chica")
    assert successful_logout["status"] == "success"


def test_admin_controller_audit_text_failure_and_success_paths(
    tmp_path,
    monkeypatch,
):
    """AdminController should handle audit text denied and allowed paths."""
    from types import SimpleNamespace

    from apps.controllers.adminController import AdminController

    monkeypatch.chdir(tmp_path)

    controller = AdminController()

    class FakeUsers:
        def __init__(self, user):
            self.user = user

        def find_by_username(self, username):
            return self.user

    class FakeAccess:
        def __init__(self, allowed):
            self.allowed = allowed

        def is_authorized(self, user, permission):
            return self.allowed

    class FakeAuditLogger:
        def __init__(self):
            self.events = []

        def log_event(self, event_type, username, status):
            self.events.append((event_type, username, status))

        def get_log_text(self):
            return "audit text"

    controller.user_repository = FakeUsers(None)

    missing = controller.get_audit_log_text("missing-user")
    assert missing["status"] == "failure"
    assert missing["message"] == "User not found"

    fake_user = SimpleNamespace(username="bob", role="patient")
    controller.user_repository = FakeUsers(fake_user)
    controller.access_control_service = FakeAccess(False)
    controller.audit_logger = FakeAuditLogger()

    denied = controller.get_audit_log_text("bob")
    assert denied["status"] == "failure"
    assert denied["message"] == "Access denied"

    admin_user = SimpleNamespace(username="admin", role="admin")
    controller.user_repository = FakeUsers(admin_user)
    controller.access_control_service = FakeAccess(True)
    controller.audit_logger = FakeAuditLogger()

    allowed = controller.get_audit_log_text("admin")
    assert allowed["status"] == "success"
    assert allowed["audit_text"] == "audit text"


def test_record_controller_patient_admin_unknown_and_denied_paths(
    tmp_path,
    monkeypatch,
):
    """RecordController should cover patient, admin, unknown, and denied paths."""
    from types import SimpleNamespace

    from apps.controllers.recordController import RecordController

    monkeypatch.chdir(tmp_path)

    controller = RecordController()

    patient_result = controller.get_record(1, "bob")
    assert patient_result["status"] == "success"
    assert patient_result["role"] == "patient"
    assert patient_result["records"] == []
    assert "No appointments" in patient_result["message"]

    missing_result = controller.get_record(1, "missing-user")
    assert missing_result["status"] == "failure"
    assert missing_result["message"] == "User not found"

    class FakeAdminUsers:
        def find_by_username(self, username):
            return SimpleNamespace(username=username, role="admin")

    controller.user_repository = FakeAdminUsers()

    admin_result = controller.get_record(1, "admin-user")
    assert admin_result["status"] == "failure"
    assert "Admins cannot retrieve patient records" in admin_result["message"]

    class FakeNurseUsers:
        def find_by_username(self, username):
            return SimpleNamespace(username=username, role="nurse")

    class FakeAccess:
        def is_authorized(self, user, permission):
            return False

    controller.user_repository = FakeNurseUsers()
    controller.access_control_service = FakeAccess()

    denied_result = controller.get_record(1, "nurse-user")
    assert denied_result["status"] == "failure"
    assert "Only providers" in denied_result["message"]


def test_admin_audit_text_route_paths(tmp_path, monkeypatch):
    """The audit-text route should cover missing, failure, and success paths."""
    from apps.main import create_app
    import apps.routes.adminroutes as adminroutes

    monkeypatch.chdir(tmp_path)

    class FakeAdminController:
        def get_audit_log_text(self, username):
            if username == "alice":
                return {
                    "status": "success",
                    "audit_text": "audit text",
                }

            return {
                "status": "failure",
                "message": "Access denied",
            }

    monkeypatch.setattr(
        adminroutes,
        "admin_controller",
        FakeAdminController(),
    )

    app = create_app()
    client = app.test_client()

    missing_response = client.get("/admin/audit-text")
    assert missing_response.status_code == 400
    assert missing_response.get_json()["status"] == "failure"

    denied_response = client.get("/admin/audit-text?username=bob")
    assert denied_response.status_code == 400
    assert denied_response.get_json()["status"] == "failure"

    allowed_response = client.get("/admin/audit-text?username=alice")
    assert allowed_response.status_code == 200
    assert allowed_response.get_json()["status"] == "success"


def test_auth_service_registration_value_error_path(tmp_path, monkeypatch):
    """AuthService should return an error when user creation raises ValueError."""
    from apps.services.authSvc import AuthService

    monkeypatch.chdir(tmp_path)

    service = AuthService()

    class FakeUserRepository:
        def find_by_username(self, username):
            return None

        def find_by_email(self, email):
            return None

        def create_user(self, username, password, role, email):
            raise ValueError("forced duplicate")

    service.user_repository = FakeUserRepository()

    result = service.register_user(
        username="chica",
        password="password123",
        role="patient",
        email="chica@example.com",
    )

    assert result["status"] == "error"
    assert result["message"] == "forced duplicate"
