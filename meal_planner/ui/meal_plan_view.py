"""Meal plan grid view with inline editing support."""
from __future__ import annotations

from datetime import date
import tkinter as tk
from tkinter import ttk

from meal_planner.database.controller import MealCategory, MealPlanEntry


class MealPlanView(ttk.Frame):
    """Grid-based presentation of the 7-day meal plan."""

    POLISH_WEEKDAYS = (
        "Poniedziałek",
        "Wtorek",
        "Środa",
        "Czwartek",
        "Piątek",
        "Sobota",
        "Niedziela",
    )

    def __init__(self, master: tk.Misc, on_change_recipe, recipe_provider) -> None:
        super().__init__(master, padding=(12, 12, 12, 12))
        self.on_change_recipe = on_change_recipe
        self.recipe_provider = recipe_provider

        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        self._placeholder_var = tk.StringVar()
        self.placeholder_label = ttk.Label(self, textvariable=self._placeholder_var, wraplength=520, justify=tk.CENTER)
        self.placeholder_label.pack(fill=tk.BOTH, expand=True, pady=(24, 0))
        self.placeholder_label.pack_forget()

        self.entries: list[MealPlanEntry] = []
        self.categories: list[MealCategory] = []

    def set_plan(self, entries: list[MealPlanEntry], categories: list[MealCategory]) -> None:
        """Render the plan based on provided entries."""

        self.entries = entries
        self.categories = categories

        for child in self.table_frame.winfo_children():
            child.destroy()

        if not entries:
            self._placeholder_var.set(
                "Plan nie został jeszcze wygenerowany. Użyj przycisku \"Wygeneruj plan\" aby rozpocząć."
            )
            self.placeholder_label.pack(fill=tk.BOTH, expand=True, pady=(24, 0))
            return

        self._placeholder_var.set("")
        self.placeholder_label.pack_forget()

        dates = sorted({entry.plan_date for entry in entries})

        header_font = ("TkDefaultFont", 11, "bold")
        ttk.Label(self.table_frame, text="Dzień", font=header_font, padding=(6, 6)).grid(row=0, column=0, sticky=tk.NSEW)
        for col_index, category in enumerate(categories, start=1):
            ttk.Label(self.table_frame, text=category.name, font=header_font, padding=(6, 6)).grid(
                row=0, column=col_index, sticky=tk.NSEW
            )

        entry_lookup = {}
        for entry in entries:
            entry_lookup[(entry.plan_date, entry.meal_category_id)] = entry

        for row_index, plan_date in enumerate(dates, start=1):
            header_text = self.format_day_header(plan_date)
            ttk.Label(self.table_frame, text=header_text, padding=(6, 6), justify=tk.CENTER).grid(
                row=row_index,
                column=0,
                sticky=tk.NSEW,
            )

            for col_index, category in enumerate(categories, start=1):
                entry = entry_lookup.get((plan_date, category.id))
                cell = ttk.Frame(self.table_frame, padding=(6, 6))
                cell.grid(row=row_index, column=col_index, sticky=tk.NSEW)

                text = entry.recipe_name if entry and entry.recipe_name else "—"
                ttk.Label(cell, text=text, wraplength=180, justify=tk.LEFT).pack(anchor=tk.W)
                ttk.Button(
                    cell,
                    text="Zmień",
                    command=lambda e=entry, c=cell: self._open_recipe_selector(e, c),
                    state=tk.NORMAL if entry else tk.DISABLED,
                ).pack(anchor=tk.W, pady=(6, 0))

        for col_index in range(len(categories) + 1):
            self.table_frame.columnconfigure(col_index, weight=1)

    def _open_recipe_selector(self, entry: MealPlanEntry | None, container: ttk.Frame) -> None:
        if entry is None:
            return
        recipes = self.recipe_provider(entry.meal_category_id)
        options = ["— Brak przepisu —"] + [recipe.name for recipe in recipes]
        combo_var = tk.StringVar()
        selector = ttk.Combobox(container, values=options, textvariable=combo_var, state="readonly")
        if entry.recipe_name:
            try:
                current_index = options.index(entry.recipe_name)
            except ValueError:
                current_index = 0
        else:
            current_index = 0
        selector.current(current_index)
        selector.pack(anchor=tk.W, pady=(4, 0))
        selector.focus_set()

        def finalize_selection(_event=None) -> None:
            index = selector.current()
            if index <= 0:
                self.on_change_recipe(entry.id, None)
            elif 0 < index <= len(recipes):
                self.on_change_recipe(entry.id, recipes[index - 1].id)
            selector.destroy()

        selector.bind("<<ComboboxSelected>>", finalize_selection)
        selector.bind("<Return>", finalize_selection)
        selector.bind("<Escape>", lambda _event: selector.destroy())

        def handle_focus_out(_event=None) -> None:
            def _cleanup() -> None:
                if not selector.winfo_exists():
                    return
                focus_widget = selector.focus_get()
                if focus_widget is selector:
                    return
                popdown = selector.tk.call("ttk::combobox::PopdownWindow", selector)
                if focus_widget is not None and str(focus_widget).startswith(popdown):
                    return
                selector.destroy()

            selector.after(200, _cleanup)

        selector.bind("<FocusOut>", handle_focus_out)

    @classmethod
    def format_day_header(cls, plan_date: date) -> str:
        weekday_name = cls.POLISH_WEEKDAYS[plan_date.weekday()]
        return f"{plan_date.isoformat()}\n{weekday_name}"
