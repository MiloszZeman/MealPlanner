"""DatabaseController encapsulates all interaction with the SQLite database."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Iterable

import bcrypt

from .schema import initialize_schema


@dataclass(frozen=True)
class UserProfile:
    """Lightweight user profile projection used by the UI layer."""

    id: int
    profile_name: str
    created_at: str


class DatabaseError(RuntimeError):
    """Raised when a database-level failure occurs."""


class AuthenticationError(RuntimeError):
    """Raised when authentication data is invalid."""


class DatabaseController:
    """Coordinated access point to the MealPlanner SQLite database."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._lock = RLock()
        self._connection = self._open_connection()
        self._prime_database()

    def _open_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    def _prime_database(self) -> None:
        with self._lock:
            cursor = self._connection.cursor()
            initialize_schema(cursor)
            self._connection.commit()

    # Lifecycle -----------------------------------------------------------------
    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def __enter__(self) -> "DatabaseController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - infrastructure
        self.close()

    # User profiles -------------------------------------------------------------
    def list_profiles(self) -> list[UserProfile]:
        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, profile_name, created_at FROM users ORDER BY LOWER(profile_name);"
            )
            rows = cursor.fetchall()
            return [UserProfile(id=row["id"], profile_name=row["profile_name"], created_at=row["created_at"]) for row in rows]

    def create_profile(self, profile_name: str, password: str) -> UserProfile:
        if not profile_name.strip():
            raise ValueError("Profile name is required.")
        if not password:
            raise ValueError("Password is required.")

        password_hash = self._hash_password(password)
        try:
            with self._lock:
                cursor = self._connection.execute(
                    "INSERT INTO users (profile_name, password_hash) VALUES (?, ?)",
                    (profile_name.strip(), password_hash),
                )
                self._connection.commit()
        except sqlite3.IntegrityError as exc:  # pragma: no cover - deterministic behavior
            raise DatabaseError("Profile name must be unique.") from exc

        return self.get_profile_by_id(cursor.lastrowid)

    def get_profile_by_id(self, profile_id: int) -> UserProfile:
        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, profile_name, created_at FROM users WHERE id = ?", (profile_id,)
            )
            row = cursor.fetchone()
        if row is None:
            raise DatabaseError(f"User with id {profile_id} was not found.")
        return UserProfile(id=row["id"], profile_name=row["profile_name"], created_at=row["created_at"])

    def authenticate(self, profile_name: str, password: str) -> UserProfile:
        if not profile_name.strip():
            raise AuthenticationError("Profile name is required.")
        if not password:
            raise AuthenticationError("Password is required.")

        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, profile_name, password_hash, created_at FROM users WHERE profile_name = ?",
                (profile_name.strip(),),
            )
            row = cursor.fetchone()

        if row is None:
            raise AuthenticationError("Invalid profile name or password.")

        stored_hash = row["password_hash"]
        if not self._verify_password(password, stored_hash):
            raise AuthenticationError("Invalid profile name or password.")

        return UserProfile(id=row["id"], profile_name=row["profile_name"], created_at=row["created_at"])

    # Password helpers ----------------------------------------------------------
    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        except ValueError:  # pragma: no cover - corrupted hash guard
            return False

    # Utility -------------------------------------------------------------------
    def execute_script(self, queries: Iterable[str]) -> None:
        """Execute raw SQL statements; primarily used for maintenance tasks."""

        with self._lock:
            cursor = self._connection.cursor()
            for query in queries:
                cursor.execute(query)
            self._connection.commit()

    @property
    def connection(self) -> sqlite3.Connection:
        """Direct connection access for advanced scenarios (read-only recommended)."""

        return self._connection
