"""Welcome screen displayed when no recipes or plans exist yet."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class WelcomeView(ttk.Frame):
    """Encourages the user to add their first recipes."""

    def __init__(self, master: tk.Misc, on_add_recipe) -> None:
        super().__init__(master, padding=32)
        self.on_add_recipe = on_add_recipe

        title = ttk.Label(self, text="Witaj w MealPlanner", font=("TkDefaultFont", 16, "bold"))
        title.pack(pady=(0, 16))

        message = (
            "Zanim wygenerujesz pierwszy plan, dodaj co najmniej po jednym przepisie "
            "dla Śniadania, Obiadu i Kolacji."
        )
        ttk.Label(self, text=message, wraplength=380, justify=tk.CENTER).pack(pady=(0, 16))

        ttk.Button(self, text="Przejdź do przepisów", command=self.on_add_recipe).pack()
