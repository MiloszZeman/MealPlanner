# Architektura UI dla MealPlanner

## 1. Przegląd struktury UI

Architektura interfejsu użytkownika (UI) aplikacji MealPlanner opiera się na podejściu "Single-Page Application" (SPA), zaimplementowanym w technologii Python/Tkinter. Centralnym elementem jest kontroler widoków (`ViewController`), który zarządza cyklem życia poszczególnych ekranów (widoków) w głównym oknie aplikacji. Takie podejście eliminuje potrzebę przeładowywania całego okna, zapewniając płynne przejścia między różnymi sekcjami aplikacji, takimi jak logowanie, zarządzanie przepisami czy przeglądanie planu posiłków.

Główny interfejs po zalogowaniu jest podzielony na dwa regulowane panele za pomocą widżetu `PanedWindow`:
1.  **Panel Główny (ok. 75% szerokości):** Domyślnie wyświetla tygodniowy plan posiłków.
2.  **Panel Boczny (ok. 25% szerokości):** Służy do prezentacji wygenerowanej listy zakupów.

Nawigacja jest kontekstowa i opiera się na akcjach użytkownika (np. kliknięcie przycisku "Moje przepisy"), które instruują `ViewController` do przełączenia widoku w panelu głównym. Architektura kładzie nacisk na hermetyzację logiki, responsywność układu oraz obsługę operacji na bazie danych w osobnych wątkach, aby zapewnić płynność działania interfejsu.

## 2. Lista widoków

### Widok 1: Ekran Startowy (Logowanie i Rejestracja)
- **Nazwa widoku:** `LoginView`
- **Ścieżka widoku:** `/` (widok początkowy)
- **Główny cel:** Umożliwienie użytkownikowi zalogowania się do istniejącego profilu lub utworzenia nowego.
- **Kluczowe informacje do wyświetlenia:** Lista istniejących profili użytkowników.
- **Kluczowe komponenty widoku:**
    - Lista rozwijana z nazwami profili.
    - Pole do wprowadzania hasła.
    - Przycisk "Zaloguj".
    - Przycisk "Utwórz konto", który odsłania (a po aktywacji pozwala ukryć przyciskiem "Anuluj") formularz rejestracji w tym samym widoku.
    - Formularz tworzenia profilu (pola: Nazwa profilu, Hasło, Powtórz hasło) renderowany dynamicznie po kliknięciu i początkowo ukryty.
    - Etykiety do wyświetlania błędów walidacji (np. "Profil o tej nazwie już istnieje.", "Nieprawidłowe hasło.").
- **UX, dostępność i względy bezpieczeństwa:**
    - **UX:** Prosty, jednoznaczny ekran startowy. Pole hasła aktywuje się po wybraniu profilu.
    - **Dostępność:** Wyraźne etykiety i komunikaty o błędach.
    - **Bezpieczeństwo:** Hasło jest maskowane. Komunikaty o błędach logowania są ogólne ("Nieprawidłowe hasło"), aby nie ujawniać, czy problemem jest nazwa użytkownika czy hasło.

### Widok 2: Główny Widok Aplikacji (Dashboard)
- **Nazwa widoku:** `MainView`
- **Ścieżka widoku:** `/dashboard`
- **Główny cel:** Prezentacja tygodniowego planu posiłków oraz zapewnienie dostępu do kluczowych funkcji (generowanie planu, lista zakupów, zarządzanie przepisami).
- **Kluczowe informacje do wyświetlenia:**
    - Tabela 7x3 z posiłkami na każdy dzień tygodnia.
    - Lista zakupów w panelu bocznym.
    - Komunikat powitalny dla nowych użytkowników.
- **Kluczowe komponenty widoku:**
    - Pasek nawigacyjny z przyciskami "Moje przepisy", "Wyloguj".
    - Przycisk "Wygeneruj plan".
    - Widok Planu Tygodniowego (`MealPlanView`) jako główny komponent.
    - Panel Boczny Listy Zakupów (`ShoppingListView`).
    - Widok Powitalny (`WelcomeView`) dla nowych użytkowników, wyświetlany zamiast `MealPlanView`.
- **UX, dostępność i względy bezpieczeństwa:**
    - **UX:** Centralny punkt aplikacji. Długotrwałe operacje (generowanie planu) sygnalizowane są zmianą kursora.
    - **Dostępność:** Czytelna struktura tabelaryczna, wyraźne przyciski.
    - **Bezpieczeństwo:** Wszystkie dane (plan, przepisy) są filtrowane i należą wyłącznie do zalogowanego użytkownika.

### Widok 3: Zarządzanie Przepisami
- **Nazwa widoku:** `RecipeListView`
- **Ścieżka widoku:** `/recipes`
- **Główny cel:** Umożliwienie użytkownikowi przeglądania, dodawania, edytowania i usuwania swoich przepisów.
- **Kluczowe informacje do wyświetlenia:** Lista wszystkich przepisów użytkownika.
- **Kluczowe komponenty widoku:**
    - Przycisk "Dodaj nowy przepis".
    - Lista przepisów, gdzie każdy element zawiera:
        - Nazwę przepisu.
        - Przyciski "Edytuj" i "Usuń".
    - Przycisk "Powrót" do głównego widoku.
- **UX, dostępność i względy bezpieczeństwa:**
    - **UX:** Prosta i przejrzysta lista. Usuwanie przepisów używanych w planie wymaga dodatkowego potwierdzenia w oknie dialogowym.
    - **Dostępność:** Każdy element listy ma jasno oznaczone akcje.
    - **Bezpieczeństwo:** Użytkownik ma dostęp tylko do własnych przepisów.

### Widok 4: Formularz Przepisu (Dodawanie/Edycja)
- **Nazwa widoku:** `RecipeFormView`
- **Ścieżka widoku:** `/recipes/new` lub `/recipes/edit/{id}`
- **Główny cel:** Stworzenie nowego przepisu lub modyfikacja istniejącego.
- **Kluczowe informacje do wyświetlenia:** Pola do wprowadzenia nazwy, kategorii i składników przepisu.
- **Kluczowe komponenty widoku:**
    - Pole tekstowe na nazwę przepisu.
    - Checkboxy dla kategorii (Śniadanie, Obiad, Kolacja).
    - Dynamiczna lista składników, gdzie każdy wiersz (`IngredientRow`) zawiera:
        - Pole tekstowe na nazwę składnika.
        - Pole numeryczne na ilość.
        - Lista rozwijana z jednostkami (gramy, mililitry, sztuki).
        - Checkbox "Ilość symboliczna".
        - Przycisk do usunięcia wiersza.
    - Przycisk "+ Dodaj składnik" do dodawania nowych wierszy.
    - Przyciski "Zapisz" i "Anuluj".
    - Etykiety do wyświetlania błędów walidacji.
- **UX, dostępność i względy bezpieczeństwa:**
    - **UX:** Dynamiczne dodawanie i usuwanie składników upraszcza proces. Walidacja "na żywo" lub przy próbie zapisu informuje o brakujących danych.
    - **Dostępność:** Wszystkie pola formularza są jasno opisane.
    - **Bezpieczeństwo:** Walidacja danych wejściowych po stronie aplikacji zapobiega zapisowi niekompletnych lub niepoprawnych danych.

## 3. Mapa podróży użytkownika

Główny przypadek użycia (od zera do listy zakupów):

1.  **Start (`LoginView`):** Nowy użytkownik klika "Stwórz nowy profil", wypełnia formularz i zostaje zalogowany.
2.  **Ekran powitalny (`MainView` -> `WelcomeView`):** Użytkownik widzi komunikat powitalny i jest kierowany do dodania przepisów. Klika przycisk "Przejdź do przepisów".
3.  **Zarządzanie przepisami (`RecipeListView`):** Widok jest pusty. Użytkownik klika "Dodaj nowy przepis".
4.  **Tworzenie przepisu (`RecipeFormView`):** Użytkownik wypełnia dane dla pierwszego przepisu (np. śniadanie), dodaje składniki i klika "Zapisz".
5.  **Powrót do listy (`RecipeListView`):** Nowy przepis jest widoczny na liście. Użytkownik powtarza kroki 3-4, aby dodać co najmniej po jednym przepisie dla obiadu i kolacji.
6.  **Powrót do Dashboardu (`MainView`):** Po dodaniu przepisów użytkownik wraca do głównego widoku, gdzie teraz widoczna jest pusta tabela planu (`MealPlanView`).
7.  **Generowanie planu (`MainView`):** Użytkownik klika "Wygeneruj plan". Po potwierdzeniu w oknie dialogowym, tabela planu zostaje wypełniona losowymi posiłkami.
8.  **Generowanie listy zakupów (`MainView` -> `ShoppingListView`):** Jednocześnie z planem, w panelu bocznym automatycznie generowana jest skonsolidowana i posortowana lista zakupów.
9.  **Edycja planu (opcjonalnie, `MealPlanView`):** Użytkownik klika na wybrany posiłek w planie, co otwiera listę rozwijaną z innymi przepisami z tej samej kategorii. Wybiera inny przepis, a plan i lista zakupów automatycznie się aktualizują.

## 4. Układ i struktura nawigacji

Nawigacja w aplikacji jest scentralizowana i opiera się na `ViewController`, który działa jak maszyna stanów, przełączając widoki w głównym kontenerze.

- **Poziom 0 (Przed zalogowaniem):**
    - `LoginView` jest jedynym dostępnym widokiem.

- **Poziom 1 (Po zalogowaniu - `MainView`):**
    - Dostęp do `RecipeListView` poprzez przycisk "Moje przepisy".
    - Dostęp do `LoginView` poprzez przycisk "Wyloguj" (reset stanu aplikacji).

- **Poziom 2 (Zarządzanie danymi):**
    - Z `RecipeListView` można przejść do `RecipeFormView` (dodawanie/edycja).
    - Z `RecipeFormView` użytkownik wraca do `RecipeListView`.

Wszystkie widoki "podrzędne" (jak `RecipeListView` czy `RecipeFormView`) zawierają przycisk "Powrót" lub "Anuluj", który cofa użytkownika do poprzedniego stanu w hierarchii nawigacji.

## 5. Kluczowe komponenty

- **ViewController:** Centralna klasa zarządzająca przełączaniem widoków. Przechowuje stan aplikacji (np. ID zalogowanego użytkownika) i przekazuje go do odpowiednich widoków.
- **DatabaseController:** Hermetyzuje całą komunikację z bazą danych SQLite. Widoki UI komunikują się tylko z tym kontrolerem, a nie bezpośrednio z bazą.
- **MealPlanView:** Komponent w formie siatki (grid) 7x3, odpowiedzialny za wyświetlanie planu. Każda komórka umożliwia edycję posiłku. Posiada metodę `refresh()`, która odświeża jego zawartość.
- **ShoppingListView:** Komponent wyświetlający posortowaną listę zakupów. Posiada metodę `refresh(plan_data)`, która na nowo generuje listę na podstawie aktualnego planu.
- **IngredientRow:** Niestandardowy widżet (Frame) hermetyzujący logikę i pola jednego wiersza składnika w formularzu przepisu. Umożliwia łatwe, dynamiczne zarządzanie listą składników.
- **Modalne okna dialogowe (`tkinter.messagebox`):** Używane do uzyskiwania potwierdzeń krytycznych akcji, takich jak usuwanie danych czy nadpisywanie istniejącego planu.
