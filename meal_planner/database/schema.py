"""Database schema definition and initialization utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SchemaStatement:
    """Represents a schema SQL statement to execute in order."""

    sql: str
    idempotent: bool = True  # allows us to ignore errors when objects already exist


SCHEMA_STATEMENTS: tuple[SchemaStatement, ...] = (
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    ),
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS meal_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_order INTEGER NOT NULL
        );
        """
    ),
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        """
    ),
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE
        );
        """
    ),
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id, name)
        );
        """
    ),
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS recipe_meal_categories (
            recipe_id INTEGER NOT NULL,
            meal_category_id INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_category_id) REFERENCES meal_categories(id) ON DELETE RESTRICT,
            PRIMARY KEY (recipe_id, meal_category_id)
        );
        """
    ),
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity REAL NULL,
            unit_id INTEGER NOT NULL,
            is_symbolic BOOLEAN NOT NULL DEFAULT 0,
            display_order INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT,
            FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE RESTRICT
        );
        """
    ),
    SchemaStatement(
        """
        CREATE TABLE IF NOT EXISTS meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            meal_category_id INTEGER NOT NULL,
            recipe_id INTEGER NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (meal_category_id) REFERENCES meal_categories(id) ON DELETE RESTRICT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE SET NULL,
            UNIQUE (user_id, date, meal_category_id)
        );
        """
    ),
    # Indexes
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_users_profile_name ON users(profile_name);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_recipe_meal_categories_recipe_id ON recipe_meal_categories(recipe_id);"),
    SchemaStatement(
        "CREATE INDEX IF NOT EXISTS idx_recipe_meal_categories_meal_category_id ON recipe_meal_categories(meal_category_id);"
    ),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_meal_plan_user_id ON meal_plan(user_id);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_meal_plan_recipe_id ON meal_plan(recipe_id);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_meal_plan_date ON meal_plan(date);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);"),
    SchemaStatement("CREATE INDEX IF NOT EXISTS idx_meal_plan_user_date ON meal_plan(user_id, date);"),
    # Trigger for updated_at consistency
    SchemaStatement(
        """
        CREATE TRIGGER IF NOT EXISTS update_recipes_timestamp
        AFTER UPDATE ON recipes
        FOR EACH ROW
        BEGIN
            UPDATE recipes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """,
    ),
)

SEED_QUERIES: tuple[str, ...] = (
    "INSERT OR IGNORE INTO meal_categories (id, name, display_order) VALUES (1, 'Śniadanie', 1);",
    "INSERT OR IGNORE INTO meal_categories (id, name, display_order) VALUES (2, 'Obiad', 2);",
    "INSERT OR IGNORE INTO meal_categories (id, name, display_order) VALUES (3, 'Kolacja', 3);",
    "INSERT OR IGNORE INTO units (name) VALUES ('gramy');",
    "INSERT OR IGNORE INTO units (name) VALUES ('mililitry');",
    "INSERT OR IGNORE INTO units (name) VALUES ('sztuki');",
)


def apply_statements(cursor, statements: Iterable[SchemaStatement]) -> None:
    """Run the provided schema statements in order."""

    for statement in statements:
        try:
            cursor.executescript(statement.sql)
        except Exception as exc:  # pragma: no cover - defensive log hook
            if not statement.idempotent:
                raise
            # When idempotent and failure occurs (e.g., already exists), we swallow the error.
            # In production we would log this scenario for diagnostics.
            _ = exc


def initialize_schema(cursor) -> None:
    """Ensure tables, indexes, triggers, and seed data exist."""

    apply_statements(cursor, SCHEMA_STATEMENTS)
    for query in SEED_QUERIES:
        cursor.execute(query)
