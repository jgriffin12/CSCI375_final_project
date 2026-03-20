from flask import Blueprint, request, jsonify
from app.controllers.login_controller import LoginController

# Blueprint groups together all authentication-related routes.
# This keeps auth endpoints separate from records and admin endpoints.
auth_bp = Blueprint("auth", __name__)

# Create one controller instance to handle auth request logic.
login_controller = LoginController()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login endpoint.

    Expected JSON:
    {
        "username": "alice",
        "password": "password123"
    }

    This route only handles HTTP input/output.
    The actual authentication logic lives in the controller/service layer.
    """
    data = request.get_json() or {}
    return jsonify(login_controller.login_request(data))


@auth_bp.route("/verify-mfa", methods=["POST"])
def verify_mfa():
    """
    MFA verification endpoint.

    Expected JSON:
    {
        "username": "alice",
        "code": "123456"
    }

    This route passes the request data to the controller, which then uses
    the service layer to verify the MFA code.
    """
    data = request.get_json() or {}
    return jsonify(login_controller.verify_mfa_request(data))


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
    return jsonify(login_controller.logout_request(data))