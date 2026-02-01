"""Entry point for the MealPlanner application."""
from __future__ import annotations

from meal_planner.app import MealPlannerApp


def main() -> None:
    app = MealPlannerApp()
    app.run()


if __name__ == "__main__":
    main()
