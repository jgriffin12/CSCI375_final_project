from flask import Blueprint, request, jsonify
from apps.controllers.loginController import LoginController

# Blueprint groups together all authentication-related routes.
# This keeps auth endpoints separate from records and admin endpoints.
auth_bp = Blueprint("auth", __name__)

# Create one controller instance to handle auth request logic.
login_controller = LoginController()


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login endpoint"""
    data = request.get_json() or {}
    result = login_controller.login_request(data)

    status_code = 400 if result.get("status") == "error" else 200
    return jsonify(result), status_code


@auth_bp.route("/verify-mfa", methods=["POST"])
def verify_mfa():
    """MFA verification endpoint"""
    data = request.get_json() or {}
    result = login_controller.verify_mfa_request(data)

    status_code = 400 if result.get("status") == "error" else 200
    return jsonify(result), status_code

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout endpoint.

    Expected JSON:
    {
        "username": "alice"
    }

    For now this is a placeholder. Later it can invalidate a session or token.
    """
    data = request.get_json() or {}
    return jsonify(login_controller.logout_request(data)), 200