"""Administrative route definitions."""

from flask import Blueprint, jsonify, request

from apps.controllers.adminController import AdminController

admin_bp = Blueprint("admin", __name__)
admin_controller = AdminController()


@admin_bp.route("/admin/health", methods=["GET"])
def admin_health():
    """Confirm that the admin blueprint is active."""
    return jsonify({"status": "admin route ready"})


@admin_bp.route("/admin/audit", methods=["GET"])
def get_audit_logs():
    """Return structured audit logs for authorized admin users."""
    username = request.args.get("username")

    if not username:
        return jsonify({"status": "failure", "message": "Username required"}), 400

    result = admin_controller.get_audit_logs(username)
    status_code = 400 if result.get("status") == "failure" else 200

    return jsonify(result), status_code


@admin_bp.route("/admin/audit-text", methods=["GET"])
def get_audit_log_text():
    """Return readable audit log text for authorized admin users."""
    username = request.args.get("username")

    if not username:
        return jsonify({"status": "failure", "message": "Username required"}), 400

    result = admin_controller.get_audit_log_text(username)
    status_code = 400 if result.get("status") == "failure" else 200

    return jsonify(result), status_code
