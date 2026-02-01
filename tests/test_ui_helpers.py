"""Unit tests for UI helper formatting functions."""
from __future__ import annotations

from datetime import date

import pytest

from meal_planner.database.controller import ShoppingListItem
from meal_planner.ui.meal_plan_view import MealPlanView
from meal_planner.ui.shopping_list_view import ShoppingListView


def test_format_day_header_returns_polish_weekday() -> None:
    header = MealPlanView.format_day_header(date(2026, 2, 1))
    assert header == "2026-02-01\nNiedziela"


@pytest.mark.parametrize(
    "item, expected",
    [
        (
            ShoppingListItem(
                ingredient_name="Mąka",
                total_quantity=1500.0,
                unit_name="gramy",
                is_symbolic=False,
            ),
            "1.5 kg",
        ),
        (
            ShoppingListItem(
                ingredient_name="Bulion",
                total_quantity=2500.0,
                unit_name="mililitry",
                is_symbolic=False,
            ),
            "2.5 litry",
        ),
        (
            ShoppingListItem(
                ingredient_name="Woda",
                total_quantity=750.0,
                unit_name="mililitry",
                is_symbolic=False,
            ),
            "750 mililitry",
        ),
    ],
)
def test_format_quantity_converts_units(item: ShoppingListItem, expected: str) -> None:
    assert ShoppingListView.format_quantity(item) == expected


def test_format_quantity_handles_symbolic_and_missing() -> None:
    symbolic = ShoppingListItem("Sól", None, "gramy", True)
    assert ShoppingListView.format_quantity(symbolic) == "symbolicznie"

    missing = ShoppingListItem("Pieprz", None, "gramy", False)
    assert ShoppingListView.format_quantity(missing) == ""
