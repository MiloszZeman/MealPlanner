"""Tests for the DatabaseController integration layer."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from meal_planner.database.controller import (
    AuthenticationError,
    DatabaseController,
    DatabaseError,
    MealCategory,
    MealPlanEntry,
    RecipeDetail,
    RecipeIngredientInput,
)
def test_create_profile_persists_user_and_hashes_password(db_controller: DatabaseController) -> None:
    user = db_controller.create_profile("Jan", "sekret")

    profiles = db_controller.list_profiles()
    names = [profile.profile_name for profile in profiles]
    assert "Jan" in names

    cursor = db_controller.connection.execute("SELECT password_hash FROM users WHERE id = ?", (user.id,))
    stored_hash = cursor.fetchone()["password_hash"]
    assert stored_hash != "sekret"
    assert stored_hash.startswith("$2b$")


def test_create_profile_rejects_blank_inputs(db_controller: DatabaseController) -> None:
    with pytest.raises(ValueError, match="Nazwa profilu jest wymagana"):
        db_controller.create_profile("   ", "secret")

    with pytest.raises(ValueError, match="Hasło jest wymagane"):
        db_controller.create_profile("Valid", "")


def test_duplicate_profile_name_raises_database_error(db_controller: DatabaseController) -> None:
    db_controller.create_profile("Anna", "haslo123")

    with pytest.raises(DatabaseError, match="Nazwa profilu musi być unikalna"):
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
    assert units == ["gramy", "kg", "litry", "mililitry", "sztuki"]

    cursor = db_controller.connection.execute(
        "SELECT name, display_order FROM meal_categories ORDER BY display_order"
    )
    categories = [(row["name"], row["display_order"]) for row in cursor.fetchall()]
    assert categories == [("Śniadanie", 1), ("Obiad", 2), ("Kolacja", 3)]


def test_list_profiles_sorted_case_insensitive(db_controller: DatabaseController) -> None:
    db_controller.create_profile("zosia", "123")
    db_controller.create_profile("Antek", "456")

    names = [profile.profile_name for profile in db_controller.list_profiles() if profile.profile_name != "demo"]
    assert names == ["Antek", "zosia"]


# Helpers ----------------------------------------------------------------------


@pytest.fixture()
def user(db_controller: DatabaseController):
    return db_controller.create_profile("Test", "sekret")


@pytest.fixture()
def units_map(db_controller: DatabaseController):
    return {unit.name: unit for unit in db_controller.list_units()}


@pytest.fixture()
def categories_map(db_controller: DatabaseController):
    return {category.name: category for category in db_controller.list_meal_categories()}


def _make_ingredient(name: str, unit_id: int, quantity: float, symbolic: bool = False) -> RecipeIngredientInput:
    return RecipeIngredientInput(name=name, unit_id=unit_id, quantity=quantity, is_symbolic=symbolic)


def _get_plan_dates(plan: list[MealPlanEntry]) -> list[date]:
    return sorted({entry.plan_date for entry in plan})


def test_create_recipe_and_fetch_details(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    detail = db_controller.create_recipe(
        user.id,
        "Owsianka",
        [categories_map["Śniadanie"].id],
        [_make_ingredient("Płatki owsiane", units_map["gramy"].id, 80.0)],
    )

    assert isinstance(detail, RecipeDetail)
    assert detail.name == "Owsianka"
    assert [cat.name for cat in detail.categories] == ["Śniadanie"]
    assert detail.ingredients[0].ingredient_name == "Płatki owsiane"


def test_create_recipe_validates_required_inputs(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    ingredient = _make_ingredient("Jajka", units_map["sztuki"].id, 2.0)

    with pytest.raises(ValueError, match="Nazwa przepisu jest wymagana"):
        db_controller.create_recipe(user.id, "   ", [categories_map["Śniadanie"].id], [ingredient])

    with pytest.raises(ValueError, match="Wybierz co najmniej jedną kategorię posiłku"):
        db_controller.create_recipe(user.id, "Omlet", [], [ingredient])

    with pytest.raises(ValueError, match="Dodaj przynajmniej jeden składnik"):
        db_controller.create_recipe(user.id, "Omlet", [categories_map["Śniadanie"].id], [])


def test_update_recipe_overwrites_categories_and_ingredients(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    recipe = db_controller.create_recipe(
        user.id,
        "Makaron",
        [categories_map["Obiad"].id],
        [_make_ingredient("Makaron", units_map["gramy"].id, 200.0)],
    )

    updated = db_controller.update_recipe(
        user.id,
        recipe.id,
        "Makaron z pesto",
        [categories_map["Obiad"].id, categories_map["Kolacja"].id],
        [
            _make_ingredient("Makaron", units_map["gramy"].id, 150.0),
            _make_ingredient("Pesto", units_map["gramy"].id, 50.0),
        ],
    )

    assert updated.name == "Makaron z pesto"
    assert sorted(cat.name for cat in updated.categories) == ["Kolacja", "Obiad"]
    ingredient_names = [ingredient.ingredient_name for ingredient in updated.ingredients]
    assert ingredient_names == ["Makaron", "Pesto"]


def test_generate_plan_requires_recipes_for_each_category(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    db_controller.create_recipe(
        user.id,
        "Placuszki",
        [categories_map["Śniadanie"].id],
        [_make_ingredient("Mąka", units_map["gramy"].id, 120.0)],
    )

    with pytest.raises(DatabaseError, match="Brak przepisów"):
        db_controller.generate_weekly_meal_plan(user.id)


def _seed_full_recipe_set(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    db_controller.create_recipe(
        user.id,
        "Jajecznica",
        [categories_map["Śniadanie"].id],
        [_make_ingredient("Jajka", units_map["sztuki"].id, 3)],
    )
    db_controller.create_recipe(
        user.id,
        "Zupa",
        [categories_map["Obiad"].id],
        [_make_ingredient("Marchew", units_map["gramy"].id, 200.0)],
    )
    db_controller.create_recipe(
        user.id,
        "Sałatka",
        [categories_map["Kolacja"].id],
        [_make_ingredient("Sałata", units_map["gramy"].id, 100.0)],
    )


def test_generate_weekly_meal_plan_creates_entries(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    _seed_full_recipe_set(db_controller, user, units_map, categories_map)

    plan = db_controller.generate_weekly_meal_plan(user.id)

    assert len(plan) == 21  # 7 days * 3 posiłki
    plan_dates = _get_plan_dates(plan)
    assert len(plan_dates) == 7
    assert plan_dates[0] == date.today() + timedelta(days=1)


def test_update_meal_plan_entry_validates_category(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    _seed_full_recipe_set(db_controller, user, units_map, categories_map)
    plan = db_controller.generate_weekly_meal_plan(user.id)

    breakfast_entry = next(entry for entry in plan if entry.meal_category_name == "Śniadanie")
    dinner_recipe = db_controller.list_recipes_for_category(user.id, categories_map["Obiad"].id)[0]

    with pytest.raises(DatabaseError):
        db_controller.update_meal_plan_entry(user.id, breakfast_entry.id, dinner_recipe.id)


def test_update_meal_plan_entry_accepts_valid_recipe_and_none(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    _seed_full_recipe_set(db_controller, user, units_map, categories_map)
    alternate = db_controller.create_recipe(
        user.id,
        "Jaglanka",
        [categories_map["Śniadanie"].id],
        [_make_ingredient("Kasza jaglana", units_map["gramy"].id, 60.0)],
    )

    plan = db_controller.generate_weekly_meal_plan(user.id)
    breakfast_entry = next(entry for entry in plan if entry.meal_category_name == "Śniadanie")

    updated_entry = db_controller.update_meal_plan_entry(user.id, breakfast_entry.id, alternate.id)
    assert updated_entry.recipe_id == alternate.id

    cleared_entry = db_controller.update_meal_plan_entry(user.id, breakfast_entry.id, None)
    assert cleared_entry.recipe_id is None


def test_build_shopping_list_aggregates_quantities(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    _seed_full_recipe_set(db_controller, user, units_map, categories_map)

    # Duplicate one ingredient across two meals to verify aggregation
    db_controller.create_recipe(
        user.id,
        "Kanapka",
        [categories_map["Kolacja"].id],
        [_make_ingredient("Sałata", units_map["gramy"].id, 50.0)],
    )

    plan = db_controller.generate_weekly_meal_plan(user.id)
    dinner_entries = [entry for entry in plan if entry.meal_category_name == "Kolacja"]
    dinner_recipes = {recipe.name: recipe for recipe in db_controller.list_recipes_for_category(user.id, categories_map["Kolacja"].id)}
    for entry in dinner_entries:
        db_controller.update_meal_plan_entry(user.id, entry.id, dinner_recipes["Kanapka"].id)

    items = db_controller.build_shopping_list(user.id)

    names = {item.ingredient_name: item for item in items}
    assert "Sałata" in names
    assert names["Sałata"].total_quantity is not None
    # 7 dni * 50 gramów = 350
    assert pytest.approx(names["Sałata"].total_quantity) == 350.0


def test_build_shopping_list_preserves_symbolic_items(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    db_controller.create_recipe(
        user.id,
        "Herbata",
        [categories_map["Śniadanie"].id],
        [
            RecipeIngredientInput(
                name="Sól",
                unit_id=units_map["gramy"].id,
                quantity=0.0,
                is_symbolic=True,
            )
        ],
    )
    db_controller.create_recipe(
        user.id,
        "Zupa",
        [categories_map["Obiad"].id],
        [_make_ingredient("Bulion", units_map["mililitry"].id, 400.0)],
    )
    db_controller.create_recipe(
        user.id,
        "Sałatka",
        [categories_map["Kolacja"].id],
        [_make_ingredient("Warzywa", units_map["gramy"].id, 120.0)],
    )

    db_controller.generate_weekly_meal_plan(user.id)

    items = db_controller.build_shopping_list(user.id)
    salt_item = next(item for item in items if item.ingredient_name == "Sól")
    assert salt_item.is_symbolic
    assert salt_item.total_quantity is None
    assert salt_item.unit_name is None


def test_delete_recipe_reassigns_plan_if_alternative_exists(db_controller: DatabaseController, user, units_map, categories_map) -> None:
    db_controller.create_recipe(
        user.id,
        "Omlet",
        [categories_map["Śniadanie"].id],
        [_make_ingredient("Jajka", units_map["sztuki"].id, 2)],
    )
    db_controller.create_recipe(
        user.id,
        "Owsianka",
        [categories_map["Śniadanie"].id],
        [_make_ingredient("Płatki", units_map["gramy"].id, 60.0)],
    )
    db_controller.create_recipe(
        user.id,
        "Zupa",
        [categories_map["Obiad"].id],
        [_make_ingredient("Bulion", units_map["mililitry"].id, 400.0)],
    )
    db_controller.create_recipe(
        user.id,
        "Sałatka",
        [categories_map["Kolacja"].id],
        [_make_ingredient("Warzywa", units_map["gramy"].id, 150.0)],
    )

    plan = db_controller.generate_weekly_meal_plan(user.id)
    breakfast_recipes = db_controller.list_recipes_for_category(user.id, categories_map["Śniadanie"].id)
    recipe_to_delete = breakfast_recipes[0]
    alternate_recipe = breakfast_recipes[1]

    # Ensure at least one entry references the recipe slated for deletion
    breakfast_entries = [entry for entry in plan if entry.meal_category_name == "Śniadanie"]
    db_controller.update_meal_plan_entry(user.id, breakfast_entries[0].id, recipe_to_delete.id)
    db_controller.update_meal_plan_entry(user.id, breakfast_entries[1].id, alternate_recipe.id)

    db_controller.delete_recipe(user.id, recipe_to_delete.id)

    refreshed_plan = db_controller.get_meal_plan(user.id)
    breakfast_entries = [entry for entry in refreshed_plan if entry.meal_category_name == "Śniadanie"]
    assert all(entry.recipe_id is not None for entry in breakfast_entries)
