from __future__ import annotations

import tkinter as tk

import pytest

from meal_planner.app import MealPlannerApp
from meal_planner.database.controller import RecipeIngredientInput
from meal_planner.ui.login_view import LoginView
from meal_planner.ui.main_view import MainView


@pytest.fixture()
def app_instance(tmp_path):
    db_path = tmp_path / "ui-tests.db"
    try:
        app = MealPlannerApp(db_path)
    except tk.TclError as exc:  # pragma: no cover - headless environments
        pytest.skip(f"Tkinter unavailable: {exc}")
    app.update()
    yield app
    app.destroy()


def _create_and_login(app: MealPlannerApp, profile_name: str = "tester", password: str = "tajnehaslo") -> MainView:
    view = app.view_controller._active_view
    assert isinstance(view, LoginView)
    view._show_create_profile_section()
    view.new_profile_name_var.set(profile_name)
    view.new_password_var.set(password)
    view.new_password_confirm_var.set(password)
    view._handle_create_profile()
    app.update()

    view.profile_var.set(profile_name)
    view.password_var.set(password)
    view._handle_login()
    app.update()

    active = app.view_controller._active_view
    assert isinstance(active, MainView)
    return active


def _seed_full_recipe_set(app: MealPlannerApp) -> None:
    assert app._active_user is not None
    categories = {c.name: c.id for c in app.db_controller.list_meal_categories()}
    units = {u.name: u.id for u in app.db_controller.list_units()}

    def ingredient(name: str, unit_key: str, quantity: float) -> RecipeIngredientInput:
        return RecipeIngredientInput(name=name, unit_id=units[unit_key], quantity=quantity, is_symbolic=False)

    app.db_controller.create_recipe(
        app._active_user.id,
        "Śniadanie testowe",
        [categories["Śniadanie"]],
        [ingredient("Jajka", "sztuki", 2.0)],
    )
    app.db_controller.create_recipe(
        app._active_user.id,
        "Obiad testowy",
        [categories["Obiad"]],
        [ingredient("Makaron", "gramy", 120.0)],
    )
    app.db_controller.create_recipe(
        app._active_user.id,
        "Kolacja testowa",
        [categories["Kolacja"]],
        [ingredient("Warzywa", "gramy", 100.0)],
    )


def test_login_flow_transitions_to_main_view(app_instance: MealPlannerApp) -> None:
    main_view = _create_and_login(app_instance)

    assert main_view.welcome_view.winfo_ismapped()
    assert not main_view.meal_plan_view.winfo_ismapped()


def test_main_view_generates_plan_and_updates_sections(app_instance: MealPlannerApp) -> None:
    main_view = _create_and_login(app_instance)
    _seed_full_recipe_set(app_instance)

    main_view.refresh()
    app_instance.update()

    assert main_view.generate_button.instate(["!disabled"])
    main_view._handle_generate_plan()
    app_instance.update()

    assert len(main_view.meal_plan_view.entries) == 21
    assert main_view.meal_plan_view.winfo_ismapped()
    assert not main_view.welcome_view.winfo_ismapped()
    assert main_view.shopping_list_view.tree.get_children()


def test_generate_plan_respects_confirmation(monkeypatch, app_instance: MealPlannerApp) -> None:
    main_view = _create_and_login(app_instance)
    _seed_full_recipe_set(app_instance)

    main_view.refresh()
    main_view._handle_generate_plan()
    app_instance.update()

    before_ids = [entry.id for entry in main_view.current_plan]
    calls = {"count": 0}

    def fake_askyesno(*_args, **_kwargs):
        calls["count"] += 1
        return False

    monkeypatch.setattr("meal_planner.ui.main_view.messagebox.askyesno", fake_askyesno)

    main_view._handle_generate_plan()
    app_instance.update()

    assert calls["count"] == 1
    assert [entry.id for entry in main_view.current_plan] == before_ids
