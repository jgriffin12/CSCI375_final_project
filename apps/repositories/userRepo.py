"""Repository for storing and loading user profiles."""

import json
from pathlib import Path
from typing import Any

from apps.models.user import User
from apps.security.passHash import PasswordHasher


class UserRepository:
    """Repository for user profiles stored in a JSON text file."""

    def __init__(self, file_path: str = "data/users.json") -> None:
        """Create the repository and ensure demo users exist."""
        self.file_path = Path(file_path)
        self.password_hasher = PasswordHasher()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_seed_users()

    def _seed_users(self) -> list[dict[str, Any]]:
        """Return the default demo users."""
        return [
            {
                "user_id": 1,
                "username": "alice",
                "email": "demo@example.com",
                "role": "provider",
                "password_hash": self.password_hasher.hash_password("password123"),
            },
            {
                "user_id": 2,
                "username": "bob",
                "email": "bob@example.com",
                "role": "patient",
                "password_hash": self.password_hasher.hash_password("password123"),
            },
            {
                "user_id": 3,
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin",
                "password_hash": self.password_hasher.hash_password("admin123"),
            },
        ]

    def _ensure_seed_users(self) -> None:
        """Create the default demo users only when the user file is missing or valid."""
        if self.file_path.exists():
            try:
                with self.file_path.open("r", encoding="utf-8") as file:
                    raw_data = json.load(file)
            except json.JSONDecodeError:
                return

            if not isinstance(raw_data, list):
                return

            users = raw_data
        else:
            users = []

        existing_usernames = {
            str(user_data.get("username", "")).strip().lower()
            for user_data in users
        }

        changed = False

        for seed_user in self._seed_users():
            username = str(seed_user["username"]).strip().lower()

            if username not in existing_usernames:
                users.append(seed_user)
                existing_usernames.add(username)
                changed = True

        if changed or not self.file_path.exists():
            self._write_users(users)

    def _read_users(self) -> list[dict[str, Any]]:
        """Read all users from the JSON text file."""
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        return data

    def _write_users(self, users: list[dict[str, Any]]) -> None:
        """Write all users to the JSON text file."""
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(users, file, indent=2)

    def _next_user_id(self, users: list[dict[str, Any]]) -> int:
        """Return the next available integer user ID."""
        if not users:
            return 1

        return max(int(user_data.get("user_id", 0)) for user_data in users) + 1

    def _to_user(self, data: dict[str, Any]) -> User:
        """Convert stored dictionary data into a User model."""
        return User(
            user_id=int(data["user_id"]),
            username=str(data["username"]),
            password_hash=str(data["password_hash"]),
            email=str(data["email"]),
            role=str(data["role"]),
        )

    def find_by_username(self, username: str) -> User | None:
        """Find a user by username."""
        normalized_username = username.strip().lower()

        for user_data in self._read_users():
            stored_username = str(user_data["username"]).strip().lower()

            if stored_username == normalized_username:
                return self._to_user(user_data)

        return None

    def find_by_email(self, email: str) -> User | None:
        """Find a user by email address."""
        normalized_email = email.strip().lower()

        for user_data in self._read_users():
            stored_email = str(user_data["email"]).strip().lower()

            if stored_email == normalized_email:
                return self._to_user(user_data)

        return None

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        email: str,
    ) -> User:
        """Create and persist a new user profile."""
        if self.find_by_username(username) is not None:
            raise ValueError("Username already exists.")

        if self.find_by_email(email) is not None:
            raise ValueError("Email already exists.")

        users = self._read_users()

        user = User(
            user_id=self._next_user_id(users),
            username=username.strip(),
            password_hash=self.password_hasher.hash_password(password),
            email=email.strip().lower(),
            role=role.strip().lower(),
        )

        users.append(
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "password_hash": user.password_hash,
            }
        )

        self._write_users(users)

        return user

    def all_users(self) -> list[User]:
        """Return all stored users."""
        return [self._to_user(user_data) for user_data in self._read_users()]
