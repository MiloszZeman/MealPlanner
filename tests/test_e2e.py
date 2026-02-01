from __future__ import annotations

from datetime import date, timedelta

import pytest

from meal_planner.database.controller import (
    AuthenticationError,
    DatabaseController,
    DatabaseError,
    RecipeIngredientInput,
)


def _maps(controller: DatabaseController) -> tuple[dict[str, int], dict[str, int]]:
    categories = {category.name: category.id for category in controller.list_meal_categories()}
    units = {unit.name: unit.id for unit in controller.list_units()}
    return categories, units


def _ingredient(name: str, unit_id: int, quantity: float, symbolic: bool = False) -> RecipeIngredientInput:
    return RecipeIngredientInput(name=name, unit_id=unit_id, quantity=quantity, is_symbolic=symbolic)


def _find_shopping_item(items, ingredient_name: str):
    return next((item for item in items if item.ingredient_name == ingredient_name), None)


def test_e2e_new_user_flow_generates_plan_and_list(db_controller: DatabaseController) -> None:
    categories, units = _maps(db_controller)
    user = db_controller.create_profile("nowyuzytkownik", "silnehaslo")
    authenticated = db_controller.authenticate("nowyuzytkownik", "silnehaslo")
    assert authenticated.id == user.id

    _ = db_controller.create_recipe(
        user.id,
        "Jajecznica",
        [categories["Śniadanie"]],
        [_ingredient("Jajka", units["sztuki"], 2.0)],
    )
    alt_breakfast = db_controller.create_recipe(
        user.id,
        "Jaglanka",
        [categories["Śniadanie"]],
        [_ingredient("Kasza jaglana", units["gramy"], 80.0)],
    )
    db_controller.create_recipe(
        user.id,
        "Makaron",
        [categories["Obiad"]],
        [_ingredient("Makaron", units["gramy"], 120.0)],
    )
    db_controller.create_recipe(
        user.id,
        "Sałatka",
        [categories["Kolacja"]],
        [_ingredient("Warzywa", units["gramy"], 150.0)],
    )

    plan = db_controller.generate_weekly_meal_plan(user.id)
    assert len(plan) == 21
    start_dates = sorted({entry.plan_date for entry in plan})
    assert start_dates[0] == date.today() + timedelta(days=1)

    breakfast_entry = next(entry for entry in plan if entry.meal_category_name == "Śniadanie")
    updated = db_controller.update_meal_plan_entry(user.id, breakfast_entry.id, alt_breakfast.id)
    assert updated.recipe_id == alt_breakfast.id

    items = db_controller.build_shopping_list(user.id)
    assert _find_shopping_item(items, "Kasza jaglana") is not None
    assert _find_shopping_item(items, "Jajka") is not None


def test_e2e_login_and_modify_recipe_flow(db_controller: DatabaseController) -> None:
    categories, units = _maps(db_controller)
    user = db_controller.create_profile("powracajacy", "sekretnehaslo")

    with pytest.raises(AuthenticationError):
        db_controller.authenticate("powracajacy", "blednehaslo")

    db_controller.authenticate("powracajacy", "sekretnehaslo")

    recipe = db_controller.create_recipe(
        user.id,
        "Makaron z sosem",
        [categories["Obiad"]],
        [_ingredient("Makaron", units["gramy"], 150.0)],
    )

    updated = db_controller.update_recipe(
        user.id,
        recipe.id,
        "Makaron warzywny",
        [categories["Obiad"]],
        [
            _ingredient("Makaron", units["gramy"], 120.0),
            _ingredient("Papryka", units["gramy"], 80.0),
        ],
    )
    assert updated.name == "Makaron warzywny"

    db_controller.create_recipe(
        user.id,
        "Pasta kanapkowa",
        [categories["Kolacja"]],
        [_ingredient("Ciecierzyca", units["gramy"], 100.0)],
    )
    db_controller.create_recipe(
        user.id,
        "Owsianka",
        [categories["Śniadanie"]],
        [_ingredient("Płatki owsiane", units["gramy"], 60.0)],
    )

    db_controller.generate_weekly_meal_plan(user.id)
    shopping_list = db_controller.build_shopping_list(user.id)
    papryka_item = _find_shopping_item(shopping_list, "Papryka")
    assert papryka_item is not None
    assert papryka_item.total_quantity == pytest.approx(80.0 * 7)


def test_e2e_edge_conditions_and_recipe_deletion(db_controller: DatabaseController) -> None:
    categories, units = _maps(db_controller)
    user = db_controller.create_profile("brzegowy", "haslo123")

    with pytest.raises(DatabaseError, match="Brak przepisów"):
        db_controller.generate_weekly_meal_plan(user.id)

    breakfast = db_controller.create_recipe(
        user.id,
        "Owsianka",
        [categories["Śniadanie"]],
        [_ingredient("Płatki", units["gramy"], 70.0)],
    )

    with pytest.raises(DatabaseError, match="Obiad"):
        db_controller.generate_weekly_meal_plan(user.id)

    lunch = db_controller.create_recipe(
        user.id,
        "Zupa",
        [categories["Obiad"]],
        [_ingredient("Bulion", units["mililitry"], 400.0)],
    )
    dinner = db_controller.create_recipe(
        user.id,
        "Sałatka",
        [categories["Kolacja"]],
        [_ingredient("Warzywa", units["gramy"], 120.0)],
    )

    db_controller.generate_weekly_meal_plan(user.id)

    db_controller.delete_recipe(user.id, breakfast.id)
    refreshed_plan = db_controller.get_meal_plan(user.id)
    breakfast_entries = [entry for entry in refreshed_plan if entry.meal_category_name == "Śniadanie"]
    assert breakfast_entries
    assert any(entry.recipe_id is None for entry in breakfast_entries)

    shopping_list = db_controller.build_shopping_list(user.id)
    # After deleting breakfast, shopping list should still include remaining categories.
    assert _find_shopping_item(shopping_list, "Bulion") is not None
    assert _find_shopping_item(shopping_list, "Warzywa") is not None

    # Lunch and dinner recipes remain untouched.
    assert lunch.id in {entry.recipe_id for entry in refreshed_plan if entry.meal_category_name == "Obiad"}
    assert dinner.id in {entry.recipe_id for entry in refreshed_plan if entry.meal_category_name == "Kolacja"}
