from apps.compiler.ast_nodes import DenyRule, MaskRule, Program, RoleRule
from apps.compiler.errors import SemanticError


ALLOWED_PERMISSIONS: set[str] = {
    "view_masked_record",
    "view_full_record",
    "view_own_record",
    "review_logs",
    "manage_users",
    "export_records",
}

ALLOWED_MASK_FIELDS: set[str] = {
    "ssn",
    "diagnosis",
    "patient_id",
    "email",
    "phone",
}

UNSAFE_PATIENT_PERMISSIONS: set[str] = {
    "review_logs",
    "manage_users",
    "export_records",
    "view_full_record",
}


class PolicySemanticAnalyzer:
    """Validate policy meaning after parsing succeeds."""

    def analyze(self, program: Program) -> dict[str, object]:
        """Return checked policy data or raise SemanticError."""
        role_permissions: dict[str, set[str]] = {}
        explicit_denies: dict[str, set[str]] = {}
        masks: dict[str, set[str]] = {}

        for statement in program.statements:
            if isinstance(statement, RoleRule):
                self._analyze_role_rule(statement, role_permissions)

        if not role_permissions:
            raise SemanticError("Policy must define at least one role rule.")

        for statement in program.statements:
            if isinstance(statement, DenyRule):
                self._analyze_deny_rule(statement, role_permissions, explicit_denies)
            elif isinstance(statement, MaskRule):
                self._analyze_mask_rule(statement, role_permissions, masks)

        for role_name, denied_permissions in explicit_denies.items():
            role_permissions[role_name] -= denied_permissions

        return {
            "roles": {
                role_name: sorted(permissions)
                for role_name, permissions in sorted(role_permissions.items())
            },
            "denies": {
                role_name: sorted(permissions)
                for role_name, permissions in sorted(explicit_denies.items())
            },
            "masks": {
                role_name: sorted(fields)
                for role_name, fields in sorted(masks.items())
            },
            "statement_count": len(program.statements),
        }

    def _analyze_role_rule(
        self, statement: RoleRule, role_permissions: dict[str, set[str]]
    ) -> None:
        if statement.role_name in role_permissions:
            raise SemanticError(
                f"Role {statement.role_name!r} is defined more than once."
            )

        permissions = set(statement.permissions)
        unknown_permissions = permissions - ALLOWED_PERMISSIONS
        if unknown_permissions:
            joined = ", ".join(sorted(unknown_permissions))
            raise SemanticError(
                f"Unknown permission(s) for role {statement.role_name}: {joined}."
            )

        if statement.role_name == "patient":
            unsafe = permissions & UNSAFE_PATIENT_PERMISSIONS
            if unsafe:
                joined = ", ".join(sorted(unsafe))
                raise SemanticError(f"Unsafe patient permission(s): {joined}.")

        role_permissions[statement.role_name] = permissions

    def _analyze_deny_rule(
        self,
        statement: DenyRule,
        role_permissions: dict[str, set[str]],
        explicit_denies: dict[str, set[str]],
    ) -> None:
        if statement.role_name not in role_permissions:
            raise SemanticError(
                f"Cannot deny permission from undefined role "
                f"{statement.role_name!r}."
            )

        if statement.permission not in ALLOWED_PERMISSIONS:
            raise SemanticError(f"Unknown denied permission {statement.permission!r}.")

        explicit_denies.setdefault(statement.role_name, set()).add(statement.permission)

    def _analyze_mask_rule(
        self,
        statement: MaskRule,
        role_permissions: dict[str, set[str]],
        masks: dict[str, set[str]],
    ) -> None:
        if statement.role_name not in role_permissions:
            raise SemanticError(
                f"Cannot mask field for undefined role {statement.role_name!r}."
            )

        if statement.field_name not in ALLOWED_MASK_FIELDS:
            raise SemanticError(f"Unknown mask field {statement.field_name!r}.")

        masks.setdefault(statement.role_name, set()).add(statement.field_name)
