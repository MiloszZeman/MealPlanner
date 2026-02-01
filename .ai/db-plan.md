# Schemat Bazy Danych SQLite - MealPlanner MVP

## 1. Tabele z kolumnami, typami danych i ograniczeniami

### 1.1. Tabela `users`
Przechowuje profile użytkowników aplikacji.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Kolumny:**
- `id` - Klucz główny, auto-inkrementowany
- `profile_name` - Unikalna nazwa profilu (case-insensitive)
- `password_hash` - Hash hasła użytkownika (Argon2/bcrypt/scrypt)
- `created_at` - Data utworzenia konta (format: YYYY-MM-DD HH:MM:SS)

**Ograniczenia:**
- `UNIQUE` na `profile_name` z `COLLATE NOCASE`
- `NOT NULL` na wszystkich kolumnach poza `id`

---

### 1.2. Tabela `meal_categories`
Słownik kategorii posiłków.

```sql
CREATE TABLE meal_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    display_order INTEGER NOT NULL
);

-- Dane początkowe (seed data)
INSERT INTO meal_categories (name, display_order) VALUES 
    ('Śniadanie', 1),
    ('Obiad', 2),
    ('Kolacja', 3);
```

**Kolumny:**
- `id` - Klucz główny, auto-inkrementowany
- `name` - Nazwa kategorii
- `display_order` - Kolejność wyświetlania (1=śniadanie, 2=obiad, 3=kolacja)

**Ograniczenia:**
- `UNIQUE` na `name`
- `NOT NULL` na wszystkich kolumnach poza `id`

---

### 1.3. Tabela `units`
Słownik jednostek miar dla składników.

```sql
CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Dane początkowe (seed data)
INSERT INTO units (name) VALUES 
    ('gramy'),
    ('mililitry'),
    ('sztuki');
```

**Kolumny:**
- `id` - Klucz główny, auto-inkrementowany
- `name` - Nazwa jednostki

**Ograniczenia:**
- `UNIQUE` na `name`
- `NOT NULL` na `name`

---

### 1.4. Tabela `ingredients`
Globalna lista składników.

```sql
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);
```

**Kolumny:**
- `id` - Klucz główny, auto-inkrementowany
- `name` - Nazwa składnika (case-insensitive, unikalna)

**Ograniczenia:**
- `UNIQUE` na `name` z `COLLATE NOCASE`
- `NOT NULL` na `name`

---

### 1.5. Tabela `recipes`
Przepisy kulinarne użytkowników.

```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, name)
);
```

**Kolumny:**
- `id` - Klucz główny, auto-inkrementowany
- `user_id` - Klucz obcy do tabeli `users`
- `name` - Nazwa przepisu (unikalna w ramach użytkownika)
- `created_at` - Data utworzenia przepisu
- `updated_at` - Data ostatniej modyfikacji

**Ograniczenia:**
- `FOREIGN KEY` do `users` z `ON DELETE CASCADE`
- `UNIQUE` na parze (`user_id`, `name`)
- `NOT NULL` na wszystkich kolumnach poza `id`

---

### 1.6. Tabela `recipe_meal_categories`
Tabela łącząca przepisy z kategoriami posiłków (relacja wiele-do-wielu).

```sql
CREATE TABLE recipe_meal_categories (
    recipe_id INTEGER NOT NULL,
    meal_category_id INTEGER NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (meal_category_id) REFERENCES meal_categories(id) ON DELETE RESTRICT,
    PRIMARY KEY (recipe_id, meal_category_id)
);
```

**Kolumny:**
- `recipe_id` - Klucz obcy do tabeli `recipes`
- `meal_category_id` - Klucz obcy do tabeli `meal_categories`

**Ograniczenia:**
- Klucz złożony `PRIMARY KEY` na (`recipe_id`, `meal_category_id`)
- `FOREIGN KEY` do `recipes` z `ON DELETE CASCADE`
- `FOREIGN KEY` do `meal_categories` z `ON DELETE RESTRICT`
- `NOT NULL` na obu kolumnach

---

### 1.7. Tabela `recipe_ingredients`
Tabela łącząca przepisy ze składnikami (relacja wiele-do-wielu z dodatkowymi atrybutami).

```sql
CREATE TABLE recipe_ingredients (
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
```

**Kolumny:**
- `id` - Klucz główny, auto-inkrementowany
- `recipe_id` - Klucz obcy do tabeli `recipes`
- `ingredient_id` - Klucz obcy do tabeli `ingredients`
- `quantity` - Ilość składnika (może być NULL dla ilości symbolicznej)
- `unit_id` - Klucz obcy do tabeli `units`
- `is_symbolic` - Flaga określająca, czy ilość jest symboliczna (0 lub 1)
- `display_order` - Opcjonalna kolejność wyświetlania składników

**Ograniczenia:**
- `FOREIGN KEY` do `recipes` z `ON DELETE CASCADE`
- `FOREIGN KEY` do `ingredients` z `ON DELETE RESTRICT`
- `FOREIGN KEY` do `units` z `ON DELETE RESTRICT`
- `NOT NULL` na wszystkich kolumnach poza `id`, `quantity` i `display_order`
- `quantity` może być `NULL` gdy `is_symbolic = 1`

---

### 1.8. Tabela `meal_plan`
Plan posiłków na 7 dni dla użytkowników.

```sql
CREATE TABLE meal_plan (
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
```

**Kolumny:**
- `id` - Klucz główny, auto-inkrementowany
- `user_id` - Klucz obcy do tabeli `users`
- `date` - Data posiłku (format: YYYY-MM-DD)
- `meal_category_id` - Klucz obcy do tabeli `meal_categories`
- `recipe_id` - Klucz obcy do tabeli `recipes` (może być NULL)

**Ograniczenia:**
- `FOREIGN KEY` do `users` z `ON DELETE CASCADE`
- `FOREIGN KEY` do `meal_categories` z `ON DELETE RESTRICT`
- `FOREIGN KEY` do `recipes` z `ON DELETE SET NULL`
- `UNIQUE` na (`user_id`, `date`, `meal_category_id`)
- `NOT NULL` na wszystkich kolumnach poza `id` i `recipe_id`

---

## 2. Relacje między tabelami

### 2.1. Relacje jeden-do-wielu

**users → recipes** (1:N)
- Jeden użytkownik może mieć wiele przepisów
- Klucz obcy: `recipes.user_id` → `users.id`
- Kaskadowe usuwanie: usunięcie użytkownika usuwa wszystkie jego przepisy

**users → meal_plan** (1:N)
- Jeden użytkownik może mieć wiele wpisów w planie
- Klucz obcy: `meal_plan.user_id` → `users.id`
- Kaskadowe usuwanie: usunięcie użytkownika usuwa jego plan

### 2.2. Relacje wiele-do-wielu

**recipes ↔ meal_categories** (N:M)
- Przepis może należeć do wielu kategorii (śniadanie + obiad)
- Kategoria może zawierać wiele przepisów
- Tabela łącząca: `recipe_meal_categories`
- Ochrona: nie można usunąć kategorii przypisanej do przepisów

**recipes ↔ ingredients** (N:M)
- Przepis może zawierać wiele składników
- Składnik może być używany w wielu przepisach
- Tabela łącząca: `recipe_ingredients` (z dodatkowymi atrybutami: quantity, unit_id)
- Ochrona: nie można usunąć składnika używanego w przepisach

### 2.3. Relacje z obsługą NULL

**meal_plan → recipes** (N:1, nullable)
- Wpis w planie może być pusty (NULL) gdy przepis został usunięty
- `ON DELETE SET NULL` pozwala na "opróżnienie" komórki w planie
- Aplikacja musi obsłużyć NULL jako "wymaga uzupełnienia"

---

## 3. Indeksy

### 3.1. Indeksy dla optymalizacji wydajności

```sql
-- Indeks na nazwie profilu dla szybkiego logowania
CREATE INDEX idx_users_profile_name ON users(profile_name);

-- Indeksy na kluczach obcych dla JOIN operations
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_recipe_meal_categories_recipe_id ON recipe_meal_categories(recipe_id);
CREATE INDEX idx_recipe_meal_categories_meal_category_id ON recipe_meal_categories(meal_category_id);
CREATE INDEX idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id);
CREATE INDEX idx_meal_plan_user_id ON meal_plan(user_id);
CREATE INDEX idx_meal_plan_recipe_id ON meal_plan(recipe_id);
CREATE INDEX idx_meal_plan_date ON meal_plan(date);

-- Indeks na nazwie przepisu dla szybkiego wyszukiwania
CREATE INDEX idx_recipes_name ON recipes(name);

-- Indeks na nazwie składnika dla szybkiego wyszukiwania
CREATE INDEX idx_ingredients_name ON ingredients(name);

-- Indeks złożony dla zapytań o plan użytkownika w konkretnym dniu
CREATE INDEX idx_meal_plan_user_date ON meal_plan(user_id, date);
```

### 3.2. Uzasadnienie indeksów

- **idx_users_profile_name**: Przyspiesza logowanie (sprawdzanie unikalności i wyszukiwanie)
- **idx_recipes_user_id**: Optymalizuje listowanie przepisów użytkownika
- **idx_meal_plan_user_date**: Kluczowy dla wyświetlania planu tygodniowego
- **idx_recipe_ingredients_***: Przyspieszają generowanie listy zakupów
- **Indeksy na kluczach obcych**: Optymalizują operacje JOIN i egzekwowanie integralności referencyjnej

---

## 4. Zasady bezpieczeństwa (RLS)

**SQLite nie wspiera natywnie Row Level Security (RLS)** jak PostgreSQL. Bezpieczeństwo na poziomie wiersza musi być zaimplementowane w logice aplikacji:

### 4.1. Zasady bezpieczeństwa aplikacji

**Izolacja danych użytkowników:**
```python
# Wszystkie zapytania muszą filtrować po user_id
SELECT * FROM recipes WHERE user_id = :current_user_id;
SELECT * FROM meal_plan WHERE user_id = :current_user_id;
```

**Hashowanie haseł:**
- Użycie Argon2, bcrypt lub scrypt przed zapisem do `users.password_hash`
- Weryfikacja hasła przy logowaniu poprzez porównanie hashy

**Walidacja po stronie aplikacji:**
- Sprawdzenie, czy użytkownik ma uprawnienia do modyfikacji przepisu/planu
- Blokowanie dostępu do danych innych użytkowników
- Walidacja unikalności nazw przed INSERT/UPDATE

---

## 5. Dodatkowe uwagi i decyzje projektowe

### 5.1. Normalizacja
Schemat jest znormalizowany do **3NF (Third Normal Form)**:
- Eliminacja redundancji danych (składniki i kategorie w osobnych tabelach)
- Separacja encji biznesowych (users, recipes, ingredients)
- Brak transytywnych zależności

### 5.2. Denormalizacja
Świadome odstępstwa od pełnej normalizacji:
- **Brak tabeli dla listy zakupów** - generowana dynamicznie z `meal_plan` i `recipe_ingredients`
- **display_order w meal_categories** - dla zachowania stałego porządku sortowania

### 5.3. Typy danych SQLite
- **INTEGER** - dla ID, liczb całkowitych, flag boolowskich
- **TEXT** - dla napisów (SQLite nie ma VARCHAR)
- **REAL** - dla ilości składników (liczby zmiennoprzecinkowe)
- **TEXT dla dat** - format ISO 8601 (YYYY-MM-DD lub YYYY-MM-DD HH:MM:SS)

### 5.4. Obsługa CURRENT_TIMESTAMP
SQLite używa `CURRENT_TIMESTAMP` dla automatycznego timestampingu.

### 5.5. Brak soft delete
Zgodnie z decyzjami z sesji planowania, MVP nie implementuje soft delete - wszystkie usunięcia są fizyczne (hard delete).

### 5.6. Trigger dla updated_at
Opcjonalnie można dodać trigger do automatycznej aktualizacji `updated_at`:

```sql
CREATE TRIGGER update_recipes_timestamp 
AFTER UPDATE ON recipes
FOR EACH ROW
BEGIN
    UPDATE recipes SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;
```

### 5.7. Generowanie listy zakupów
Lista zakupów jest generowana dynamicznie zapytaniem SQL:

```sql
SELECT 
    i.name AS ingredient_name,
    CASE 
        WHEN ri.is_symbolic = 1 THEN NULL 
        ELSE SUM(ri.quantity) 
    END AS total_quantity,
    u.name AS unit_name
FROM meal_plan mp
JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
JOIN ingredients i ON ri.ingredient_id = i.id
JOIN units u ON ri.unit_id = u.id
WHERE mp.user_id = :user_id 
  AND mp.date BETWEEN :start_date AND :end_date
GROUP BY i.id, ri.is_symbolic, u.id
ORDER BY i.name ASC;
```

### 5.8. Migracje
Schemat jest gotowy do utworzenia poprzez wykonanie kolejnych instrukcji `CREATE TABLE` i `INSERT` w podanej kolejności.

---

**Wersja:** 1.0  
**Data:** 2026-02-01  
**Status:** Zatwierdzony do implementacji MVP
