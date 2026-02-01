# Plan Testów dla Aplikacji MealPlanner

## 1. Wprowadzenie i cele testowania

### 1.1. Wprowadzenie
Niniejszy dokument określa plan testów dla aplikacji desktopowej MealPlanner. Aplikacja, zbudowana przy użyciu Python z biblioteką Tkinter oraz bazą danych SQLite, ma na celu uproszczenie procesu planowania posiłków i generowania list zakupów. Plan ten obejmuje strategię, zakres, zasoby i harmonogram działań testowych mających na celu zapewnienie jakości, funkcjonalności i niezawodności produktu końcowego.

### 1.2. Cele testowania
Głównym celem jest weryfikacja, czy aplikacja MealPlanner spełnia wszystkie wymagania funkcjonalne i niefunkcjonalne opisane w dokumentacji projektu (PRD).

**Cele szczegółowe:**
*   Zapewnienie stabilności i poprawności działania kluczowych modułów: zarządzania profilami, przepisami, generowania planu posiłków i listy zakupów.
*   Weryfikacja integralności i poprawności operacji na bazie danych SQLite.
*   Sprawdzenie intuicyjności i responsywności interfejsu użytkownika (UI) zbudowanego w Tkinter.
*   Identyfikacja i zaraportowanie defektów w celu ich naprawy przed wdrożeniem.
*   Potwierdzenie, że aplikacja jest gotowa do użytku, zgodnie z zdefiniowanymi kryteriami akceptacji.

## 2. Zakres testów

### 2.1. Funkcjonalności objęte testami
*   **Zarządzanie profilami:** Tworzenie, logowanie, walidacja unikalności nazw, obsługa błędnych haseł.
*   **Zarządzanie przepisami:** Dodawanie, edycja, usuwanie przepisów; walidacja formularzy; obsługa kategorii i składników.
*   **Generowanie planu posiłków:** Automatyczne tworzenie planu na 7 dni, obsługa warunków brzegowych (brak przepisów), losowość i unikanie powtórzeń.
*   **Edycja planu posiłków:** Ręczna zmiana posiłków w wygenerowanym planie.
*   **Generowanie listy zakupów:** Automatyczne tworzenie skonsolidowanej i posortowanej listy na podstawie planu, sumowanie ilości, obsługa jednostek.
*   **Nawigacja i przepływ użytkownika:** Przejścia między widokami (`LoginView`, `MainView`, `RecipeListView`, `RecipeFormView`), obsługa wylogowania.

### 2.2. Funkcjonalności wyłączone z testów
Zgodnie z dokumentem PRD, następujące elementy są poza zakresem testów dla wersji MVP:
*   Obliczanie wartości odżywczych i cen.
*   Funkcje społecznościowe i synchronizacja online.
*   Śledzenie postępów w realizacji planu/listy.
*   Zaawansowane ustawienia aplikacji (np. zmiana motywu).
*   Drukowanie i eksport danych.

## 3. Typy testów do przeprowadzenia

*   **Testy jednostkowe (Unit Tests):** Skoncentrowane na weryfikacji pojedynczych komponentów w izolacji, głównie logiki biznesowej w `database/controller.py` oraz funkcji pomocniczych.
*   **Testy integracyjne (Integration Tests):** Weryfikacja współpracy między modułami, np. interakcji `ViewController` z poszczególnymi widokami (`*View.py`) oraz komunikacji widoków z `DatabaseController`.
*   **Testy systemowe (System/E2E Tests):** Kompleksowa weryfikacja działania całej aplikacji z perspektywy użytkownika końcowego. Testy te będą symulować rzeczywiste scenariusze użytkowania, od założenia konta po wygenerowanie listy zakupów.
*   **Testy manualne (Manual Tests):** Ręczne przeklikiwanie aplikacji w celu oceny użyteczności (UX), czytelności interfejsu oraz weryfikacji scenariuszy trudnych do zautomatyzowania.

## 4. Scenariusze testowe dla kluczowych funkcjonalności

### Scenariusz 1: Pełny cykl nowego użytkownika
1.  **Krok 1:** Uruchom aplikację. Sprawdź, czy widok logowania (`LoginView`) jest widoczny.
2.  **Krok 2:** Utwórz nowy profil, podając unikalną nazwę i hasło. Sprawdź, czy nastąpiło automatyczne zalogowanie i przejście do widoku powitalnego (`WelcomeView`).
3.  **Krok 3:** Przejdź do widoku przepisów (`RecipeListView`). Sprawdź, czy lista jest pusta.
4.  **Krok 4:** Dodaj 3 nowe przepisy, po jednym dla każdej kategorii (śniadanie, obiad, kolacja), wypełniając wszystkie pola w `RecipeFormView`.
5.  **Krok 5:** Wróć do widoku głównego (`MainView`). Sprawdź, czy widoczny jest pusty plan posiłków (`MealPlanView`).
6.  **Krok 6:** Kliknij "Wygeneruj plan". Potwierdź operację. Sprawdź, czy plan został wypełniony, a w panelu bocznym pojawiła się poprawnie wygenerowana lista zakupów (`ShoppingListView`).
7.  **Krok 7:** Wyloguj się. Sprawdź, czy aplikacja powróciła do widoku logowania.

### Scenariusz 2: Logowanie i modyfikacja danych
1.  **Krok 1:** Uruchom aplikację. Wybierz istniejący profil z listy.
2.  **Krok 2:** Podaj nieprawidłowe hasło. Sprawdź, czy wyświetlony został komunikat o błędzie.
3.  **Krok 3:** Podaj prawidłowe hasło. Sprawdź, czy nastąpiło zalogowanie i załadowanie danych użytkownika.
4.  **Krok 4:** Przejdź do listy przepisów i edytuj jeden z nich, zmieniając składniki.
5.  **Krok 5:** Wróć do widoku głównego i ponownie wygeneruj plan. Sprawdź, czy lista zakupów została zaktualizowana zgodnie ze zmianami w przepisie.

### Scenariusz 3: Obsługa przypadków brzegowych
1.  **Krok 1:** Utwórz nowy profil i spróbuj wygenerować plan bez dodawania żadnych przepisów. Sprawdź, czy aplikacja wyświetla odpowiedni komunikat i blokuje operację.
2.  **Krok 2:** Dodaj przepis tylko dla jednej kategorii (np. śniadanie) i spróbuj wygenerować plan. Sprawdź reakcję systemu.
3.  **Krok 3:** W widoku `RecipeFormView` spróbuj zapisać przepis bez nazwy lub bez wybranej kategorii. Sprawdź, czy walidacja formularza działa poprawnie.
4.  **Krok 4:** Usuń przepis, który jest aktualnie używany w planie. Sprawdź, czy pojawia się okno dialogowe z ostrzeżeniem, a po potwierdzeniu posiłek w planie zostaje zastąpiony lub oznaczony jako pusty.

## 5. Środowisko testowe
*   **System operacyjny:** Linux (zgodnie ze środowiskiem deweloperskim).
*   **Wersja Python:** Zgodna z `requirements.txt`.
*   **Baza danych:** Czysta instancja bazy danych SQLite generowana przed każdą sesją testów automatycznych w celu zapewnienia izolacji.
*   **Zależności:** Wszystkie biblioteki zdefiniowane w pliku `requirements.txt`.

## 6. Narzędzia do testowania
*   **Testy jednostkowe i integracyjne:** `unittest` (wbudowany w Python) lub `pytest`.
*   **Testy E2E (opcjonalnie, w zależności od budżetu):** Narzędzia do automatyzacji GUI dla aplikacji desktopowych, np. `PyAutoGUI` (dla prostszych scenariuszy) lub dedykowane frameworki.
*   **Zarządzanie testami i raportowanie błędów:** Narzędzia takie jak Jira, TestRail lub proste dokumenty w repozytorium (np. pliki Markdown w dedykowanym folderze `tests/reports`).

## 7. Harmonogram testów
Proces testowy będzie prowadzony równolegle z fazą deweloperską (ciągła integracja).
*   **Tydzień 1:** Przygotowanie środowiska testowego, konfiguracja narzędzi, implementacja testów jednostkowych dla logiki bazy danych (`DatabaseController`).
*   **Tydzień 2:** Implementacja testów integracyjnych dla kluczowych widoków i `ViewController`. Rozpoczęcie manualnych testów eksploracyjnych.
*   **Tydzień 3:** Przeprowadzenie pełnej tury testów systemowych (E2E) według zdefiniowanych scenariuszy. Testy regresji po wprowadzonych poprawkach.
*   **Tydzień 4:** Finalne testy akceptacyjne, weryfikacja kryteriów wyjścia i przygotowanie raportu końcowego.

## 8. Kryteria akceptacji testów

### 8.1. Kryteria wejścia
*   Zakończono implementację funkcjonalności przewidzianych dla wersji MVP.
*   Aplikacja pomyślnie się kompiluje i uruchamia.
*   Dostępna jest kompletna dokumentacja techniczna i produktowa.

### 8.2. Kryteria wyjścia
*   Wszystkie zaplanowane testy jednostkowe i integracyjne kończą się sukcesem (100% pass).
*   Wszystkie krytyczne i poważne błędy zidentyfikowane podczas testów zostały naprawione i zweryfikowane.
*   Scenariusze testów systemowych dla kluczowych funkcjonalności kończą się sukcesem.
*   Brak znanych błędów blokujących podstawowy przepływ użytkownika.

## 9. Role i odpowiedzialności
*   **Inżynier QA (Test Lead):** Odpowiedzialny za stworzenie i utrzymanie planu testów, projektowanie scenariuszy, nadzór nad procesem testowym, raportowanie statusu i wyników.
*   **Deweloperzy:** Odpowiedzialni za pisanie testów jednostkowych dla swojego kodu, naprawę zgłoszonych błędów oraz wsparcie w diagnozowaniu problemów.
*   **Project Manager:** Nadzór nad harmonogramem, priorytetyzacja błędów we współpracy z QA i zespołem deweloperskim.

## 10. Procedury raportowania błędów
Każdy zidentyfikowany błąd musi zostać zaraportowany w systemie do śledzenia błędów i zawierać następujące informacje:
*   **Tytuł:** Zwięzły opis problemu.
*   **Środowisko:** Wersja aplikacji, system operacyjny.
*   **Kroki do odtworzenia:** Szczegółowa, numerowana lista kroków prowadzących do wystąpienia błędu.
*   **Wynik oczekiwany:** Co powinno się wydarzyć.
*   **Wynik rzeczywisty:** Co faktycznie się wydarzyło.
*   **Priorytet/Waga:** (np. Krytyczny, Poważny, Drobny) w celu ułatwienia priorytetyzacji.
*   **Załączniki:** Zrzuty ekranu, logi lub krótkie nagrania wideo.
