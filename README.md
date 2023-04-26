# genetic-genealogy

## Formáty souborů
Formáty jednotivých druhů výstupních souborů jsou specifikovány
pomocí tříd obsažených v souboru *headers.py*.
Jsou zde i třídy popisující formáty možných vstupních souborů.

Každá z těchto tříd definuje, jak bude vypadat hlavička příslušného druhu souboru.
Je-li to potřeba, třída definuje mapování mezi sloupci vstupního a výstupního souboru.

## Parsování shod
Script *parse_matches.py* je nástrojem pro unifikaci formátu seznamu shod.
Program načte data ze vstupního souboru (první argument) a uloží je do
souboru výstupního (druhý argument) ve správném formátu.
Je potřeba specifikovat počáteční formát zadáním informace
o zdrojové databázi argumentem *-s/--source*.

Každý záznam ze vstupního souboru je porovnán s "databází" uloženou v souboru
s názvem "all_matches.csv" dosud přidaných osob
a pokud je nalezena shoda, je záznamu o osobě přidělené stejné ID.
V opačném případě je vygenerováno nové, unikátní ID.

Pokud all_matches.csv neexistuje, je vytvořen nový. 

Použití:

    parse_matches.py input_file output_file -s source_database

## Parsování sdílených shod
*parse_shared_matches.py* provádí propojení a unifikaci souborů obsahujících
sdílené shody POI a shod POI.

Sjednocený přehled o shodách shod je vypsán do výstupního souboru, 
který je specifikován prvním parametrem.
Vstupních souborů je možné předat libovolné množství pomocí argumentu *-f/--files*.
Je také možné programu předat libovolné množství adresářů, které obsahují soubory určené k parsování,
pomocí argumentu *-d/--directories*.
Oba argumenty je možné nezávisle kombinovat.
Zdroj dat je opět specifikován pomocí argumentu *-s/--source*.

Použití:

    parse_shared_matches.py output_file -s SOURCE -f file_1 file_2 file_3 -d directory_1 directory_2

## Parsování dat o segmentech
*parse_segments.py* zajišťuje transformaci dat o segmentech do unifikovaného formátu.

Pomocí prvního argumentu specifikujte vstupní soubor, pomocí druhého výstupní soubor.
Argumentem *-s/--source* specifikujte zdrojovou databázi.

Každý záznam je porovnán s "databází" všech segmentů v souboru s názvem 
"all_segments.csv". A pokud je nalezena shoda, je segmentu přiděleno stejné
ID. V opačném případě je vygenerováno nové, unikátní ID.

Pokud soubor all_segments.csv neexistuje, je vytvořen nový.

Použití:

    parse_segments.py input_file output_file -s SOURCE
