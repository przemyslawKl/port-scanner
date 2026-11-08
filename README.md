TCP Port Scanner

Cel i zakres

TCP Port Scanner to narzędzie napisane w Pythonie służące do sprawdzania możliwości nawiązania połączenia TCP z wybranym hostem IPv4 i zakresem portów.

Program przeznaczony jest wyłącznie do testowania własnych lub autoryzowanych systemów.

Wersja laboratoryjna:

obsługuje IPv4,
używa TCP connect(),
skanuje jeden host,
wykonuje skan sekwencyjny,
nie wykrywa podatności,
nie identyfikuje usług,
nie przeprowadza brute force.


Wymagania i przygotowanie
Python
Wymagany Python 3.10 lub nowszy.

Zależności
Projekt wykorzystuje wyłącznie bibliotekę standardową Pythona.

Utworzenie środowiska
python3 -m venv .venv
source .venv/bin/activate

Sprawdzenie interpretera
python --version
python -c 'import sys; print(sys.executable)'

Interpreter powinien pochodzić z katalogu .venv.

Lokalny cel testowy
W katalogu laboratorium uruchom:

python3 -m http.server 18080 --bind 127.0.0.1 --directory materials/http-root

Serwer nasłuchuje na:
127.0.0.1:18080

Zatrzymanie:
Ctrl + C


Uruchomienia

Pomoc:
python scanner.py --help

Skan jednego portu:
python scanner.py 127.0.0.1 \
--start 18080 \
--end 18080 \
--timeout 0.5 \
--output output/open.csv

Skan zakresu:
python scanner.py 127.0.0.1 \
--start 18080 \
--end 18082 \
--timeout 0.5 \
--output output/range.csv \
--verbose

Przykład celu DNS:

python scanner.py localhost \
--start 18080 \
--end 18080
Argumenty


Argument	Znaczenie	                    Domyślnie
host	    Adres IPv4 lub nazwa DNS	    wymagany
--start	    Pierwszy port	                1
--end	    Ostatni port	                1024
--timeout	Timeout TCP w sekundach	        1.0
--output	Plik CSV	                    output/results.csv
--verbose	Diagnostyka DEBUG	            wyłączona


Wyniki i logi
Program zapisuje raport CSV:

CSV
host,port,status,timestamp

Zapisywane są wyłącznie porty, dla których udało się nawiązać połączenie TCP.
Przy zerowej liczbie otwartych portów raport zawiera wyłącznie nagłówek.
Logi zapisywane są do:

logs/scanner.log

Podsumowanie wyświetlane jest na standardowym wyjściu.

Diagnostyka trafia na stderr.

Kody wyjścia
Kod	    Znaczenie
0	    Pomyślnie zakończony skan
1	    Błąd wykonania
2	    Niepoprawne argumenty
130	    Przerwanie przez użytkownika


Testowanie
Przykłady:

Poprawny skan:
python scanner.py 127.0.0.1 --start 18080 --end 18080

Niepoprawny zakres:
python scanner.py 127.0.0.1 --start 18082 --end 18080

Niepoprawny timeout:
python scanner.py 127.0.0.1 --timeout 0

Uruchomienie testów:
python -m unittest discover tests -v
lub:
python -m unittest discover tests -q

Ograniczenia interpretacyjne

Otwarty port oznacza wyłącznie możliwość zestawienia połączenia TCP w chwili pomiaru.
Brak połączenia nie oznacza automatycznie, że port jest zamknięty.

Wynik zależy od:

stanu sieci,
konfiguracji firewalla,
aktualnego działania usługi,
opóźnień sieciowych.

Program nie identyfikuje aplikacji działających na porcie i nie ocenia podatności bezpieczeństwa.

Dalszy rozwój
Możliwe rozszerzenia:

zapis JSON,
rozbudowane logowanie,
dodatkowe testy automatyczne,
atomowy zapis CSV,
podział projektu na moduły.

Rozszerzenie projektu
Projekt został rozszerzony o automatyczne testy jednostkowe z wykorzystaniem modułów:

unittest
unittest.mock

Testy obejmują:

błędy DNS,
timeout połączenia,
przerwanie programu (KeyboardInterrupt),
walidację argumentów,
poprawne i niepoprawne połączenia TCP,
poprawne zakończenie skanu.