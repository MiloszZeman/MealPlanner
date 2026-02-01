"""Main application bootstrap for the MealPlanner Tkinter UI."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path

from meal_planner.database.controller import DatabaseController, UserProfile
from meal_planner.ui.login_view import LoginView


class MealPlannerApp(tk.Tk):
    """Root Tk application wiring together the database layer and the UI."""

    def __init__(self, db_path: str | Path = "meal_planner.db") -> None:
        super().__init__()
        self.title("MealPlanner")
        self.geometry("480x520")
        self.resizable(True, True)

        self.db_controller = DatabaseController(db_path)
        self._active_user: UserProfile | None = None

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.login_view = LoginView(self, self.db_controller, self._on_login_success)
        self.login_view.pack(fill=tk.BOTH, expand=True)

    def _on_login_success(self, user: UserProfile) -> None:
        self._active_user = user
        self.login_view.set_status(f"Zalogowano jako {user.profile_name}.")
        # TODO: Switch to MainView once implemented.

    def _on_close(self) -> None:
        self.db_controller.close()
        self.destroy()

    def run(self) -> None:
        self.mainloop()
