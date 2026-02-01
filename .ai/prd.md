Dokument wymagań produktu (PRD) - MealPlanner
1.
Przegląd produktu
MealPlanner to aplikacja desktopowa (stworzona w technologii Electron) przeznaczona dla użytkowników, którzy chcą uprościć proces planowania posiłków i tworzenia list zakupów. Aplikacja umożliwia tworzenie lokalnych profili użytkowników, dodawanie własnych przepisów kulinarnych, automatyczne generowanie tygodniowych planów żywieniowych oraz tworzenie skonsolidowanych list zakupów na podstawie tych planów. Całość funkcjonuje w trybie offline, zapewniając użytkownikom pełną kontrolę nad swoimi danymi bez konieczności połączenia z internetem. Celem wersji MVP jest dostarczenie kluczowych funkcjonalności, które rozwiązują główny problem użytkownika w prosty i intuicyjny sposób.

2. Problem użytkownika
Planowanie posiłków na cały tydzień oraz przygotowywanie szczegółowej listy zakupów jest procesem czasochłonnym i często frustrującym. Użytkownicy borykają się z koniecznością pamiętania o wszystkich niezbędnych składnikach, co prowadzi do częstych, nieplanowanych wizyt w sklepie w ostatniej chwili. Brak zorganizowanego planu utrudnia efektywne zarządzanie domowym budżetem i czasem. Aplikacja MealPlanner ma na celu wyeliminowanie tego problemu, oferując narzędzie do łatwego tworzenia planów żywieniowych i automatycznego generowania list zakupów, co daje pewność, że wszystkie potrzebne produkty znajdują się w lodówce przed rozpoczęciem gotowania.

3. Wymagania funkcjonalne
FR-1: Zarządzanie profilami użytkowników: Aplikacja umożliwia tworzenie wielu lokalnych profili użytkowników w ramach jednej instalacji. Każdy profil jest chroniony hasłem.
FR-2: Tworzenie i zarządzanie przepisami: Użytkownik może dodawać, edytować i usuwać własne przepisy. Każdy przepis zawiera nazwę, przypisanie do jednej lub wielu kategorii (śniadanie, obiad, kolacja) oraz listę składników.
FR-3: Definiowanie składników: Podczas dodawania składnika do przepisu użytkownik określa jego nazwę, ilość, predefiniowaną jednostkę (gramy, mililitry, sztuki) oraz ma możliwość zaznaczenia opcji "ilość symboliczna" (np. dla szczypty soli).
FR-4: Generowanie planu żywieniowego: Aplikacja potrafi wygenerować losowy plan żywieniowy na 7 kolejnych dni (3 posiłki dziennie) na podstawie bazy przepisów użytkownika, starając się unikać powtórzeń.
FR-5: Edycja planu żywieniowego: Użytkownik ma możliwość ręcznej modyfikacji wygenerowanego planu poprzez zamianę dowolnego posiłku na inny z tej samej kategorii.
FR-6: Generowanie listy zakupów: Na podstawie aktywnego planu żywieniowego aplikacja generuje skonsolidowaną, posortowaną alfabetycznie listę zakupów, sumując ilości potrzebnych składników.
FR-7: Interfejs użytkownika: Aplikacja posiada prosty i intuicyjny interfejs, który jest responsywny na zmiany rozmiaru okna. Głównym widokiem jest plan tygodniowy, a lista zakupów prezentowana jest w panelu bocznym.
4. Granice produktu
Następujące funkcje i elementy są świadomie wyłączone z zakresu wersji MVP (Minimum Viable Product):

Obliczanie wartości odżywczych (kalorii, makroskładników) oraz cen posiłków.
Funkcje społecznościowe, takie jak udostępnianie przepisów między kontami.
Śledzenie postępów w realizacji planu żywieniowego lub listy zakupów (np. odhaczanie kupionych produktów).
Funkcje online, synchronizacja danych w chmurze, tworzenie kopii zapasowych online.
Zaawansowane ustawienia aplikacji, takie jak zmiana hasła, motywy (jasny/ciemny) czy eksport/import danych.
Drukowanie planów lub list zakupów.
Edycja wygenerowanej listy zakupów.
Wskaźniki ładowania lub powiadomienia o pomyślnym wykonaniu akcji.
5. Historyjki użytkowników
ID: US-001

Tytuł: Tworzenie nowego profilu użytkownika

Opis: Jako nowy użytkownik, chcę móc stworzyć osobisty, chroniony hasłem profil, aby przechowywać w nim swoje przepisy i plany żywieniowe.

Kryteria akceptacji:

Na ekranie startowym widoczny jest przycisk "Stwórz nowy profil".
Po kliknięciu przycisku pojawia się formularz z polami: "Nazwa profilu", "Hasło", "Powtórz hasło".
System weryfikuje, czy nazwa profilu jest unikalna. Jeśli nie, wyświetla komunikat błędu "Profil o tej nazwie już istnieje.".
System weryfikuje, czy oba wprowadzone hasła są identyczne. Jeśli nie, wyświetla komunikat błędu.
Po pomyślnym utworzeniu profilu, użytkownik jest zalogowany i przeniesiony do głównego widoku aplikacji.
ID: US-002

Tytuł: Logowanie do istniejącego profilu

Opis: Jako powracający użytkownik, chcę móc wybrać swój profil z listy i zalogować się za pomocą hasła, aby uzyskać dostęp do moich danych.

Kryteria akceptacji:

Na ekranie startowym widoczna jest lista istniejących profili.
Po wybraniu profilu aktywuje się pole do wpisania hasła.
Po wpisaniu poprawnego hasła i zatwierdzeniu, użytkownik zostaje przeniesiony do głównego widoku aplikacji z załadowanym swoim planem.
Po wpisaniu niepoprawnego hasła, wyświetlany jest komunikat o błędzie.
ID: US-003

Tytuł: Dodawanie nowego przepisu

Opis: Jako użytkownik, chcę móc dodać nowy przepis do mojej bazy, określając jego nazwę, kategorie oraz wszystkie niezbędne składniki, abym mógł go później wykorzystać w planie żywieniowym.

Kryteria akceptacji:

W sekcji "Moje Przepisy" znajduje się opcja "Dodaj nowy przepis".
Formularz dodawania przepisu zawiera pole na nazwę oraz checkboxy dla kategorii (Śniadanie, Obiad, Kolacja).
Formularz zawiera dynamiczną listę składników.
Użytkownik może dodać nowy wiersz składnika za pomocą przycisku "+ Dodaj składnik".
Każdy wiersz składnika zawiera pola: "Nazwa" (tekst), "Ilość" (liczba), "Jednostka" (lista rozwijana: gramy, mililitry, sztuki) oraz checkbox "Ilość symboliczna".
Zapisanie przepisu jest możliwe tylko wtedy, gdy nazwa przepisu jest uzupełniona i przypisano co najmniej jedną kategorię.
ID: US-004

Tytuł: Edycja istniejącego przepisu

Opis: Jako użytkownik, chcę mieć możliwość edycji moich przepisów, aby poprawić błędy lub zmodyfikować składniki.

Kryteria akceptacji:

Na liście przepisów każdy element ma opcję "Edytuj".
Po wybraniu edycji, użytkownik widzi formularz wypełniony danymi edytowanego przepisu.
Użytkownik może zmieniać nazwę, kategorie oraz dodawać, usuwać i modyfikować składniki.
Po zapisaniu zmian, przepis na liście jest zaktualizowany.
ID: US-005

Tytuł: Generowanie tygodniowego planu żywieniowego

Opis: Jako użytkownik, chcę móc jednym kliknięciem wygenerować losowy plan posiłków na cały tydzień, aby zaoszczędzić czas na jego ręcznym układaniu.

Kryteria akceptacji:

W głównym widoku aplikacji znajduje się przycisk "Wygeneruj plan".
Przed wygenerowaniem planu aplikacja sprawdza, czy istnieje co najmniej jeden przepis w każdej kategorii (śniadanie, obiad, kolacja). Jeśli nie, wyświetla komunikat o brakujących przepisach i nie generuje planu.
Po kliknięciu przycisku (i przy wystarczającej liczbie przepisów) pojawia się okno dialogowe z pytaniem "Czy na pewno chcesz wygenerować nowy plan? Spowoduje to utratę obecnego.".
Po potwierdzeniu, aplikacja tworzy tabelę z planem na 7 kolejnych dni (zaczynając od jutra), wypełniając ją losowymi przepisami z odpowiednich kategorii.
Algorytm stara się nie powtarzać posiłków w ramach jednego planu, jeśli liczba unikalnych przepisów na to pozwala.
ID: US-006

Tytuł: Ręczna edycja wygenerowanego planu

Opis: Jako użytkownik, chcę mieć możliwość ręcznej zmiany pojedynczego posiłku w moim planie, aby dostosować go do swoich preferencji.

Kryteria akceptacji:

Każdy posiłek w tabeli planu ma opcję edycji.
Po kliknięciu edycji pojawia się lista rozwijana zawierająca wszystkie dostępne przepisy z tej samej kategorii, posortowane alfabetycznie.
Po wybraniu nowego przepisu z listy, zastępuje on poprzedni w planie.
Zmiana jest zapisywana automatycznie.
ID: US-007

Tytuł: Generowanie listy zakupów

Opis: Jako użytkownik, chcę móc wygenerować kompletną listę zakupów na podstawie mojego tygodniowego planu, aby mieć pewność, że kupię wszystkie potrzebne składniki.

Kryteria akceptacji:

W głównym widoku znajduje się przycisk "Wygeneruj listę" (lub jest ona generowana automatycznie).
Po wygenerowaniu, w panelu bocznym (zajmującym ok. 1/4 szerokości okna) pojawia się lista zakupów.
Lista zawiera wszystkie składniki ze wszystkich posiłków w planie.
Ilości tych samych składników (np. "jajka") są sumowane.
Składniki oznaczone jako "ilość symboliczna" pojawiają się na liście bez ilości (np. "Sól").
Cała lista jest posortowana alfabetycznie.
ID: US-008

Tytuł: Usuwanie przepisu

Opis: Jako użytkownik, chcę móc usunąć przepis, którego już nie potrzebuję, aby utrzymać porządek w mojej bazie.

Kryteria akceptacji:

Na liście przepisów każdy element ma opcję "Usuń".
Jeśli usuwany przepis nie jest używany w aktualnym planie, zostaje usunięty po potwierdzeniu.
Jeśli usuwany przepis jest używany w aktualnym planie, aplikacja wyświetla okno dialogowe z pytaniem, czy na pewno usunąć i informacją, że posiłek w planie zostanie zastąpiony innym.
Po potwierdzeniu usunięcia, przepis znika z bazy, a w planie na jego miejsce wstawiany jest inny losowy przepis z tej samej kategorii.
Jeśli nie ma innego przepisu w tej kategorii, komórka w planie staje się pusta i jest oznaczona jako wymagająca uzupełnienia.
ID: US-009

Tytuł: Widok startowy dla nowego użytkownika

Opis: Jako nowy użytkownik, który jeszcze nie ma żadnego planu, po zalogowaniu chcę zobaczyć ekran, który pokieruje mnie, co robić dalej.

Kryteria akceptacji:

Po zalogowaniu na nowo utworzone konto, główny widok nie pokazuje pustej tabeli.
Zamiast tego wyświetlany jest komunikat powitalny oraz duży przycisk "Stwórz swój pierwszy plan żywieniowy!" z informacją, że najpierw należy dodać przepisy.
6. Metryki sukcesu
Głównym kryterium sukcesu dla wersji MVP jest pomyślne i bezproblemowe ukończenie przez użytkownika kluczowej ścieżki użytkowania. Sukces zostanie zmierzony poprzez weryfikację następującego scenariusza:

Mierzalny cel: Użytkownik jest w stanie pomyślnie utworzyć konto, dodać co najmniej 3 przepisy (po jednym dla każdej kategorii), wygenerować plan żywieniowy oraz odpowiadającą mu listę zakupów w czasie krótszym niż 10 minut.
Realizacja tego scenariusza przez grupę testową potwierdzi, że podstawowe funkcjonalności działają zgodnie z założeniami i rozwiązują główny problem użytkownika.