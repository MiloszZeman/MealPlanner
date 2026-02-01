<conversation_summary> <dec

isions>

Klucze główne we wszystkich tabelach będą typu INTEGER PRIMARY KEY dla zapewnienia auto-inkrementacji i wydajności.
Profile użytkowników (users) będą usuwane kaskadowo (ON DELETE CASCADE), co spowoduje automatyczne usunięcie wszystkich powiązanych z nimi danych (przepisów, planów).
Nazwy w tabelach meal_categories i units będą unikalne (UNIQUE), aby zapobiec duplikatom.
Tabele meal_categories i units zostaną wstępnie wypełnione danymi: ('Śniadanie', 'Obiad', 'Kolacja') oraz ('gramy', 'mililitry', 'sztuki').
Tabela recipe_ingredients pozwoli na wielokrotne dodanie tego samego składnika do jednego przepisu.
Kolejność wyświetlania kategorii posiłków (Śniadanie, Obiad, Kolacja) będzie zarządzana przez dedykowaną kolumnę display_order w tabeli meal_categories.
Nazwy składników w tabeli ingredients będą porównywane bez uwzględniania wielkości liter (COLLATE NOCASE), aby uniknąć duplikatów.
Wszystkie kluczowe kolumny (klucze obce, nazwy, hasła) będą miały ograniczenie NOT NULL, z wyjątkiem recipe_id w tabeli meal_plan.
Pary recipe_id i meal_category_id w tabeli łączącej recipe_meal_categories będą unikalne, aby zapobiec wielokrotnemu przypisaniu tej samej kategorii do przepisu.
Usunięcie kategorii posiłku, która jest w użyciu, zostanie zablokowane przez ograniczenie ON DELETE RESTRICT.</decisions>
<matched_recommendations> 1. Zalecenie utworzenia tabeli łączącej `recipe_categories` w celu obsługi relacji wiele-do-wielu między przepisami a kategoriami. 2. Rekomendacja przechowywania haseł w postaci hashy, a nie czystego tekstu. 3. Zalecenie utworzenia dedykowanych tabel `units` i `meal_categories` dla większej elastyczności. 4. Rekomendacja dopuszczenia wartości `NULL` w kolumnie `quantity` dla składników o "ilości symbolicznej". 5. Zalecenie użycia `ON DELETE SET NULL` w tabeli `meal_plan`, aby obsłużyć usuwanie przepisów będących częścią planu. 6. Rekomendacja utworzenia globalnej tabeli `ingredients` w celu ułatwienia agregacji na liście zakupów. 7. Zalecenie dodania kolumn `created_at` i `updated_at` do kluczowych tabel (`users`, `recipes`) jako dobra praktyka na przyszłość. 8. Rekomendacja zastosowania kaskadowego usuwania (`ON DELETE CASCADE`) dla danych użytkownika w celu zachowania integralności bazy danych. </dmatched_recommendations> <database_planning_summary> Na podstawie wymagań dla MVP aplikacji MealPlanner, zaplanowano schemat relacyjnej bazy danych SQLite. Celem jest obsługa kluczowych funkcjonalności w trybie offline, w tym zarządzania profilami, przepisami, generowania planów żywieniowych i list zakupów.

Główne wymagania dotyczące schematu:
Schemat musi wspierać tworzenie wielu profili użytkowników, dodawanie przepisów z listą składników, przypisywanie przepisów do wielu kategorii, generowanie 7-dniowego planu posiłków oraz skonsolidowanej listy zakupów. Baza danych musi być spójna i zoptymalizowana pod kątem typowych operacji.

Kluczowe encje i ich relacje:

Users: Przechowuje profile użytkowników. Ma relację jeden-do-wielu z Recipes i Meal_Plan.
Recipes: Główna encja dla przepisów. Ma relację wiele-do-wielu z Meal_Categories (przez tabelę Recipe_Meal_Categories) oraz Ingredients (przez tabelę Recipe_Ingredients).
Ingredients: Globalna tabela składników.
Meal_Categories: Tabela słownikowa dla kategorii posiłków (np. Śniadanie).
Units: Tabela słownikowa dla jednostek miar (np. gramy).
Meal_Plan: Przechowuje wygenerowany plan, łącząc Users, Recipes i Meal_Categories dla konkretnej daty.
Ważne kwestie dotyczące bezpieczeństwa i wydajności:

Bezpieczeństwo: Hasła użytkowników będą hashowane po stronie aplikacji przed zapisaniem w bazie danych. Usunięcie kategorii w użyciu będzie blokowane, aby chronić integralność danych.
Wydajność i skalowalność: We wszystkich tabelach jako klucze główne zostaną użyte INTEGER PRIMARY KEY. Indeksy zostaną założone na kluczach obcych oraz często przeszukiwanych kolumnach (np. nazwa profilu, nazwa przepisu) w celu przyspieszenia zapytań. Dynamiczne generowanie listy zakupów zamiast jej przechowywania upraszcza model i zmniejsza redundancję danych.
</database_planning_summary> <unresolved_issues> 1. **Wybór algorytmu hashowania**: Należy podjąć ostateczną decyzję co do konkretnego algorytmu hashowania haseł (np. Argon2, scrypt, bcrypt), który zostanie zaimplementowany w logice aplikacji w Pythonie. </unresolved_issues> </conversation_summary>