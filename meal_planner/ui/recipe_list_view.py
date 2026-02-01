"""Recipe list view with edit controls."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from meal_planner.database.controller import RecipeSummary


class RecipeListView(ttk.Frame):
    """Displays all recipes for the active user."""

    def __init__(
        self,
        master: tk.Misc,
        recipes: list[RecipeSummary],
        on_add,
        on_edit,
        on_delete,
        on_back,
    ) -> None:
        super().__init__(master, padding=24)
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        ttk.Label(self, text="Moje przepisy", font=("TkDefaultFont", 16, "bold")).pack(anchor=tk.W)

        self.tree = ttk.Treeview(self, columns=("categories",), show="tree headings", selectmode="browse")
        self.tree.heading("categories", text="Kategorie")
        self.tree.column("categories", width=240, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(12, 12))

        button_row = ttk.Frame(self)
        button_row.pack(fill=tk.X)
        ttk.Button(button_row, text="Dodaj nowy przepis", command=self.on_add).pack(side=tk.LEFT)
        ttk.Button(button_row, text="Edytuj", command=self._handle_edit).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(button_row, text="Usuń", command=self._handle_delete).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(button_row, text="Powrót", command=self.on_back).pack(side=tk.RIGHT)

        self.placeholder_var = tk.StringVar()
        self.placeholder_label = ttk.Label(self, textvariable=self.placeholder_var, justify=tk.CENTER, wraplength=420)
        self.placeholder_label.pack(fill=tk.X, pady=(12, 0))

        self.update_recipes(recipes)

    def update_recipes(self, recipes: list[RecipeSummary]) -> None:
        for child in self.tree.get_children():
            self.tree.delete(child)

        if not recipes:
            self.placeholder_var.set("Nie dodano jeszcze żadnych przepisów.")
            self.placeholder_label.lift()
            return

        self.placeholder_label.lower()
        for recipe in recipes:
            categories = ", ".join(recipe.category_names) if recipe.category_names else "—"
            self.tree.insert("", tk.END, iid=str(recipe.id), values=(categories,), text=recipe.name)
        self.tree.heading("#0", text="Nazwa")
        self.tree.column("#0", width=220, anchor=tk.W)

    def _get_selected_recipe_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("MealPlanner", "Wybierz przepis z listy.")
            return None
        return int(selection[0])

    def _handle_edit(self) -> None:
        recipe_id = self._get_selected_recipe_id()
        if recipe_id is not None:
            self.on_edit(recipe_id)

    def _handle_delete(self) -> None:
        recipe_id = self._get_selected_recipe_id()
        if recipe_id is None:
            return
        if not messagebox.askyesno(
            "MealPlanner",
            "Usunięcie przepisu może wpłynąć na obecny plan. Czy na pewno chcesz kontynuować?",
        ):
            return
        self.on_delete(recipe_id)
