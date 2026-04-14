from flask import Blueprint, jsonify

# Blueprint for all protected-record routes.
record_bp = Blueprint("records", __name__)


@record_bp.route("/records/<int:record_id>", methods=["GET"])
def get_record(record_id: int):
    """
    Placeholder route for fetching a protected record.

    Later this route should:
    1. Check the current authenticated user
    2. Call the record controller
    3. Enforce RBAC
    4. Return masked/tokenized sensitive data
    """
    return jsonify({"message": f"Record endpoint placeholder for record {record_id}"})