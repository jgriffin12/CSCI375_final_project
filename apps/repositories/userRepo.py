from apps.models.user import User
from apps.security.passHash import PasswordHasher


class UserRepository:
    """
    Repository responsible for user data access.
    """

    def __init__(self) -> None:
        hasher = PasswordHasher()

        self.users = {
            "doctor": User(
                user_id=1,
                username="doctor",
                password_hash=hasher.hash_password("password123"),
                email="your@email.com",  # replace if needed
                role="provider",
            ),
            "patient": User(
                user_id=2,
                username="patient",
                password_hash=hasher.hash_password("password123"),
                email="your@email.com",  # replace if needed
                role="patient",
            ),
        }

    def find_by_username(self, username: str):
        """
        Return a User object if the username exists.
        """
        return self.users.get(username)