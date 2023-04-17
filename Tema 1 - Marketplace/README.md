Nume: Pavăl Bogdan-Costin
Grupă: 332CA

# Tema <NR> 1 Marketplace


Organizare
-
Am folosit un dicționar producers_lists pentru a stoca fiecare producător (reprezentat prin key) și lista cu produsele fiecăruia (reprezentat ca value), o lista all_products ce are elemente de tip tuplu (produs, id_producator) și stochează toate produsele disponibile în magazin, o lista all_carts pentru a stoca la fiecare cart lista cu produsele din el, nr_producers este numărul total de producători, nr_products este numărul total de produse existente în magazin și nr_carts este numărul total de carts/consumatori. Pentru sincronizare am folosit 3 Lock-uri (locker_nr_producers -> folosit când se adaugă un producător nou, locker_all_carts -> folosit când se adaugă un cart nou, locker_insert_del -> folosit la add/remove a unui produs în cart) și un Semafor inițializat cu 1 pentru a face afișarea (place_order) în siguranță.


Implementare
-
Producer:
	- încearcă să producă produsele din lista dată, luându-se pe rând fiecare produs se apelează metoda publish din Marketplace de atâtea ori cât este cantitatea acelui produs (dacă s-a putut publica sau nu se alege timpul pentru sleep);
	- dacă nu mai este niciun producător activ, se oprește producția.
Consumer:
	- se parcurge fiecare operație și se creează un cart pentru acel consumator, apoi (luând în considerare cantitatea dorită) se verifică dacă este o operație de tip add sau remove și în funcție de aceasta se adaugă sau se șterge din coș acel produs;
	- la final se publică comanda.
Marketplace:
	- id-urile de producător sunt asignate începand cu 0 și crește cu fiecare nou producător (asemănător și la cart);
	- fiecare producător are lista lui cu ce a produs;
	- la publicarea unui produs în marketplace, dacă mai este loc, se adaugă produsul atât în lista producătorului, cât și în lista magazinului;
	- la adaugarea unui produs în coș, se caută produsul în magazin (pentru a verifica dacă există), se șterge din magazin și din lista producătorului, apoi se adaugă în coșul consumatorului (operația inversă reprezintă implementarea pentru ștergerea produsului);
	- la plasarea comenzii, se afișează lista cu produsele din acel coș și se șterg din coș;
	- în metode se verifică dacă producătorul/cart există, pentru a nu face operații pe ceva inexistent;
	- implementarea pentru log este facută în fiecare funcție.
TestMarketplace:
	- teste pentru fiecare metodă din Marketplace.


Tema chiar mi s-a părut utilă, pentru că am învățat și python, fiind al treilea limbaj de programare în care folosesc pricipiile de multithreading (și astfel am văzut diferențele). Implementarea o consider destul de eficientă, dar peste tot este loc de mai bine.
Este implementat întregul enunț.
Dificultăți am avut la partea de unittesting, că am avut eroare la Product (la importul în Marketplace) din cauza versiunii de python (trebuia 3.10, iar eu aveam 3.7).

Resurse utilizate
-
- link-urile din enunțul temei
- laboratoarele 1, 2, 3 de asc
- diverse site-uri la care nu am salvat link-urile, cum ar fi: Stack Overflow, Stack Exchange, ChatGpt
- https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler
- https://stackoverflow.com/questions/6321160/how-to-set-timestamps-on-gmt-utc-on-python-logging

Git
-
https://github.com/bogdanpaval10/ASC.git
