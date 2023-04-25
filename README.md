# genetic-genealogy

## Formáty souborů
Formáty jednotivých druhů výstupních souborů jsou specifikovány pomocí tříd obsažených v souboru *headers.py*.
Jsou zde i třídy popisující formáty možných vstupních souborů.

Každá z těchto tříd definuje, jak bude vypadat hlavička příslušného druhu souboru.
Je-li to potřeba, třída definuje mapování mezi sloupci vstupního a výstupního souboru.

## Parsování shod
Script *parse_matches.py* je nástrojem pro unifikaci formátu seznamu shod.
Program načte data ze vstupního souboru (první argument) a uloží je do souboru výstupního (druhý argument) ve správném formátu.
Je potřeba specifikovat počáteční formát zadáním informace o zdrojové databázi argumentem -s/--source. 