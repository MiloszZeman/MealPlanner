from __future__ import annotations

import tkinter as tk

from meal_planner.ui.view_controller import ViewController


class DummyWidget:
    def __init__(self, label: str) -> None:
        self.label = label
        self.pack_calls: list[dict[str, object]] = []
        self.pack_forget_count = 0

    def pack(self, **kwargs) -> None:  # type: ignore[override]
        self.pack_calls.append(kwargs)

    def pack_forget(self) -> None:  # type: ignore[override]
        self.pack_forget_count += 1


class DummyContainer:
    pass


def test_show_switches_between_views_and_packs_new_widget() -> None:
    controller = ViewController(DummyContainer())
    first = DummyWidget("first")
    second = DummyWidget("second")

    controller.show(first)
    assert first.pack_calls == [{"fill": tk.BOTH, "expand": True}]

    controller.show(second)
    assert first.pack_forget_count == 1
    assert second.pack_calls == [{"fill": tk.BOTH, "expand": True}]


def test_show_does_nothing_when_same_view_passed() -> None:
    controller = ViewController(DummyContainer())
    view = DummyWidget("unique")

    controller.show(view)
    before = len(view.pack_calls)
    controller.show(view)

    assert len(view.pack_calls) == before
    assert view.pack_forget_count == 0


def test_clear_removes_active_view() -> None:
    controller = ViewController(DummyContainer())
    view = DummyWidget("clear me")

    controller.show(view)
    controller.clear()

    assert view.pack_forget_count == 1

    replacement = DummyWidget("replacement")
    controller.show(replacement)
    assert replacement.pack_calls == [{"fill": tk.BOTH, "expand": True}]
