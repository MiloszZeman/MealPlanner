"""Implementation of the LoginView Tkinter frame."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from meal_planner.database.controller import AuthenticationError, DatabaseController, DatabaseError


class LoginView(ttk.Frame):
    """Provides the initial login and profile creation UI."""

    def __init__(self, master: tk.Misc, db_controller: DatabaseController, on_login_success) -> None:
        super().__init__(master, padding=24)
        self.db_controller = db_controller
        self.on_login_success = on_login_success

        self.profile_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.new_profile_name_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        self.new_password_confirm_var = tk.StringVar()

        self._new_profile_visible = False

        self._build_layout()
        self.refresh_profiles()

    def _build_layout(self) -> None:
        title = ttk.Label(self, text="MealPlanner", font=("TkDefaultFont", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 12))

        # Existing profile login section
        ttk.Label(self, text="Wybierz profil:").grid(row=1, column=0, sticky=tk.W)
        self.profile_combo = ttk.Combobox(self, textvariable=self.profile_var, state="readonly")
        self.profile_combo.grid(row=1, column=1, sticky=tk.EW)

        ttk.Label(self, text="Hasło:").grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        password_entry = ttk.Entry(self, textvariable=self.password_var, show="*")
        password_entry.grid(row=2, column=1, sticky=tk.EW, pady=(8, 0))

        login_button = ttk.Button(self, text="Zaloguj", command=self._handle_login)
        login_button.grid(row=3, column=0, columnspan=2, pady=(12, 0), sticky=tk.EW)

        # Status message label
        status_label = ttk.Label(self, textvariable=self.status_var, foreground="#b00020")
        status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

        self.toggle_create_profile_button = ttk.Button(
            self,
            text="Utwórz konto",
            command=self._toggle_create_profile_section,
        )
        self.toggle_create_profile_button.grid(row=5, column=0, columnspan=2, pady=(16, 0), sticky=tk.EW)

        self.new_profile_frame = ttk.Frame(self, padding=(0, 16, 0, 0))
        self._build_new_profile_frame()
        self.new_profile_frame.grid(row=6, column=0, columnspan=2, sticky=tk.EW)
        self.new_profile_frame.grid_remove()

        self.columnconfigure(1, weight=1)

    def _build_new_profile_frame(self) -> None:
        separator = ttk.Separator(self.new_profile_frame, orient=tk.HORIZONTAL)
        separator.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        ttk.Label(self.new_profile_frame, text="Stwórz nowy profil", font=("TkDefaultFont", 12, "bold")).grid(
            row=1, column=0, columnspan=2, sticky=tk.W
        )

        ttk.Label(self.new_profile_frame, text="Nazwa profilu:").grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        ttk.Entry(self.new_profile_frame, textvariable=self.new_profile_name_var).grid(
            row=2, column=1, sticky=tk.EW, pady=(8, 0)
        )

        ttk.Label(self.new_profile_frame, text="Hasło:").grid(row=3, column=0, sticky=tk.W, pady=(8, 0))
        ttk.Entry(self.new_profile_frame, textvariable=self.new_password_var, show="*").grid(
            row=3, column=1, sticky=tk.EW, pady=(8, 0)
        )

        ttk.Label(self.new_profile_frame, text="Powtórz hasło:").grid(row=4, column=0, sticky=tk.W, pady=(8, 0))
        ttk.Entry(self.new_profile_frame, textvariable=self.new_password_confirm_var, show="*").grid(
            row=4, column=1, sticky=tk.EW, pady=(8, 0)
        )

        create_button = ttk.Button(self.new_profile_frame, text="Stwórz profil", command=self._handle_create_profile)
        create_button.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky=tk.EW)

        self.new_profile_frame.columnconfigure(1, weight=1)

    # Data operations -----------------------------------------------------------
    def refresh_profiles(self) -> None:
        profiles = self.db_controller.list_profiles()
        profile_names = [profile.profile_name for profile in profiles]
        self.profile_combo["values"] = profile_names
        if profile_names:
            self.profile_combo.current(0)
        else:
            self.profile_combo.set("")

    # Event handlers ------------------------------------------------------------
    def _handle_login(self) -> None:
        profile_name = self.profile_var.get().strip()
        password = self.password_var.get()
        try:
            user = self.db_controller.authenticate(profile_name, password)
        except AuthenticationError as exc:
            self.set_status(str(exc))
            return
        except DatabaseError as exc:  # pragma: no cover - defensive path
            self.set_status(str(exc))
            return

        self.set_status("")
        self.password_var.set("")
        self.on_login_success(user)

    def _handle_create_profile(self) -> None:
        profile_name = self.new_profile_name_var.get().strip()
        password = self.new_password_var.get()
        password_confirm = self.new_password_confirm_var.get()

        if password != password_confirm:
            self.set_status("Hasła nie są identyczne.")
            return

        try:
            user = self.db_controller.create_profile(profile_name, password)
        except ValueError as exc:
            self.set_status(str(exc))
            return
        except DatabaseError as exc:
            self.set_status(str(exc))
            return

        self.set_status("Profil został utworzony. Zaloguj się.")
        self.new_profile_name_var.set("")
        self.new_password_var.set("")
        self.new_password_confirm_var.set("")
        self.refresh_profiles()
        # Pre-select the newly created profile for convenience
        self.profile_combo.set(user.profile_name)
        self._hide_create_profile_section()

    # Helpers -------------------------------------------------------------------
    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _toggle_create_profile_section(self) -> None:
        if self._new_profile_visible:
            self._hide_create_profile_section()
        else:
            self._show_create_profile_section()

    def _show_create_profile_section(self) -> None:
        self.new_profile_frame.grid()
        self._new_profile_visible = True
        self.toggle_create_profile_button.config(text="Anuluj")

    def _hide_create_profile_section(self) -> None:
        self.new_profile_frame.grid_remove()
        self._new_profile_visible = False
        self.toggle_create_profile_button.config(text="Utwórz konto")
        self.new_profile_name_var.set("")
        self.new_password_var.set("")
        self.new_password_confirm_var.set("")
