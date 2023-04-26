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
o zdrojové databázi vybráním jednoho ze dvou vzájemně se vylučujících argumentů
*--ftdna* a *--gedmatch.*

Každý záznam ze vstupního souboru je porovnán s "databází" uloženou v souboru
s názvem "all_matches.csv" dosud přidaných osob
a pokud je nalezena shoda, je záznamu o osobě přidělené stejné ID.
V opačném případě je vygenerováno nové, unikátní ID a záznam je přidán do databáze.
Modifikovány jsou tedy dva soubory - do specifikovaného výstupního souboru 
je vypsána ta množina záznamů, která je obsažena v souboru vstupním a do souboru
all_mathces.csv jsou připsány ty záznamy, které se zde dosud neobjevily.

Pokud all_matches.csv neexistuje, je vytvořen nový. 

Použití:

    parse_matches.py input_file_from_FTDNA output_file --ftdna

    parse_matches.py input_file_from_GEDmatch output_file --gedmatch

## Parsování sdílených shod
*parse_shared_matches.py* provádí propojení a unifikaci souborů obsahujících
sdílené shody POI a shod POI.

Sjednocený přehled o shodách shod je vypsán do výstupního souboru, 
který je specifikován prvním parametrem.
Vstupních souborů je možné předat libovolné množství pomocí argumentu *-f/--files*.
Je také možné programu předat libovolné množství adresářů, které obsahují soubory určené k parsování,
pomocí argumentu *-d/--directories*.
Oba argumenty je možné nezávisle kombinovat.
Zdroj dat je opět specifikován pomocí argumentu *--ftdna* nebo *--gedmatch*.

Pokud data pochází z FTDNA, každý vstupní soubor musí obsahovat pouze shody,
které POI sdílí s jednou osobou,
jméno této osoby musí být názvem tohoto souboru.
Jméno se by mělo být složeno z prvního i druhého jména a příjmení.
Pokud jméno není identifikováno v databázi všech shod (all_matches.csv),
místo ID osoby je do výstupního souboru uložena hodnota **-1** a uživatel
je vyzván k ruční opravě dat nebo jména.

> Kvůli vyhledávání IDs v databázi je tedy potřeba **před parsováním
> shod shod zpracovat samotné shody POI
pomocí *parse_matches.py***.

Použití:

    parse_shared_matches.py output_file --ftdna -d directory_containing_files_from_FTDNA

    parse_shared_matches.py output_file --gedmatch -f file_1 file_2 file_3 -d directory_1 directory_2

## Parsování dat o segmentech
*parse_segments.py* zajišťuje transformaci dat o segmentech do unifikovaného formátu.

Pomocí prvního argumentu specifikujte vstupní soubor, pomocí druhého výstupní soubor.
Jedním z argumentů *--ftdna* nebo *--gedmatch* specifikujte zdrojovou databázi.

Každý záznam je porovnán s "databází" všech segmentů v souboru s názvem 
"all_segments.csv". A pokud je nalezena shoda, je segmentu přiděleno stejné segment
ID. V opačném případě je vygenerováno nové, unikátní segment ID.
Stejně jako u parsování shod jsou nové záznamy o segmentech přidány do příslušné databáze.

Pokud soubor all_segments.csv neexistuje, je vytvořen nový.

Použití:

    parse_segments.py input_file_from_FTDNA unified_output_file --ftdna

    parse_segments.py input_file_from_GEDmatch unified_output_file --gedmatch

Poznámka:

Pochází-li segment data z FamilyTreeDNA, je  v databázi všech osob (all_matches.csv)
pro každý záznam o segmetnu podle jména
osoby vyhledáno ID osoby, se kterou POI sdílí daný segment.
Toto ID osoby je pak přidáno k záznamu o segmentu do výstupního souboru.

Pokud není podle jména danou osobu možné dohledat, je jí přidělena automatická hodnota id
**-1** a uživatel je vyzván k ručnímu vyhledání dané osoby a ruční opravě záznamu.

## Hledání průniků segmentů
*find_segment_intersections.py* umožňuje najít průniky segmentů.
Program na vstupu bere naparsovaný seznam segmentů v unifikovaném formátu
jako první parametr a jako druhý parametr bere jméno výstupního souboru.

>Je nutné nejdříve naparsovat segmenty pomocí programu *parse_segments.py*
> a výstupní soubor předat jako vstupní soubor tomuto programu

Je možné ze segmentů v zadaném vstupním souboru vyextrahovat všechny možné 
dvojice segmentů, které mají neprázdný průnik.
Nebo je možné argumentem *-id/--personID* zadat ID osoby a tím omezit,
které dvojice segmentů budou vypsány pouze na dvojice, kde jedna z osob je
identifikována tímto ID.

Použití:

    find_segment_intersections.py parsed_segments_file output_file

    find_segment_intersections.py parsed_segments_file output_file -id 123

