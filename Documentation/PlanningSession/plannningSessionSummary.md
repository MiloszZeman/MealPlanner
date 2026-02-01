<conversation_summary> <decisions> 1. **Zarządzanie kontami:** Kont

a będą lokalnymi profilami w ramach jednej instalacji aplikacji. Nie będzie funkcji usuwania kont ani zmiany hasła w MVP.
2. Tworzenie profili: Ekran startowy będzie minimalistyczny, z opcją wyboru profilu lub stworzenia nowego. Nowe profile wymagają podania unikalnej nazwy i hasła (bez specjalnych wymagań co do złożoności).
3. Zarządzanie przepisami: Użytkownik może dodawać, edytować i usuwać przepisy. Przepis może należeć do wielu kategorii (śniadanie, obiad, kolacja).
4. Interfejs dodawania przepisów: Składniki dodawane są dynamicznie jako lista wierszy. Każdy wiersz zawiera pola: Nazwa, Ilość, predefiniowana Jednostka (gramy, mililitry, sztuki) oraz checkbox "ilość symboliczna".
5. Usuwanie przepisów: Przy próbie usunięcia przepisu używanego w planie, aplikacja zapyta o potwierdzenie i poinformuje, że posiłek zostanie zastąpiony innym. Jeśli innego nie ma, pole w planie zostanie puste.
6. Generowanie planu: Plan generowany jest na 7 kolejnych dni, zaczynając od jutra. Unika się powtarzania posiłków, jeśli jest ich wystarczająco dużo. W przeciwnym razie posiłki są powtarzane. Generowanie planu wymaga potwierdzenia, aby nie nadpisać istniejącego przypadkowo.
7. Edycja planu: Użytkownik może edytować wygenerowany plan, zamieniając posiłek na inny z tej samej kategorii, wybrany z alfabetycznie posortowanej listy rozwijanej. Zmiany są zapisywane automatycznie.
8. Generowanie listy zakupów: Lista jest generowana na żądanie na podstawie aktualnego planu. Składniki są sumowane. Lista jest widoczna jako boczny panel (1/4 szerokości okna) obok planu i jest posortowana alfabetycznie. Edycja listy nie wchodzi w zakres MVP.
9. Interfejs użytkownika (UI): Głównym widokiem po zalogowaniu jest plan tygodniowy z nagłówkiem dat. Zanim plan zostanie wygenerowany, widok zachęca do działania. Posiłki w planie mają oznaczenia kategorii. Nawigacja odbywa się przez prosty pasek boczny/górny. Interfejs jest responsywny.
10. Technologia i zakres: Aplikacja desktopowa (Electron) działająca w pełni offline. MVP nie obejmuje: eksportu/importu danych, drukowania, obliczania kalorii/cen, udostępniania przepisów, śledzenia realizacji planu, powiadomień o sukcesie akcji, wskaźników ładowania.
</decisions>

<matched_recommendations> 1. Zaimplementowanie prostego systemu profili w ramach jednej instalacji, chronionych hasłem. 2. Wymuszenie unikalności nazw profili w celu uniknięcia pomyłek przy logowaniu. 3. Dodanie pól "ilość" i "jednostka" przy składnikach, aby umożliwić ich agregację na liście zakupów. 4. Wprowadzenie opcji "ilość symboliczna" dla składników takich jak "szczypta", aby nie były one sumowane. 5. Umożliwienie przypisania jednego przepisu do wielu kategorii (np. obiad i kolacja), co zwiększa elastyczność. 6. Zastosowanie automatycznego zapisu zmian w planie żywieniowym w celu wygody użytkownika i uniknięcia utraty danych. 7. Wyświetlanie okna dialogowego z potwierdzeniem przed wygenerowaniem nowego planu, aby chronić użytkownika przed przypadkowym nadpisaniem danych. 8. Zaprojektowanie interfejsu dodawania składników jako dynamicznej listy wierszy, co jest wygodniejsze niż osobne okna. 9. Wyświetlanie zachęty do działania na pustym ekranie planu, aby poprowadzić nowego użytkownika. 10. Dodanie nagłówka z zakresem dat nad tabelą planu w celu ułatwienia orientacji czasowej. </matched_recommendations> <prd_planning_summary> Na podstawie przeprowadzonej analizy, MVP aplikacji MealPlanner ma na celu rozwiązanie problemu czasochłonnego planowania posiłków i zakupów. Aplikacja będzie narzędziem desktopowym (Electron) działającym w trybie offline.

Główne wymagania funkcjonalne:

System profili: Użytkownicy mogą tworzyć lokalne, chronione hasłem profile o unikalnych nazwach.
Zarządzanie przepisami: Użytkownicy mogą tworzyć własne przepisy, określając ich nazwę, kategorie (śniadanie, obiad, kolacja - wielokrotny wybór) oraz listę składników z ilością, jednostką i opcją "ilości symbolicznej". Możliwa jest edycja i usuwanie przepisów.
Planowanie posiłków: Aplikacja generuje 7-dniowy plan żywieniowy (3 posiłki dziennie) na podstawie dodanych przepisów, starając się unikać powtórzeń. Użytkownik ma możliwość ręcznej edycji planu.
Generowanie listy zakupów: Na podstawie aktywnego planu generowana jest zagregowana i posortowana alfabetycznie lista zakupów, prezentowana w panelu bocznym.
Kluczowe historie użytkownika i ścieżki korzystania:

Nowy użytkownik: Uruchamia aplikację, tworzy nowy profil, loguje się. Widzi pusty ekran planu z zachętą do działania. Przechodzi do sekcji "Moje Przepisy", dodaje kilka własnych przepisów. Wraca do widoku planu, klika "Wygeneruj plan", potwierdza akcję. Przegląda wygenerowany plan i listę zakupów.
Powracający użytkownik: Uruchamia aplikację, wybiera swój profil z listy, wpisuje hasło, loguje się. Widzi swój ostatnio zapisany plan. Postanawia wymienić obiad we wtorek na inny, klika na posiłek i wybiera alternatywę z listy rozwijanej. Zmiana zapisuje się automatycznie. Generuje nową listę zakupów, aby odzwierciedlić zmianę.
Ważne kryteria sukcesu i sposoby ich mierzenia:
Głównym kryterium sukcesu jest płynne przejście przez kluczową ścieżkę użytkownika. Mierzalny cel: "Użytkownik jest w stanie pomyślnie utworzyć konto, dodać co najmniej 3 przepisy (po jednym dla każdej kategorii), wygenerować plan żywieniowy oraz odpowiadającą mu listę zakupów." Realizacja tego scenariusza potwierdza działanie podstawowych funkcjonalności.

</prd_planning_summary> <unresolved_issues> Brak nierozwiązanych kwestii. Wszystkie punkty poruszone w trakcie dyskusji zostały doprecyzowane i zamknięte na potrzeby zdefiniowania zakresu MVP. </unresolved_issues> </conversation_summary>