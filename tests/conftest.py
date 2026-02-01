from __future__ import annotations

from pathlib import Path

import pytest

from meal_planner.database.controller import DatabaseController


@pytest.fixture()
def db_controller(tmp_path: Path) -> DatabaseController:
    db_path = tmp_path / "mealplanner-test.db"
    controller = DatabaseController(db_path)
    try:
        yield controller
    finally:
        controller.close()
