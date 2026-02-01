"""Tests for the DatabaseController integration layer."""
from __future__ import annotations

from pathlib import Path

import pytest

from meal_planner.database.controller import (
    AuthenticationError,
    DatabaseController,
    DatabaseError,
)


@pytest.fixture()
def db_controller(tmp_path: Path) -> DatabaseController:
    db_path = tmp_path / "mealplanner-test.db"
    controller = DatabaseController(db_path)
    try:
        yield controller
    finally:
        controller.close()


def test_create_profile_persists_user_and_hashes_password(db_controller: DatabaseController) -> None:
    user = db_controller.create_profile("Jan", "sekret")

    profiles = db_controller.list_profiles()
    assert len(profiles) == 1
    assert profiles[0].profile_name == "Jan"

    cursor = db_controller.connection.execute("SELECT password_hash FROM users WHERE id = ?", (user.id,))
    stored_hash = cursor.fetchone()["password_hash"]
    assert stored_hash != "sekret"
    assert stored_hash.startswith("$2b$")


def test_duplicate_profile_name_raises_database_error(db_controller: DatabaseController) -> None:
    db_controller.create_profile("Anna", "haslo123")

    with pytest.raises(DatabaseError, match="Profile name must be unique"):
        db_controller.create_profile("Anna", "innehaslo")


def test_authenticate_with_valid_credentials_returns_user(db_controller: DatabaseController) -> None:
    db_controller.create_profile("Ola", "tajnehaslo")

    user = db_controller.authenticate("Ola", "tajnehaslo")

    assert user.profile_name == "Ola"


def test_authenticate_with_wrong_password_raises_error(db_controller: DatabaseController) -> None:
    db_controller.create_profile("Piotr", "haslo123")

    with pytest.raises(AuthenticationError):
        db_controller.authenticate("Piotr", "zlehaslo")


def test_seed_data_present_after_initialization(db_controller: DatabaseController) -> None:
    cursor = db_controller.connection.execute("SELECT name FROM units ORDER BY name")
    units = [row["name"] for row in cursor.fetchall()]
    assert units == ["gramy", "mililitry", "sztuki"]

    cursor = db_controller.connection.execute(
        "SELECT name, display_order FROM meal_categories ORDER BY display_order"
    )
    categories = [(row["name"], row["display_order"]) for row in cursor.fetchall()]
    assert categories == [("Śniadanie", 1), ("Obiad", 2), ("Kolacja", 3)]


def test_list_profiles_sorted_case_insensitive(db_controller: DatabaseController) -> None:
    db_controller.create_profile("zosia", "123")
    db_controller.create_profile("Antek", "456")

    names = [profile.profile_name for profile in db_controller.list_profiles()]
    assert names == ["Antek", "zosia"]
