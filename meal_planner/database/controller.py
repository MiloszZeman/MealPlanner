"""DatabaseController encapsulates all interaction with the SQLite database."""
from __future__ import annotations

import random
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from threading import RLock
from typing import Iterable, Sequence

import bcrypt

from .schema import initialize_schema


MEAL_PLAN_DAYS = 7


@dataclass(frozen=True)
class UserProfile:
    """Lightweight user profile projection used by the UI layer."""

    id: int
    profile_name: str
    created_at: str


@dataclass(frozen=True)
class MealCategory:
    id: int
    name: str
    display_order: int


@dataclass(frozen=True)
class Unit:
    id: int
    name: str


@dataclass(frozen=True)
class RecipeSummary:
    id: int
    name: str
    category_names: tuple[str, ...]


@dataclass(frozen=True)
class RecipeIngredientData:
    ingredient_name: str
    quantity: float | None
    unit_id: int
    unit_name: str
    is_symbolic: bool
    display_order: int | None


@dataclass(frozen=True)
class RecipeDetail:
    id: int
    user_id: int
    name: str
    categories: tuple[MealCategory, ...]
    ingredients: tuple[RecipeIngredientData, ...]


@dataclass(frozen=True)
class MealPlanEntry:
    id: int
    user_id: int
    plan_date: date
    meal_category_id: int
    meal_category_name: str
    recipe_id: int | None
    recipe_name: str | None


@dataclass(frozen=True)
class ShoppingListItem:
    ingredient_name: str
    total_quantity: float | None
    unit_name: str | None
    is_symbolic: bool


@dataclass
class RecipeIngredientInput:
    name: str
    unit_id: int
    quantity: float | None
    is_symbolic: bool
    display_order: int | None = None


DEMO_RECIPES: tuple[dict[str, object], ...] = (
    {
        "name": "Jajecznica z warzywami",
        "categories": ("Śniadanie",),
        "ingredients": (
            {"name": "Jajka", "quantity": 3.0, "unit": "sztuki"},
            {"name": "Masło", "quantity": 10.0, "unit": "gramy"},
            {"name": "Papryka czerwona", "quantity": 50.0, "unit": "gramy"},
            {"name": "Szczypiorek", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Owsianka z jabłkiem",
        "categories": ("Śniadanie",),
        "ingredients": (
            {"name": "Płatki owsiane", "quantity": 60.0, "unit": "gramy"},
            {"name": "Mleko", "quantity": 200.0, "unit": "mililitry"},
            {"name": "Jabłko", "quantity": 1.0, "unit": "sztuki"},
            {"name": "Cynamon", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Kanapki z twarożkiem",
        "categories": ("Śniadanie",),
        "ingredients": (
            {"name": "Pieczywo pełnoziarniste", "quantity": 100.0, "unit": "gramy"},
            {"name": "Twarożek", "quantity": 80.0, "unit": "gramy"},
            {"name": "Ogórek", "quantity": 50.0, "unit": "gramy"},
            {"name": "Szczypiorek", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Placki bananowe",
        "categories": ("Śniadanie",),
        "ingredients": (
            {"name": "Banany", "quantity": 2.0, "unit": "sztuki"},
            {"name": "Płatki owsiane", "quantity": 50.0, "unit": "gramy"},
            {"name": "Jajka", "quantity": 1.0, "unit": "sztuki"},
        ),
    },
    {
        "name": "Tosty francuskie",
        "categories": ("Śniadanie",),
        "ingredients": (
            {"name": "Pieczywo tostowe", "quantity": 80.0, "unit": "gramy"},
            {"name": "Jajka", "quantity": 2.0, "unit": "sztuki"},
            {"name": "Mleko", "quantity": 80.0, "unit": "mililitry"},
            {"name": "Cynamon", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Omlet serowy",
        "categories": ("Śniadanie",),
        "ingredients": (
            {"name": "Jajka", "quantity": 3.0, "unit": "sztuki"},
            {"name": "Ser żółty", "quantity": 40.0, "unit": "gramy"},
            {"name": "Mleko", "quantity": 40.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Jogurt z granolą",
        "categories": ("Śniadanie",),
        "ingredients": (
            {"name": "Jogurt naturalny", "quantity": 200.0, "unit": "mililitry"},
            {"name": "Granola", "quantity": 60.0, "unit": "gramy"},
            {"name": "Miód", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Kurczak pieczony",
        "categories": ("Obiad",),
        "ingredients": (
            {"name": "Pierś z kurczaka", "quantity": 200.0, "unit": "gramy"},
            {"name": "Oliwa", "quantity": 20.0, "unit": "mililitry"},
            {"name": "Zioła prowansalskie", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Spaghetti bolognese",
        "categories": ("Obiad",),
        "ingredients": (
            {"name": "Makaron spaghetti", "quantity": 120.0, "unit": "gramy"},
            {"name": "Mięso mielone", "quantity": 150.0, "unit": "gramy"},
            {"name": "Sos pomidorowy", "quantity": 200.0, "unit": "mililitry"},
            {"name": "Cebula", "quantity": 1.0, "unit": "sztuki"},
        ),
    },
    {
        "name": "Zupa pomidorowa",
        "categories": ("Obiad",),
        "ingredients": (
            {"name": "Bulion warzywny", "quantity": 500.0, "unit": "mililitry"},
            {"name": "Makaron drobny", "quantity": 80.0, "unit": "gramy"},
            {"name": "Przecier pomidorowy", "quantity": 200.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Gulasz warzywny",
        "categories": ("Obiad",),
        "ingredients": (
            {"name": "Marchew", "quantity": 100.0, "unit": "gramy"},
            {"name": "Cukinia", "quantity": 100.0, "unit": "gramy"},
            {"name": "Papryka", "quantity": 80.0, "unit": "gramy"},
            {"name": "Pomidory krojone", "quantity": 200.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Łosoś z ryżem",
        "categories": ("Obiad",),
        "ingredients": (
            {"name": "Filet z łososia", "quantity": 180.0, "unit": "gramy"},
            {"name": "Ryż", "quantity": 100.0, "unit": "gramy"},
            {"name": "Cytryna", "quantity": 1.0, "unit": "sztuki"},
            {"name": "Koperek", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Kotlet schabowy",
        "categories": ("Obiad",),
        "ingredients": (
            {"name": "Schab", "quantity": 180.0, "unit": "gramy"},
            {"name": "Jajka", "quantity": 1.0, "unit": "sztuki"},
            {"name": "Bułka tarta", "quantity": 40.0, "unit": "gramy"},
            {"name": "Olej", "quantity": 30.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Risotto z grzybami",
        "categories": ("Obiad",),
        "ingredients": (
            {"name": "Ryż arborio", "quantity": 120.0, "unit": "gramy"},
            {"name": "Bulion warzywny", "quantity": 400.0, "unit": "mililitry"},
            {"name": "Pieczarki", "quantity": 150.0, "unit": "gramy"},
            {"name": "Parmezan", "quantity": 40.0, "unit": "gramy"},
        ),
    },
    {
        "name": "Sałatka grecka",
        "categories": ("Kolacja",),
        "ingredients": (
            {"name": "Pomidor", "quantity": 120.0, "unit": "gramy"},
            {"name": "Ogórek", "quantity": 100.0, "unit": "gramy"},
            {"name": "Ser feta", "quantity": 80.0, "unit": "gramy"},
            {"name": "Oliwki", "quantity": 40.0, "unit": "gramy"},
            {"name": "Oliwa", "quantity": 20.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Tortilla z warzywami",
        "categories": ("Kolacja",),
        "ingredients": (
            {"name": "Tortilla pszenna", "quantity": 2.0, "unit": "sztuki"},
            {"name": "Papryka", "quantity": 60.0, "unit": "gramy"},
            {"name": "Kukurydza", "quantity": 80.0, "unit": "gramy"},
            {"name": "Sos jogurtowy", "quantity": 50.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Krem z dyni",
        "categories": ("Kolacja",),
        "ingredients": (
            {"name": "Dynia", "quantity": 250.0, "unit": "gramy"},
            {"name": "Bulion warzywny", "quantity": 300.0, "unit": "mililitry"},
            {"name": "Śmietanka", "quantity": 50.0, "unit": "mililitry"},
            {"name": "Gałka muszkatołowa", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
    {
        "name": "Zapiekanka makaronowa",
        "categories": ("Kolacja",),
        "ingredients": (
            {"name": "Makaron", "quantity": 120.0, "unit": "gramy"},
            {"name": "Ser żółty", "quantity": 80.0, "unit": "gramy"},
            {"name": "Szynka", "quantity": 80.0, "unit": "gramy"},
            {"name": "Sos śmietanowy", "quantity": 100.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Wrap z kurczakiem",
        "categories": ("Kolacja",),
        "ingredients": (
            {"name": "Tortilla pszenna", "quantity": 2.0, "unit": "sztuki"},
            {"name": "Kurczak grillowany", "quantity": 120.0, "unit": "gramy"},
            {"name": "Sałata", "quantity": 60.0, "unit": "gramy"},
            {"name": "Sos czosnkowy", "quantity": 40.0, "unit": "mililitry"},
        ),
    },
    {
        "name": "Tarta warzywna",
        "categories": ("Kolacja",),
        "ingredients": (
            {"name": "Ciasto kruche", "quantity": 150.0, "unit": "gramy"},
            {"name": "Brokuł", "quantity": 120.0, "unit": "gramy"},
            {"name": "Ser feta", "quantity": 60.0, "unit": "gramy"},
            {"name": "Jajka", "quantity": 2.0, "unit": "sztuki"},
        ),
    },
    {
        "name": "Kasza z warzywami",
        "categories": ("Kolacja",),
        "ingredients": (
            {"name": "Kasza gryczana", "quantity": 120.0, "unit": "gramy"},
            {"name": "Marchew", "quantity": 80.0, "unit": "gramy"},
            {"name": "Groszek", "quantity": 80.0, "unit": "gramy"},
            {"name": "Zioła prowansalskie", "quantity": None, "unit": "gramy", "symbolic": True},
        ),
    },
)


class DatabaseError(RuntimeError):
    """Raised when a database-level failure occurs."""


class AuthenticationError(RuntimeError):
    """Raised when authentication data is invalid."""


class DatabaseController:
    """Coordinated access point to the MealPlanner SQLite database."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._lock = RLock()
        self._connection = self._open_connection()
        self._prime_database()

    def _open_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    def _prime_database(self) -> None:
        with self._lock:
            cursor = self._connection.cursor()
            initialize_schema(cursor)
            self._connection.commit()
        self._ensure_demo_dataset()

    # Lifecycle -----------------------------------------------------------------
    def close(self) -> None:
        with self._lock:
            self._connection.close()

    def __enter__(self) -> "DatabaseController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - infrastructure
        self.close()

    # User profiles -------------------------------------------------------------
    def list_profiles(self) -> list[UserProfile]:
        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, profile_name, created_at FROM users ORDER BY LOWER(profile_name);"
            )
            rows = cursor.fetchall()
            return [UserProfile(id=row["id"], profile_name=row["profile_name"], created_at=row["created_at"]) for row in rows]

    def create_profile(self, profile_name: str, password: str) -> UserProfile:
        if not profile_name.strip():
            raise ValueError("Nazwa profilu jest wymagana.")
        if not password:
            raise ValueError("Hasło jest wymagane.")

        password_hash = self._hash_password(password)
        try:
            with self._lock:
                cursor = self._connection.execute(
                    "INSERT INTO users (profile_name, password_hash) VALUES (?, ?)",
                    (profile_name.strip(), password_hash),
                )
                self._connection.commit()
        except sqlite3.IntegrityError as exc:  # pragma: no cover - deterministic behavior
            raise DatabaseError("Nazwa profilu musi być unikalna.") from exc

        return self.get_profile_by_id(cursor.lastrowid)

    def get_profile_by_id(self, profile_id: int) -> UserProfile:
        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, profile_name, created_at FROM users WHERE id = ?", (profile_id,)
            )
            row = cursor.fetchone()
        if row is None:
            raise DatabaseError(f"Nie znaleziono użytkownika o identyfikatorze {profile_id}.")
        return UserProfile(id=row["id"], profile_name=row["profile_name"], created_at=row["created_at"])

    def authenticate(self, profile_name: str, password: str) -> UserProfile:
        if not profile_name.strip():
            raise AuthenticationError("Nazwa profilu jest wymagana.")
        if not password:
            raise AuthenticationError("Hasło jest wymagane.")

        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, profile_name, password_hash, created_at FROM users WHERE profile_name = ?",
                (profile_name.strip(),),
            )
            row = cursor.fetchone()

        if row is None:
            raise AuthenticationError("Nieprawidłowa nazwa profilu lub hasło.")

        stored_hash = row["password_hash"]
        if not self._verify_password(password, stored_hash):
            raise AuthenticationError("Nieprawidłowa nazwa profilu lub hasło.")

        return UserProfile(id=row["id"], profile_name=row["profile_name"], created_at=row["created_at"])

    # Reference data ------------------------------------------------------------
    def list_meal_categories(self) -> list[MealCategory]:
        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, name, display_order FROM meal_categories ORDER BY display_order"
            )
            return [MealCategory(id=row["id"], name=row["name"], display_order=row["display_order"]) for row in cursor.fetchall()]

    def list_units(self) -> list[Unit]:
        with self._lock:
            cursor = self._connection.execute("SELECT id, name FROM units ORDER BY LOWER(name)")
            return [Unit(id=row["id"], name=row["name"]) for row in cursor.fetchall()]

    # Recipes -------------------------------------------------------------------
    def list_recipes(self, user_id: int) -> list[RecipeSummary]:
        with self._lock:
            recipes_cursor = self._connection.execute(
                "SELECT id, name FROM recipes WHERE user_id = ? ORDER BY LOWER(name)",
                (user_id,),
            )
            recipes = recipes_cursor.fetchall()
            if not recipes:
                return []

            categories_cursor = self._connection.execute(
                """
                SELECT r.id AS recipe_id, mc.name
                FROM recipes r
                JOIN recipe_meal_categories rmc ON rmc.recipe_id = r.id
                JOIN meal_categories mc ON mc.id = rmc.meal_category_id
                WHERE r.user_id = ?
                ORDER BY r.id, mc.display_order
                """,
                (user_id,),
            )
            categories_map: dict[int, list[str]] = {}
            for row in categories_cursor.fetchall():
                categories_map.setdefault(row["recipe_id"], []).append(row["name"])

        summaries = []
        for row in recipes:
            summaries.append(
                RecipeSummary(
                    id=row["id"],
                    name=row["name"],
                    category_names=tuple(categories_map.get(row["id"], [])),
                )
            )
        return summaries

    def list_recipes_for_category(self, user_id: int, meal_category_id: int) -> list[RecipeSummary]:
        with self._lock:
            cursor = self._connection.execute(
                """
                SELECT r.id, r.name
                FROM recipes r
                JOIN recipe_meal_categories rmc ON rmc.recipe_id = r.id
                WHERE r.user_id = ? AND rmc.meal_category_id = ?
                ORDER BY LOWER(r.name)
                """,
                (user_id, meal_category_id),
            )
            recipes = cursor.fetchall()

            categories_cursor = self._connection.execute(
                """
                SELECT r.id AS recipe_id, mc.name
                FROM recipes r
                JOIN recipe_meal_categories rmc ON rmc.recipe_id = r.id
                JOIN meal_categories mc ON mc.id = rmc.meal_category_id
                WHERE r.user_id = ?
                ORDER BY r.id, mc.display_order
                """,
                (user_id,),
            )
            categories_map: dict[int, list[str]] = {}
            for row in categories_cursor.fetchall():
                categories_map.setdefault(row["recipe_id"], []).append(row["name"])

        return [
            RecipeSummary(
                id=row["id"],
                name=row["name"],
                category_names=tuple(categories_map.get(row["id"], [])),
            )
            for row in recipes
        ]

    def get_recipe_detail(self, user_id: int, recipe_id: int) -> RecipeDetail:
        with self._lock:
            cursor = self._connection.execute(
                "SELECT id, user_id, name FROM recipes WHERE id = ? AND user_id = ?",
                (recipe_id, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("Nie znaleziono przepisu dla użytkownika.")

            categories_cursor = self._connection.execute(
                """
                SELECT mc.id, mc.name, mc.display_order
                FROM recipe_meal_categories rmc
                JOIN meal_categories mc ON mc.id = rmc.meal_category_id
                WHERE rmc.recipe_id = ?
                ORDER BY mc.display_order
                """,
                (recipe_id,),
            )
            categories = tuple(
                MealCategory(id=row_cat["id"], name=row_cat["name"], display_order=row_cat["display_order"])
                for row_cat in categories_cursor.fetchall()
            )

            ingredients_cursor = self._connection.execute(
                """
                SELECT i.name AS ingredient_name,
                       ri.quantity,
                       ri.unit_id,
                       u.name AS unit_name,
                       ri.is_symbolic,
                       ri.display_order
                FROM recipe_ingredients ri
                JOIN ingredients i ON i.id = ri.ingredient_id
                JOIN units u ON u.id = ri.unit_id
                WHERE ri.recipe_id = ?
                ORDER BY COALESCE(ri.display_order, 9999), i.name
                """,
                (recipe_id,),
            )
            ingredients = tuple(
                RecipeIngredientData(
                    ingredient_name=row_ing["ingredient_name"],
                    quantity=row_ing["quantity"],
                    unit_id=row_ing["unit_id"],
                    unit_name=row_ing["unit_name"],
                    is_symbolic=bool(row_ing["is_symbolic"]),
                    display_order=row_ing["display_order"],
                )
                for row_ing in ingredients_cursor.fetchall()
            )

        return RecipeDetail(id=row["id"], user_id=row["user_id"], name=row["name"], categories=categories, ingredients=ingredients)

    def create_recipe(
        self,
        user_id: int,
        name: str,
        category_ids: Sequence[int],
        ingredients: Sequence[RecipeIngredientInput],
    ) -> RecipeDetail:
        self._validate_recipe_inputs(name, category_ids, ingredients)

        with self._lock:
            cursor = self._connection.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute(
                    "INSERT INTO recipes (user_id, name) VALUES (?, ?)",
                    (user_id, name.strip()),
                )
                recipe_id = cursor.lastrowid

                self._apply_recipe_categories(cursor, recipe_id, category_ids)
                self._apply_recipe_ingredients(cursor, recipe_id, ingredients)

                self._connection.commit()
            except Exception as exc:  # pragma: no cover - transactional guard
                self._connection.rollback()
                raise DatabaseError("Nie udało się utworzyć przepisu.") from exc

        return self.get_recipe_detail(user_id, recipe_id)

    def update_recipe(
        self,
        user_id: int,
        recipe_id: int,
        name: str,
        category_ids: Sequence[int],
        ingredients: Sequence[RecipeIngredientInput],
    ) -> RecipeDetail:
        self._validate_recipe_inputs(name, category_ids, ingredients)

        with self._lock:
            cursor = self._connection.cursor()
            cursor.execute("SELECT id FROM recipes WHERE id = ? AND user_id = ?", (recipe_id, user_id))
            if cursor.fetchone() is None:
                raise DatabaseError("Nie znaleziono przepisu dla użytkownika.")

            try:
                cursor.execute("BEGIN")
                cursor.execute("UPDATE recipes SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (name.strip(), recipe_id))
                cursor.execute("DELETE FROM recipe_meal_categories WHERE recipe_id = ?", (recipe_id,))
                cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))

                self._apply_recipe_categories(cursor, recipe_id, category_ids)
                self._apply_recipe_ingredients(cursor, recipe_id, ingredients)

                self._connection.commit()
            except Exception as exc:  # pragma: no cover - transactional guard
                self._connection.rollback()
                raise DatabaseError("Nie udało się zaktualizować przepisu.") from exc

        return self.get_recipe_detail(user_id, recipe_id)

    def delete_recipe(self, user_id: int, recipe_id: int) -> None:
        with self._lock:
            cursor = self._connection.cursor()
            cursor.execute("SELECT id FROM recipes WHERE id = ? AND user_id = ?", (recipe_id, user_id))
            if cursor.fetchone() is None:
                raise DatabaseError("Nie znaleziono przepisu dla użytkownika.")

            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
                self._reassign_meal_plan_entries(cursor, user_id)
                self._connection.commit()
            except Exception as exc:  # pragma: no cover - transactional guard
                self._connection.rollback()
                raise DatabaseError("Nie udało się usunąć przepisu.") from exc

    def _apply_recipe_categories(self, cursor: sqlite3.Cursor, recipe_id: int, category_ids: Sequence[int]) -> None:
        for category_id in category_ids:
            cursor.execute(
                "INSERT INTO recipe_meal_categories (recipe_id, meal_category_id) VALUES (?, ?)",
                (recipe_id, category_id),
            )

    def _apply_recipe_ingredients(
        self,
        cursor: sqlite3.Cursor,
        recipe_id: int,
        ingredients: Sequence[RecipeIngredientInput],
    ) -> None:
        for index, ingredient in enumerate(ingredients):
            ingredient_id = self._ensure_ingredient(cursor, ingredient.name)
            quantity = None if ingredient.is_symbolic else ingredient.quantity
            display_order = ingredient.display_order if ingredient.display_order is not None else index
            cursor.execute(
                """
                INSERT INTO recipe_ingredients (
                    recipe_id,
                    ingredient_id,
                    quantity,
                    unit_id,
                    is_symbolic,
                    display_order
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    recipe_id,
                    ingredient_id,
                    quantity,
                    ingredient.unit_id,
                    1 if ingredient.is_symbolic else 0,
                    display_order,
                ),
            )

    def _ensure_ingredient(self, cursor: sqlite3.Cursor, name: str) -> int:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Nazwa składnika jest wymagana.")

        cursor.execute("SELECT id FROM ingredients WHERE name = ?", (normalized,))
        row = cursor.fetchone()
        if row:
            return row["id"]

        cursor.execute("INSERT INTO ingredients (name) VALUES (?)", (normalized,))
        return cursor.lastrowid

    def _ensure_demo_dataset(self) -> None:
        try:
            with self._lock:
                cursor = self._connection.execute(
                    "SELECT id FROM users WHERE profile_name = ?",
                    ("demo",),
                )
                row = cursor.fetchone()

            if row:
                demo_user_id = row["id"]
                with self._lock:
                    cursor = self._connection.execute(
                        "SELECT COUNT(*) AS cnt FROM recipes WHERE user_id = ?",
                        (demo_user_id,),
                    )
                    if cursor.fetchone()["cnt"] >= len(DEMO_RECIPES):
                        return
            else:
                demo_user = self.create_profile("demo", "demo")
                demo_user_id = demo_user.id

            categories = {category.name: category.id for category in self.list_meal_categories()}
            units = {unit.name: unit.id for unit in self.list_units()}

            for spec in DEMO_RECIPES:
                name = spec["name"]  # type: ignore[index]
                with self._lock:
                    cursor = self._connection.execute(
                        "SELECT 1 FROM recipes WHERE user_id = ? AND name = ?",
                        (demo_user_id, name),
                    )
                    if cursor.fetchone():
                        continue

                category_ids = [categories[cat_name] for cat_name in spec["categories"]]  # type: ignore[index]
                ingredients_input: list[RecipeIngredientInput] = []
                for index, ingredient in enumerate(spec["ingredients"]):  # type: ignore[index]
                    symbol = bool(ingredient.get("symbolic", False))
                    quantity = ingredient["quantity"] if not symbol else None
                    ingredients_input.append(
                        RecipeIngredientInput(
                            name=ingredient["name"],
                            unit_id=units[ingredient["unit"]],
                            quantity=quantity,
                            is_symbolic=symbol,
                            display_order=index,
                        )
                    )

                self.create_recipe(demo_user_id, name, category_ids, ingredients_input)
        except Exception:
            # Seeding should never break application startup; failures are silently ignored.
            return

    def _validate_recipe_inputs(
        self,
        name: str,
        category_ids: Sequence[int],
        ingredients: Sequence[RecipeIngredientInput],
    ) -> None:
        if not name.strip():
            raise ValueError("Nazwa przepisu jest wymagana.")
        if not category_ids:
            raise ValueError("Wybierz co najmniej jedną kategorię posiłku.")
        if not ingredients:
            raise ValueError("Dodaj przynajmniej jeden składnik.")

    # Meal plan -----------------------------------------------------------------
    def get_meal_plan(self, user_id: int) -> list[MealPlanEntry]:
        with self._lock:
            cursor = self._connection.execute(
                """
                SELECT mp.id,
                       mp.user_id,
                       mp.date,
                       mp.meal_category_id,
                       mc.name AS meal_category_name,
                       mp.recipe_id,
                       r.name AS recipe_name
                FROM meal_plan mp
                JOIN meal_categories mc ON mc.id = mp.meal_category_id
                LEFT JOIN recipes r ON r.id = mp.recipe_id
                WHERE mp.user_id = ?
                ORDER BY mp.date, mc.display_order
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

        return [
            MealPlanEntry(
                id=row["id"],
                user_id=row["user_id"],
                plan_date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                meal_category_id=row["meal_category_id"],
                meal_category_name=row["meal_category_name"],
                recipe_id=row["recipe_id"],
                recipe_name=row["recipe_name"],
            )
            for row in rows
        ]

    def generate_weekly_meal_plan(self, user_id: int, start_date: date | None = None) -> list[MealPlanEntry]:
        start = start_date or (date.today() + timedelta(days=1))
        categories = self.list_meal_categories()
        if len(categories) != 3:
            raise DatabaseError("Oczekiwano trzech kategorii posiłków do wygenerowania planu.")

        recipe_map = {
            category.id: self._recipe_ids_for_category(user_id, category.id) for category in categories
        }
        missing = [cat.name for cat in categories if not recipe_map[cat.id]]
        if missing:
            raise DatabaseError(
                "Brak przepisów dla kategorii: " + ", ".join(missing)
            )

        schedule: dict[int, list[int]] = {}
        for category in categories:
            schedule[category.id] = self._build_weekly_sequence(recipe_map[category.id])

        with self._lock:
            cursor = self._connection.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM meal_plan WHERE user_id = ?", (user_id,))

                for offset in range(MEAL_PLAN_DAYS):
                    target_date = start + timedelta(days=offset)
                    date_str = target_date.isoformat()
                    for category in categories:
                        recipe_id = schedule[category.id][offset]
                        cursor.execute(
                            """
                            INSERT INTO meal_plan (user_id, date, meal_category_id, recipe_id)
                            VALUES (?, ?, ?, ?)
                            """,
                            (user_id, date_str, category.id, recipe_id),
                        )

                self._connection.commit()
            except Exception as exc:  # pragma: no cover - transactional guard
                self._connection.rollback()
                raise DatabaseError("Nie udało się wygenerować planu posiłków.") from exc

        return self.get_meal_plan(user_id)

    def update_meal_plan_entry(self, user_id: int, plan_entry_id: int, recipe_id: int | None) -> MealPlanEntry:
        with self._lock:
            cursor = self._connection.cursor()
            cursor.execute(
                "SELECT meal_category_id FROM meal_plan WHERE id = ? AND user_id = ?",
                (plan_entry_id, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise DatabaseError("Nie znaleziono pozycji planu dla użytkownika.")

            meal_category_id = row["meal_category_id"]
            if recipe_id is not None:
                cursor.execute(
                    """
                    SELECT 1 FROM recipes r
                    JOIN recipe_meal_categories rmc ON rmc.recipe_id = r.id
                    WHERE r.id = ? AND r.user_id = ? AND rmc.meal_category_id = ?
                    """,
                    (recipe_id, user_id, meal_category_id),
                )
                if cursor.fetchone() is None:
                    raise DatabaseError("Przepis nie pasuje do tej kategorii posiłku.")

            cursor.execute(
                "UPDATE meal_plan SET recipe_id = ? WHERE id = ?",
                (recipe_id, plan_entry_id),
            )
            self._connection.commit()

        return self._get_meal_plan_entry(plan_entry_id)

    def _get_meal_plan_entry(self, plan_entry_id: int) -> MealPlanEntry:
        with self._lock:
            cursor = self._connection.execute(
                """
                SELECT mp.id,
                       mp.user_id,
                       mp.date,
                       mp.meal_category_id,
                       mc.name AS meal_category_name,
                       mp.recipe_id,
                       r.name AS recipe_name
                FROM meal_plan mp
                JOIN meal_categories mc ON mc.id = mp.meal_category_id
                LEFT JOIN recipes r ON r.id = mp.recipe_id
                WHERE mp.id = ?
                """,
                (plan_entry_id,),
            )
            row = cursor.fetchone()

        if row is None:
            raise DatabaseError("Nie znaleziono pozycji planu.")

        return MealPlanEntry(
            id=row["id"],
            user_id=row["user_id"],
            plan_date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
            meal_category_id=row["meal_category_id"],
            meal_category_name=row["meal_category_name"],
            recipe_id=row["recipe_id"],
            recipe_name=row["recipe_name"],
        )

    def _reassign_meal_plan_entries(self, cursor: sqlite3.Cursor, user_id: int) -> None:
        cursor.execute(
            "SELECT id, meal_category_id FROM meal_plan WHERE user_id = ? AND recipe_id IS NULL",
            (user_id,),
        )
        orphaned = cursor.fetchall()
        if not orphaned:
            return

        cache: dict[int, list[int]] = {}
        for row in orphaned:
            category_id = row["meal_category_id"]
            recipe_candidates = cache.get(category_id)
            if recipe_candidates is None:
                recipe_candidates = self._recipe_ids_for_category(user_id, category_id)
                cache[category_id] = recipe_candidates
            if not recipe_candidates:
                continue
            replacement = random.choice(recipe_candidates)
            cursor.execute(
                "UPDATE meal_plan SET recipe_id = ? WHERE id = ?",
                (replacement, row["id"]),
            )

    def _recipe_ids_for_category(self, user_id: int, category_id: int) -> list[int]:
        with self._lock:
            cursor = self._connection.execute(
                """
                SELECT r.id
                FROM recipes r
                JOIN recipe_meal_categories rmc ON rmc.recipe_id = r.id
                WHERE r.user_id = ? AND rmc.meal_category_id = ?
                ORDER BY LOWER(r.name)
                """,
                (user_id, category_id),
            )
            return [row["id"] for row in cursor.fetchall()]

    def _build_weekly_sequence(self, recipe_ids: list[int]) -> list[int]:
        if not recipe_ids:
            return []
        if len(recipe_ids) >= MEAL_PLAN_DAYS:
            shuffled = recipe_ids.copy()
            random.shuffle(shuffled)
            return shuffled[:MEAL_PLAN_DAYS]

        result: list[int] = []
        pool = recipe_ids.copy()
        while len(result) < MEAL_PLAN_DAYS:
            if not pool:
                pool = recipe_ids.copy()
            random.shuffle(pool)
            result.append(pool.pop())
        return result

    def _recipe_name_by_id(self, cursor: sqlite3.Cursor, recipe_id: int) -> str:
        cursor.execute("SELECT name FROM recipes WHERE id = ?", (recipe_id,))
        row = cursor.fetchone()
        return row["name"] if row else ""

    # Shopping list -------------------------------------------------------------
    def build_shopping_list(self, user_id: int, start_date: date | None = None, end_date: date | None = None) -> list[ShoppingListItem]:
        plan_entries = self.get_meal_plan(user_id)
        if not plan_entries:
            return []

        start = start_date or min(entry.plan_date for entry in plan_entries)
        end = end_date or max(entry.plan_date for entry in plan_entries)

        with self._lock:
            cursor = self._connection.execute(
                """
                SELECT i.name AS ingredient_name,
                       CASE WHEN ri.is_symbolic = 1 THEN NULL ELSE SUM(ri.quantity) END AS total_quantity,
                       CASE WHEN ri.is_symbolic = 1 THEN NULL ELSE u.name END AS unit_name,
                       ri.is_symbolic
                FROM meal_plan mp
                JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
                JOIN ingredients i ON ri.ingredient_id = i.id
                JOIN units u ON ri.unit_id = u.id
                WHERE mp.user_id = ?
                  AND mp.date BETWEEN ? AND ?
                  AND mp.recipe_id IS NOT NULL
                GROUP BY i.name, ri.is_symbolic, u.name
                ORDER BY i.name COLLATE NOCASE
                """,
                (user_id, start.isoformat(), end.isoformat()),
            )
            rows = cursor.fetchall()

        return [
            ShoppingListItem(
                ingredient_name=row["ingredient_name"],
                total_quantity=row["total_quantity"],
                unit_name=row["unit_name"],
                is_symbolic=bool(row["is_symbolic"]),
            )
            for row in rows
        ]

    # Utility -------------------------------------------------------------------
    def execute_script(self, queries: Iterable[str]) -> None:
        """Execute raw SQL statements; primarily used for maintenance tasks."""

        with self._lock:
            cursor = self._connection.cursor()
            for query in queries:
                cursor.execute(query)
            self._connection.commit()

    @property
    def connection(self) -> sqlite3.Connection:
        """Direct connection access for advanced scenarios (read-only recommended)."""

        return self._connection

    # Password helpers ----------------------------------------------------------
    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        except ValueError:  # pragma: no cover - corrupted hash guard
            return False
