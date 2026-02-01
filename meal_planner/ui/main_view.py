"""Main application view composed of meal plan and shopping list."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from meal_planner.database.controller import DatabaseController, MealCategory, MealPlanEntry, RecipeSummary, UserProfile
from meal_planner.ui.meal_plan_view import MealPlanView
from meal_planner.ui.shopping_list_view import ShoppingListView
from meal_planner.ui.welcome_view import WelcomeView


class MainView(ttk.Frame):
    """Dashboard rendering the weekly plan and navigation."""

    def __init__(
        self,
        master: tk.Misc,
        db_controller: DatabaseController,
        user: UserProfile,
        on_open_recipes,
        on_logout,
    ) -> None:
        super().__init__(master, padding=12)
        self.db_controller = db_controller
        self.user = user
        self.on_open_recipes = on_open_recipes
        self.on_logout = on_logout

        self.current_plan: list[MealPlanEntry] = []
        self.meal_categories: list[MealCategory] = []

        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(header, text=f"Plan użytkownika: {user.profile_name}", font=("TkDefaultFont", 14, "bold")).pack(side=tk.LEFT)

        ttk.Button(header, text="Wyloguj", command=self.on_logout).pack(side=tk.RIGHT)
        ttk.Button(header, text="Moje przepisy", command=self.on_open_recipes).pack(side=tk.RIGHT, padx=(0, 8))
        self.generate_button = ttk.Button(header, text="Wygeneruj plan", command=self._handle_generate_plan)
        self.generate_button.pack(side=tk.RIGHT, padx=(0, 8))

        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.left_container = ttk.Frame(self.paned)
        self.paned.add(self.left_container, weight=3)

        self.right_container = ttk.Frame(self.paned)
        self.paned.add(self.right_container, weight=1)

        self.plan_container = ttk.Frame(self.left_container)
        self.plan_container.pack(fill=tk.BOTH, expand=True)

        self.meal_plan_view = MealPlanView(self.plan_container, self._handle_change_recipe, self._get_recipes_for_category)
        self.meal_plan_view.pack(fill=tk.BOTH, expand=True)

        self.welcome_view = WelcomeView(self.plan_container, self.on_open_recipes)

        self.shopping_list_view = ShoppingListView(self.right_container)
        self.shopping_list_view.pack(fill=tk.BOTH, expand=True)

        self.refresh()

    def refresh(self) -> None:
        self.meal_categories = self.db_controller.list_meal_categories()
        recipes = self.db_controller.list_recipes(self.user.id)

        if not recipes:
            self.current_plan = []
            self._show_welcome()
            self.shopping_list_view.update_items([])
            self.generate_button.state(["disabled"])
            return

        self.generate_button.state(["!disabled"])
        self._show_plan()

        self.current_plan = self.db_controller.get_meal_plan(self.user.id)
        self.meal_plan_view.set_plan(self.current_plan, self.meal_categories)

        shopping_items = self.db_controller.build_shopping_list(self.user.id) if self.current_plan else []
        self.shopping_list_view.update_items(shopping_items)

    def _show_welcome(self) -> None:
        self.meal_plan_view.pack_forget()
        self.welcome_view.pack(fill=tk.BOTH, expand=True)

    def _show_plan(self) -> None:
        self.welcome_view.pack_forget()
        self.meal_plan_view.pack(fill=tk.BOTH, expand=True)

    def _handle_generate_plan(self) -> None:
        if self.current_plan:
            confirm = messagebox.askyesno(
                "MealPlanner",
                "Czy na pewno chcesz wygenerować nowy plan? Spowoduje to utratę bieżącego.",
            )
            if not confirm:
                return
        try:
            self.db_controller.generate_weekly_meal_plan(self.user.id)
        except Exception as exc:  # pragma: no cover - UI feedback path
            messagebox.showerror("MealPlanner", str(exc))
            return
        self.refresh()

    def _handle_change_recipe(self, plan_entry_id: int, recipe_id: int | None) -> None:
        try:
            self.db_controller.update_meal_plan_entry(self.user.id, plan_entry_id, recipe_id)
        except Exception as exc:  # pragma: no cover - UI feedback path
            messagebox.showerror("MealPlanner", str(exc))
            return
        self.refresh()

    def _get_recipes_for_category(self, category_id: int) -> list[RecipeSummary]:
        return self.db_controller.list_recipes_for_category(self.user.id, category_id)
