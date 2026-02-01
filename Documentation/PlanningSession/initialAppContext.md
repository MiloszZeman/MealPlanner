# Aplikacja - MealPlanner (MVP)

## Główny problem
Planowanie posiłków i kupowanie odpowiednich składników na cały tydzień jest czasochłonne, dużo prościej jest przygotować
listę śniadań, obiadów i kolacji na cały tydzień, a następnie udać się na zakupy spożywcze raz w tygodniu i zapełnić całą lodówkę.
Aplikacja MealPlanner ma pozwalać na planowanie posiłków i odpowiadającej listy zakupów tak aby przed przygotowaniem każdego posiłku
mieć pewność że wszystkie niezbędne składniki są już w lodówce i nie trzeba biec do sklepu na ostatni moment.

## Najmniejszy zestaw funkcjonalności
- aplikacja desktopowa
- możliwość zakładania kont lokalnych dla wielu użytkowników + możliwość logowania
- użytkownik może dodać własny przepis - nazwa posiłku + typ posiłku (śniadanie, obiad, kolacja) + niezbędne składniki
- użytkownik może wcisnąć przycisk "Wygeneruj plan", który tworzy losowy plan żywieniowy na najbliższy tydzień (3 posiłki dziennie) w formie tabeli.
  Plan jest zapisywany dla danego konta tak aby po wylogowaniu i zalogowaniu się był dalej dostępny
- użytkownik może wcisnąć przycisk "Wygeneruj listę", który na podstawie aktualnego planu, generuje listę zakupoów.
  Plan jest zapisywany dla danego konta tak aby po wylogowaniu i zalogowaniu się był dalej dostępny

## Co NIE wchodzi w zakres MVP
- obliczanie kalorii lub cen dla danych posiłków
- udostępnianie przepisów między kontami
- śledzenie stopnia realizacji planu lub listy zakupów

## Kryteria sukcesu
- Działają podstawowe funckjonalności -> użytkownik może dodać własne posiłki i wygenerować plan i listę zakupów na nakbliższy tydzień