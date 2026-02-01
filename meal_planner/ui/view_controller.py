"""Simple view controller to manage swapping Tkinter frames."""
from __future__ import annotations

import tkinter as tk


class ViewController:
    """Controls which view is currently displayed in the root container."""

    def __init__(self, container: tk.Misc) -> None:
        self.container = container
        self._active_view: tk.Widget | None = None

    def show(self, view: tk.Widget) -> None:
        """Display the provided view, hiding the currently active one."""

        if self._active_view is view:
            return
        if self._active_view is not None:
            self._active_view.pack_forget()
        self._active_view = view
        view.pack(fill=tk.BOTH, expand=True)

    def clear(self) -> None:
        """Remove the currently shown view."""

        if self._active_view is not None:
            self._active_view.pack_forget()
            self._active_view = None
