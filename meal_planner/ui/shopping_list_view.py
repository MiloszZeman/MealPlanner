"""Shopping list panel displaying aggregated ingredients."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from meal_planner.database.controller import ShoppingListItem


class ShoppingListView(ttk.Frame):
    """Shows the consolidated shopping list for the active meal plan."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=(12, 12, 12, 12))

        ttk.Label(self, text="Lista zakupów", font=("TkDefaultFont", 12, "bold")).pack(anchor=tk.W)

        columns = ("quantity",)
        self.tree = ttk.Treeview(self, columns=columns, show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="Składnik")
        self.tree.heading("quantity", text="Ilość")
        self.tree.column("#0", stretch=True, width=180)
        self.tree.column("quantity", stretch=False, width=120, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self.placeholder_var = tk.StringVar(value="Brak pozycji do wyświetlenia.")
        self.placeholder_label = ttk.Label(self, textvariable=self.placeholder_var, wraplength=220, justify=tk.CENTER)
        self.placeholder_label.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        self.placeholder_label.pack_forget()

    def update_items(self, items: list[ShoppingListItem]) -> None:
        """Reload the shopping list content."""

        for child in self.tree.get_children():
            self.tree.delete(child)

        if not items:
            self.placeholder_var.set("Lista zakupów będzie dostępna po wygenerowaniu planu.")
            self.placeholder_label.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
            return

        self.placeholder_var.set("")
        self.placeholder_label.pack_forget()
        for item in items:
            quantity_text = self.format_quantity(item)
            self.tree.insert("", tk.END, text=item.ingredient_name, values=(quantity_text,))

    @staticmethod
    def format_quantity(item: ShoppingListItem) -> str:
        if item.is_symbolic:
            return "symbolicznie"
        if item.total_quantity is None:
            return ""

        quantity = item.total_quantity
        unit = item.unit_name or ""

        if unit == "gramy" and quantity >= 1000:
            quantity = quantity / 1000
            unit = "kg"
        elif unit == "mililitry" and quantity >= 1000:
            quantity = quantity / 1000
            unit = "litry"

        formatted_qty = ("{0:.2f}".format(quantity)).rstrip("0").rstrip(".")
        return f"{formatted_qty} {unit}".strip()
