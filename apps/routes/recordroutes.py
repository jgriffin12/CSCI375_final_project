"""Protected medical record route definitions."""

from flask import Blueprint, jsonify, request

from apps.controllers.recordController import RecordController

record_bp = Blueprint("records", __name__)
record_controller = RecordController()


@record_bp.route("/records/<int:record_id>", methods=["GET"])
def get_record(record_id: int):
    """Return a protected medical record for an authorized provider."""
    username = request.args.get("username")

    if not username:
        return jsonify({"status": "failure", "message": "Username required."}), 400

    result = record_controller.get_record(record_id, username)
    status_code = 400 if result.get("status") == "failure" else 200

    return jsonify(result), status_code
