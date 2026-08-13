#!/usr/bin/env python3
import re
import urllib.parse
from official_oracle_parser import extract_oracle_plan

BOOK_MAP = [
    ("1 Księgę Mojżesza", "Rdz"),
    ("2 Księgę Mojżesza", "Wj"),
    ("3 Księgę Mojżesza", "Kpł"),
    ("4 Księgę Mojżesza", "Licz"),
    ("5 Księgę Mojżesza", "Pwt"),
    ("1 Księgę Samuela", "1 Sm"),
    ("2 Księgę Samuela", "2 Sm"),
    ("1 Księgę Królewską", "1 Król"),
    ("2 Księgę Królewską", "2 Król"),
    ("1 Księgę Kronik", "1 Krn"),
    ("2 Księgę Kronik", "2 Krn"),
    ("1 List do Koryntian", "1 Kor"),
    ("2 List do Koryntian", "2 Kor"),
    ("1 List do Tesaloniczan", "1 Tes"),
    ("2 List do Tesaloniczan", "2 Tes"),
    ("1 List do Tymoteusza", "1 Tm"),
    ("2 List do Tymoteusza", "2 Tm"),
    ("1 List Piotra", "1 P"),
    ("2 List Piotra", "2 P"),
    ("1 List Jana", "1 J"),
    ("2 i 3 List Jana", "2 J"),
    ("1 List Judy", "Jud"),
    ("Księgę Jozuego", "Joz"),
    ("Księgę Sędziów", "Sędz"),
    ("Księgę Rut", "Rut"),
    ("Księgę Ezdrasza", "Ezd"),
    ("Księgę Nehemiasza", "Neh"),
    ("Księgę Estery", "Est"),
    ("Księgę Hioba", "Hi"),
    ("Psalm", "Ps"),
    ("Księgę Przysłów", "Prz"),
    ("Księgę Koheleta", "Koh"),
    ("Pieśń nad Pieśniami", "Pnp"),
    ("Księgę Izajasza", "Iz"),
    ("Księgę Jeremiasza", "Jr"),
    ("Księgę Lamentacji", "Lm"),
    ("Księgę Ezechiela", "Ez"),
    ("Księgę Daniela", "Dn"),
    ("Księgę Ozeasza", "Oz"),
    ("Księgę Joela", "Jl"),
    ("Księgę Amosa", "Am"),
    ("Księgę Abdiasza", "Ab"),
    ("Księgę Jonasza", "Jon"),
    ("Księgę Micheasza", "Mi"),
    ("Księgę Nahuma", "Na"),
    ("Księgę Habakuka", "Ha"),
    ("Księgę Sofoniasza", "So"),
    ("Księgę Aggeusza", "Ag"),
    ("Księgę Zachariasza", "Za"),
    ("Księgę Malachiasza", "Ml"),
    ("Ewangelię Mateusza", "Mt"),
    ("Ewangelię Marka", "Mk"),
    ("Ewangelię Łukasza", "Łk"),
    ("Ewangelię Jana", "J"),
    ("Dzieje Apostolskie", "Dz"),
    ("List do Rzymian", "Rz"),
    ("List do Galacjan", "Ga"),
    ("List do Galatów", "Ga"),
    ("List do Efezjan", "Ef"),
    ("List do Filipian", "Flp"),
    ("List do Kolosan", "Kol"),
    ("List do Tytusa", "Tt"),
    ("List do Filemona", "Flm"),
    ("List do Hebrajczyków", "Hbr"),
    ("List Jakuba", "Jk"),
    ("List Judy", "Jud"),
    ("Apokalipsę Jana", "Ap"),
]

def text_to_deon_link(text: str) -> tuple[str, str]:
    clean_text = text.rstrip(".").strip()
    matched_abbr = None
    matched_name = None
    for name, abbr in BOOK_MAP:
        if name in clean_text:
            matched_abbr = abbr
            matched_name = name
            break
            
    if not matched_abbr:
        query = urllib.parse.quote_plus(clean_text)
        return clean_text, f"https://biblia.deon.pl/otworz.php?skrot={query}"

    after_book = clean_text[clean_text.find(matched_name) + len(matched_name):]
    nums = re.findall(r'\d+', after_book)
    
    if "wersety" in after_book.lower() and len(nums) >= 3:
        ch = nums[0]
        v_start = nums[1]
        v_end = nums[2]
        label = f"{matched_abbr} {ch},{v_start}-{v_end}"
        query = f"{matched_abbr}+{ch},{v_start}-{v_end}"
    elif nums:
        first_ch = nums[0]
        if len(nums) == 1:
            label = f"{matched_abbr} {first_ch}"
            query = f"{matched_abbr}+{first_ch}"
        elif len(nums) == 2:
            label = f"{matched_abbr} {nums[0]}-{nums[1]}"
            query = f"{matched_abbr}+{first_ch}"
        else:
            label = f"{matched_abbr} {nums[0]}-{nums[-1]}"
            query = f"{matched_abbr}+{first_ch}"
    else:
        label = f"{matched_abbr} 1"
        query = f"{matched_abbr}+1"

    url = f"https://biblia.deon.pl/otworz.php?skrot={query}"
    return label, url

plan = extract_oracle_plan()
for day in plan[:5]:
    print(f"--- Dzień {day['day']} ---")
    for track_key in ["t1_ref", "t2_ref", "t3_ref"]:
        txt = day[track_key]
        lbl, url = text_to_deon_link(txt)
        print(f"  Opis: '{txt}' -> Etykieta: '{lbl}' | URL: {url}")
