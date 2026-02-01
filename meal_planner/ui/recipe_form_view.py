"""Recipe form view supporting add and edit operations."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from meal_planner.database.controller import (
    MealCategory,
    RecipeDetail,
    RecipeIngredientData,
    RecipeIngredientInput,
    Unit,
)


class IngredientRow(ttk.Frame):
    """Dynamic row for ingredient entry."""

    def __init__(
        self,
        master: tk.Misc,
        units: list[Unit],
        on_remove,
        initial: RecipeIngredientData | None = None,
    ) -> None:
        super().__init__(master)
        self.units = units
        self.on_remove = on_remove

        self.name_var = tk.StringVar(value=initial.ingredient_name if initial else "")
        quantity_value = ""
        if initial and initial.quantity is not None:
            quantity_value = ("{0:.2f}".format(initial.quantity)).rstrip("0").rstrip(".")
        self.quantity_var = tk.StringVar(value=quantity_value)
        self.unit_var = tk.IntVar(value=initial.unit_id if initial else (units[0].id if units else 0))
        self.symbolic_var = tk.BooleanVar(value=initial.is_symbolic if initial else False)

        ttk.Entry(self, textvariable=self.name_var, width=24).grid(row=0, column=0, padx=(0, 8))
        self.quantity_entry = ttk.Entry(self, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=0, column=1, padx=(0, 8))

        self.unit_combo = ttk.Combobox(
            self,
            values=[unit.name for unit in units],
            state="readonly",
            width=12,
        )
        if units:
            index = 0
            if initial:
                for idx, unit in enumerate(units):
                    if unit.id == initial.unit_id:
                        index = idx
                        break
            self.unit_combo.current(index)
        self.unit_combo.grid(row=0, column=2, padx=(0, 8))

        symbolic_check = ttk.Checkbutton(
            self,
            text="Symbolicznie",
            variable=self.symbolic_var,
            command=self._sync_symbolic_state,
        )
        symbolic_check.grid(row=0, column=3, padx=(0, 8))

        ttk.Button(self, text="Usuń", command=self.on_remove).grid(row=0, column=4)

        self._sync_symbolic_state()

    def _sync_symbolic_state(self) -> None:
        if self.symbolic_var.get():
            self.quantity_entry.configure(state=tk.DISABLED)
        else:
            self.quantity_entry.configure(state=tk.NORMAL)

    def get_input(self, units: list[Unit]) -> RecipeIngredientInput:
        name = self.name_var.get().strip()
        if not name:
            raise ValueError("Nazwa składnika jest wymagana.")

        symbolic = self.symbolic_var.get()
        quantity = None
        if not symbolic:
            quantity_text = self.quantity_var.get().strip()
            if not quantity_text:
                raise ValueError(f"Podaj ilość dla składnika '{name}'.")
            try:
                quantity = float(quantity_text)
            except ValueError as exc:
                raise ValueError(f"Niepoprawna ilość dla składnika '{name}'.") from exc

        unit_index = self.unit_combo.current()
        if unit_index < 0 or unit_index >= len(units):
            raise ValueError(f"Wybierz jednostkę miary dla składnika '{name}'.")

        return RecipeIngredientInput(
            name=name,
            unit_id=units[unit_index].id,
            quantity=quantity,
            is_symbolic=symbolic,
        )


class RecipeFormView(ttk.Frame):
    """Dynamic form for creating or editing recipes."""

    def __init__(
        self,
        master: tk.Misc,
        meal_categories: list[MealCategory],
        units: list[Unit],
        on_submit,
        on_cancel,
        recipe: RecipeDetail | None = None,
    ) -> None:
        super().__init__(master, padding=24)
        self.meal_categories = meal_categories
        self.units = units
        self.on_submit = on_submit
        self.on_cancel = on_cancel

        self.recipe = recipe

        ttk.Label(self, text="Dodaj przepis" if recipe is None else "Edytuj przepis", font=("TkDefaultFont", 16, "bold")).pack(anchor=tk.W)

        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        ttk.Label(form_frame, text="Nazwa przepisu:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar(value=recipe.name if recipe else "")
        ttk.Entry(form_frame, textvariable=self.name_var, width=48).grid(row=0, column=1, sticky=tk.EW)

        ttk.Label(form_frame, text="Kategorie posiłku:").grid(row=1, column=0, sticky=tk.W, pady=(12, 0))
        self.category_vars: dict[int, tk.BooleanVar] = {}
        category_frame = ttk.Frame(form_frame)
        category_frame.grid(row=1, column=1, sticky=tk.W, pady=(12, 0))
        selected_ids = {cat.id for cat in recipe.categories} if recipe else set()
        for category in meal_categories:
            var = tk.BooleanVar(value=category.id in selected_ids)
            ttk.Checkbutton(category_frame, text=category.name, variable=var).pack(anchor=tk.W)
            self.category_vars[category.id] = var

        ttk.Label(form_frame, text="Składniki:").grid(row=2, column=0, sticky=tk.NW, pady=(12, 0))
        self.ingredients_container = ttk.Frame(form_frame)
        self.ingredients_container.grid(row=2, column=1, sticky=tk.EW, pady=(12, 0))

        self.ingredient_rows: list[IngredientRow] = []
        initial_ingredients = list(recipe.ingredients) if recipe else []
        if not initial_ingredients:
            self._add_ingredient_row()
        else:
            for ingredient in initial_ingredients:
                self._add_ingredient_row(initial=ingredient)

        add_button = ttk.Button(self.ingredients_container, text="Dodaj składnik", command=self._add_ingredient_row)
        add_button.grid(row=999, column=0, columnspan=5, pady=(12, 0), sticky=tk.W)

        self.error_var = tk.StringVar()
        ttk.Label(self, textvariable=self.error_var, foreground="#b00020").pack(anchor=tk.W, pady=(12, 0))

        button_row = ttk.Frame(self)
        button_row.pack(fill=tk.X, pady=(16, 0))
        ttk.Button(button_row, text="Zapisz", command=self._handle_submit).pack(side=tk.RIGHT)
        ttk.Button(button_row, text="Anuluj", command=self.on_cancel).pack(side=tk.RIGHT, padx=(0, 8))

        form_frame.columnconfigure(1, weight=1)

    def _add_ingredient_row(self, initial: RecipeIngredientData | None = None) -> None:
        row = IngredientRow(self.ingredients_container, self.units, lambda: self._remove_ingredient_row(row), initial)
        row.grid(row=len(self.ingredient_rows), column=0, columnspan=5, pady=(4, 0), sticky=tk.W)
        self.ingredient_rows.append(row)

    def _remove_ingredient_row(self, row: IngredientRow) -> None:
        if row in self.ingredient_rows:
            row.destroy()
            self.ingredient_rows.remove(row)
        if not self.ingredient_rows:
            self._add_ingredient_row()

    def _handle_submit(self) -> None:
        try:
            name = self.name_var.get().strip()
            if not name:
                raise ValueError("Nazwa przepisu jest wymagana.")

            category_ids = [cid for cid, var in self.category_vars.items() if var.get()]
            if not category_ids:
                raise ValueError("Wybierz co najmniej jedną kategorię.")

            ingredient_inputs = [row.get_input(self.units) for row in self.ingredient_rows]
            if not ingredient_inputs:
                raise ValueError("Dodaj przynajmniej jeden składnik.")

            self.error_var.set("")
            self.on_submit(name, category_ids, ingredient_inputs)
        except ValueError as exc:
            self.error_var.set(str(exc))
