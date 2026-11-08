Notatki — Lab 22: TCP Port Scanner
Środowisko
Autor i data: Przemysław K., 2026-11-08
System operacyjny: Kali Linux
Wersja Pythona: Python 3.14.6
Ścieżka interpretera .venv: /usr/bin/python
Katalog projektu: /home/kali/Desktop/labolatorium python 5/port-scanner
Kontrolowany adres i port: 127.0.0.1:18080
Jeśli zmieniono port 18080, uzasadnienie: nie dotyczy

Uruchomienie lokalnej usługi

Polecenie i katalog startowy:
python3 -m http.server 18080 --bind 127.0.0.1 --directory materials/http-root
Potwierdzenie nasłuchu:
Strona dostępna pod adresem: http://127.0.0.1:18080
Funkcja check_port() zwracała True.

Potwierdzenie zatrzymania własnego procesu:
Zatrzymanie usługi przez Ctrl+C.
Funkcja check_port() zwracała False po zatrzymaniu serwera.

Wyniki prób
Przypadek	Polecenie lub sposób podmiany	Stan serwera	Kod wyjścia	CSV / liczba rekordów	Obserwacje
Pomoc i import	python scanner.py --help, python -c 'import scanner'	uruchomiony	0	brak	Import nie uruchamia skanowania
Jeden port, usługa działa	python scanner.py 127.0.0.1 --start 18080 --end 18080	działa	0	1 rekord	Port 18080 wykryty jako open
Ten sam port po zatrzymaniu	python scanner.py 127.0.0.1 --start 18080 --end 18080	zatrzymany	0	nagłówek	Brak otwartych portów
Zakres trzech portów	python scanner.py 127.0.0.1 --start 18080 --end 18082	działa	0	zależnie od środowiska	Dokładnie 3 próby TCP
Alternatywa: scanme.nmap.org, porty 79–81	nie wykonywano	-	-	-	wariant opcjonalny
localhost	python scanner.py localhost --start 18080 --end 18080	działa	0	1 rekord	DNS rozwiązany do 127.0.0.1
Niepoprawny zakres	--start 18082 --end 18080	nie dotyczy	2	brak	Walidacja przed DNS i TCP
Timeout 0, nan, inf	odpowiednie polecenia testowe	nie dotyczy	2	brak	Parametry odrzucone
Niepoprawny format celu	URL, CIDR, IPv6	nie dotyczy	2	brak	Parametry odrzucone
Kontrolowany błąd DNS	unittest.mock + gaierror	nie dotyczy	1	brak	Brak rozpoczęcia skanu
Kontrolowany timeout TCP	unittest.mock + socket.timeout	nie dotyczy	brak awarii programu	brak	Funkcja zwróciła False
Błąd zapisu	--output output	działa	1	brak	Błąd zapisany do loga
Przerwanie skanowania	unittest.mock + KeyboardInterrupt	działa	130	brak zmian	Poprawna obsługa przerwania
Porównanie verbose	ten sam skan z i bez --verbose	działa	0	identyczne CSV	Tylko dodatkowe logi DEBUG


Wybrane ślady diagnostyczne
INFO
INFO - Starting scan host=127.0.0.1 ip=127.0.0.1
INFO - Range=18080-18082, timeout=0.5
INFO - Open port detected: 18080
INFO - Scan complete. Checked=3, Open=1
DEBUG
DEBUG - Port 18080: open=True
DEBUG - Port 18081: open=False
DEBUG - Port 18082: open=False
ERROR
ERROR - DNS resolution failed.
ERROR - Start port must be between 1 and 65535.
ERROR - File operation failed.


Pytania do wyjaśnienia
1. Co dokładnie potwierdza kod 0 zwrócony przez connect_ex()?
Kod 0 oznacza, że nawiązanie połączenia TCP zakończyło się sukcesem.

2. Dlaczego brak udanego połączenia nie oznacza automatycznie zamkniętego portu?
Przyczyną może być firewall, timeout sieciowy, filtrowanie ruchu lub problemy routingu.

3. Dlaczego timeout połączenia nie ogranicza automatycznie czasu DNS?
Rozwiązywanie DNS jest oddzielną operacją wykonywaną przed próbą TCP.

4. Co zapewnia użycie context managera dla socketu?
Automatyczne zamknięcie socketu nawet przy wystąpieniu wyjątku.

5. Dlaczego CSV zawierający tylko nagłówek może być poprawnym wynikiem?
Skan został wykonany poprawnie, ale nie wykryto żadnego otwartego portu.

6. Jak sprawdzono, że błędne argumenty nie powodują połączeń?
Walidacja wykonywana jest przed DNS oraz przed wywołaniem check_port().

7. Jak odróżniasz brak otwartych portów od awarii skanera?
Brak portów open zwraca kod 0, natomiast awaria programu zwraca kod 1.

8. Jakie ograniczenia wersji podstawowej podasz osobie korzystającej z narzędzia?
tylko IPv4,
TCP connect scan,
jeden host,
brak wielowątkowości,
brak identyfikacji usług,
brak wykrywania podatności.

Kryteria końcowe
CLI i pomoc działają.
Import nie ma skutków ubocznych.
Walidacja następuje przed DNS i próbami TCP.
DNS wykonywany jest raz.
Sockety są zamykane również przy błędzie.
CSV i podsumowanie są zgodne.
Obsłużono błędy oraz przerwanie.
Logi i wyniki mają osobne kanały.
README, requirements.txt i .gitignore są gotowe.
Rozszerzenie i wnioski
Wybrane rozszerzenie: Testy automatyczne przy użyciu unittest oraz unittest.mock.

Co zmieniło się względem wersji podstawowej:
dodano testy DNS,
dodano testy timeoutów,
dodano testy KeyboardInterrupt,
dodano testy walidacji,
dodano testy funkcji check_port().

Pozostałe ograniczenia:
tylko IPv4,
brak identyfikacji usług,
brak wykrywania podatności,
brak skanowania wielu hostów,
brak pracy wielowątkowej.
