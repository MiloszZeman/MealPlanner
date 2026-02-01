"""Main application bootstrap for the MealPlanner Tkinter UI."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from meal_planner.database.controller import DatabaseController, RecipeDetail, RecipeIngredientInput, UserProfile
from meal_planner.ui.login_view import LoginView
from meal_planner.ui.main_view import MainView
from meal_planner.ui.recipe_form_view import RecipeFormView
from meal_planner.ui.recipe_list_view import RecipeListView
from meal_planner.ui.view_controller import ViewController


class MealPlannerApp(tk.Tk):
    """Root Tk application wiring together the database layer and the UI."""

    def __init__(self, db_path: str | Path = "meal_planner.db") -> None:
        super().__init__()
        self.title("MealPlanner")
        self.geometry("960x640")
        self.resizable(True, True)

        self.db_controller = DatabaseController(db_path)
        self._active_user: UserProfile | None = None

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.view_controller = ViewController(self.container)
        self._show_login_view()

    # View orchestration -------------------------------------------------------
    def _show_login_view(self) -> None:
        login_view = LoginView(self.container, self.db_controller, self._handle_login_success)
        self.view_controller.show(login_view)

    def _show_main_view(self) -> None:
        assert self._active_user is not None
        main_view = MainView(
            self.container,
            self.db_controller,
            self._active_user,
            on_open_recipes=self._show_recipe_list,
            on_logout=self._handle_logout,
        )
        self.view_controller.show(main_view)

    def _show_recipe_list(self) -> None:
        assert self._active_user is not None
        recipes = self.db_controller.list_recipes(self._active_user.id)
        recipe_list_view = RecipeListView(
            self.container,
            recipes,
            on_add=self._show_add_recipe_form,
            on_edit=self._show_edit_recipe_form,
            on_delete=self._delete_recipe,
            on_back=self._show_main_view,
        )
        self.view_controller.show(recipe_list_view)

    def _show_add_recipe_form(self) -> None:
        self._show_recipe_form()

    def _show_edit_recipe_form(self, recipe_id: int) -> None:
        assert self._active_user is not None
        recipe = self.db_controller.get_recipe_detail(self._active_user.id, recipe_id)
        self._show_recipe_form(recipe)

    def _show_recipe_form(self, recipe: RecipeDetail | None = None) -> None:
        assert self._active_user is not None
        categories = self.db_controller.list_meal_categories()
        units = self.db_controller.list_units()

        def handle_submit(name: str, category_ids, ingredient_inputs: list[RecipeIngredientInput]) -> None:
            try:
                if recipe is None:
                    self.db_controller.create_recipe(self._active_user.id, name, category_ids, ingredient_inputs)
                else:
                    self.db_controller.update_recipe(self._active_user.id, recipe.id, name, category_ids, ingredient_inputs)
            except Exception as exc:  # pragma: no cover - UI feedback path
                messagebox.showerror("MealPlanner", str(exc))
                return
            self._show_recipe_list()

        recipe_form = RecipeFormView(
            self.container,
            categories,
            units,
            on_submit=handle_submit,
            on_cancel=self._show_recipe_list,
            recipe=recipe,
        )
        self.view_controller.show(recipe_form)

    # Event handlers -----------------------------------------------------------
    def _handle_login_success(self, user: UserProfile) -> None:
        self._active_user = user
        self._show_main_view()

    def _handle_logout(self) -> None:
        if messagebox.askyesno("MealPlanner", "Czy na pewno chcesz wylogować użytkownika?"):
            self._active_user = None
            self._show_login_view()

    def _delete_recipe(self, recipe_id: int) -> None:
        assert self._active_user is not None
        try:
            self.db_controller.delete_recipe(self._active_user.id, recipe_id)
        except Exception as exc:  # pragma: no cover - UI feedback path
            messagebox.showerror("MealPlanner", str(exc))
            return
        messagebox.showinfo("MealPlanner", "Przepis został usunięty.")
        self._show_recipe_list()

    # Lifecycle ----------------------------------------------------------------
    def _on_close(self) -> None:
        self.db_controller.close()
        self.destroy()

    def run(self) -> None:
        self.mainloop()
