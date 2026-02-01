1. Zaimplementowany zostanie centralny kontroler widoków (view controller) do zarządzania nawigacją między ramkami (Frames). 2. Główny interfejs zostanie podzielony na dwie części (plan tygodniowy

i lista zakupów) za pomocą widżetu PanedWindow.
3. Zostanie stworzona dedykowana klasa IngredientRow do dynamicznego zarządzania polami składników w formularzu przepisów.
4. Responsywność interfejsu będzie zapewniona przez menedżery geometrii grid lub pack z opcjami weight i fill.
5. Dla nowych użytkowników, zamiast pustego planu, wyświetlony zostanie ekran powitalny z instrukcjami i przyciskiem do dodawania przepisów.
6. Walidacja formularzy będzie realizowana przy utracie fokusu lub zapisie, a błędy będą wyświetlane za pomocą dedykowanych etykiet.
7. Kwestia spójności wyglądu na różnych systemach operacyjnych (np. przez ttkthemes) jest na razie pomijana.
8. Długotrwałe operacje na bazie danych będą obsługiwane w osobnych wątkach, a interfejs będzie informował o stanie oczekiwania poprzez zmianę kursora.
9. Do obsługi potwierdzeń od użytkownika (np. usuwanie, generowanie planu) będą używane standardowe okna dialogowe z modułu tkinter.messagebox.
10. Zostanie stworzona centralna metoda refresh_meal_plan_view() do odświeżania widoku planu po każdej modyfikacji danych.
</decisions>
<matched_recommendations>

Implementacja centralnego kontrolera widoków do symulacji nawigacji jednostronicowej.
Użycie PanedWindow do stworzenia regulowanego, dwupanelowego układu dla planu i listy zakupów.
Hermetyzacja logiki wiersza składnika w dedykowanej klasie Frame w celu dynamicznego zarządzania formularzem.
Wykorzystanie menedżerów geometrii grid/pack do zapewnienia responsywności układu.
Stworzenie dedykowanego widoku startowego dla nowych użytkowników, kierującego ich do dodania pierwszych przepisów.
Implementacja walidacji w formularzach z wyświetlaniem komunikatów o błędach bezpośrednio w UI.
Użycie osobnych wątków dla operacji blokujących UI oraz zmiana kursora na "watch" w celu poprawy doświadczenia użytkownika.
Stosowanie modalnych okien dialogowych (tkinter.messagebox) do uzyskiwania potwierdzeń od użytkownika.
Stworzenie centralnej funkcji odświeżającej widok planu w celu zapewnienia spójności danych.</matched_recommendations> <ui_architecture_planning_summary> Na podstawie wymagań produktu (PRD) i specyfikacji technicznej (Python/Tkinter, SQLite) zaplanowano architekturę interfejsu użytkownika dla aplikacji MealPlanner.
a. Główne wymagania dotyczące architektury UI:
Architektura będzie oparta na podejściu "Single-Page Application", gdzie centralny kontroler widoków (ViewController) będzie zarządzał wyświetlaniem, tworzeniem i niszczeniem poszczególnych widoków ( ramek Frame) w głównym oknie aplikacji. Główny układ aplikacji zostanie podzielony na dwie regulowane sekcje za pomocą widżetu PanedWindow, co pozwoli na jednoczesne wyświetlanie planu tygodniowego i listy zakupów.

b. Kluczowe widoki, ekrany i przepływy użytkownika:
Zidentyfikowano następujące kluczowe widoki i przepływy:

Widok Logowania/Tworzenia Profilu: Ekran startowy z listą profili, logowaniem i opcją tworzenia nowego konta.
Główny Widok Aplikacji: Po zalogowaniu użytkownik trafia tutaj. Widok ten zawiera:
Widok Planu Tygodniowego: Tabelaryczna prezentacja posiłków na 7 dni.
Panel Boczny Listy Zakupów: Skonsolidowana lista składników.
Widok Powitalny: Specjalny ekran dla nowych użytkowników, zachęcający do dodania przepisów.
Widok Zarządzania Przepisami: Lista istniejących przepisów z opcjami dodawania, edycji i usuwania.
Formularz Przepisu: Widok do tworzenia i edycji przepisów, zawierający dynamicznie zarządzaną listę składników.
Przepływ użytkownika rozpoczyna się od logowania, przechodzi do głównego widoku, gdzie może on zarządzać przepisami, generować plan posiłków i na jego podstawie tworzyć listę zakupów.
c. Strategia integracji z API i zarządzania stanem:
Interakcje z bazą danych SQLite będą hermetyzowane w dedykowanej klasie DatabaseController. Widoki UI nie będą wykonywać bezpośrednich zapytań SQL, lecz komunikować się z kontrolerem bazy danych. Stan aplikacji, taki jak ID zalogowanego użytkownika, będzie przechowywany w głównej klasie aplikacji i przekazywany do widoków w razie potrzeby. Długotrwałe operacje na bazie danych będą uruchamiane w osobnych wątkach, aby nie blokować interfejsu.

d. Kwestie dotyczące responsywności, dostępności i bezpieczeństwa:

Responsywność: Zapewniona zostanie poprzez użycie menedżerów geometrii grid i pack z odpowiednimi opcjami (weight, fill, sticky), aby elementy UI skalowały się wraz z oknem.
Dostępność: Na tym etapie nie zdefiniowano szczegółowych wymagań, jednak prostota Tkinter i jasna struktura będą wspierać podstawową czytelność.
Bezpieczeństwo: Logika aplikacji będzie musiała zapewnić izolację danych między profilami użytkowników, filtrując wszystkie zapytania do bazy danych przez user_id aktualnie zalogowanego użytkownika.
e. Wszelkie nierozwiązane kwestie lub obszary wymagające dalszego wyjaśnienia:
Zgodnie z podjętymi decyzjami, kwestia zaawansowanej stylizacji i zapewnienia spójnego wyglądu na różnych systemach operacyjnych (np. za pomocą ttk lub ttkthemes) została odłożona na później. Priorytetem jest implementacja funkcjonalności.
</ui_architecture_planning_summary>
<unresolved_issues>
Brak nierozwiązanych kwestii na tym etapie. Wszystkie kluczowe zalecenia dotyczące architektury UI zostały omówione i zaakceptowane do dalszej implementacji.
</unresolved_issues>
</conversation_summary>