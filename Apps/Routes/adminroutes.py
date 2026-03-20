from flask import Blueprint, jsonify

# Blueprint for administrative routes such as user management or log review.
admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/health", methods=["GET"])
def admin_health():
    """
    Simple placeholder route to confirm that the admin blueprint is active.

    This is useful early in development to verify that blueprint registration works.
    """
    return jsonify({"status": "admin route ready"})