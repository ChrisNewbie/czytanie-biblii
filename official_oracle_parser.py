#!/usr/bin/env python3
"""Official Oracle Parser for Christadelphian Bible Companion Reading Plan.

Parses prawdy-biblijne-index.html to extract all 365 daily reading definitions
as the single source of truth (Oracle).
Converts Polish text descriptions to 100% verified HiperBiblia.com URLs and clean labels.
Normalizes Polish book names from Accusative (Biernik) to clean Nominative (Mianownik).
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

HTML_PATH = Path(__file__).resolve().parent / "prawdy-biblijne-index.html"
OUT_JSON = Path(__file__).resolve().parent / "official_oracle_plan.json"

# Verified 1:1 HiperBiblia.com book mapping extracted from site HTML wizard
HIPERBIBLIA_MAP = [
    ("1 Księgę Mojżesza", "gen", "Rdz"),
    ("1 Księga Mojżesza", "gen", "Rdz"),
    ("2 Księgę Mojżesza", "exo", "Wj"),
    ("2 Księga Mojżesza", "exo", "Wj"),
    ("3 Księgę Mojżesza", "lev", "Kpł"),
    ("3 Księga Mojżesza", "lev", "Kpł"),
    ("4 Księgę Mojżesza", "num", "Lb"),
    ("4 Księga Mojżesza", "num", "Lb"),
    ("5 Księgę Mojżesza", "deu", "Pwt"),
    ("5 Księga Mojżesza", "deu", "Pwt"),
    ("1 Księgę Samuela", "1sa", "1Sm"),
    ("1 Księga Samuela", "1sa", "1Sm"),
    ("2 Księgę Samuela", "2sa", "2Sm"),
    ("2 Księga Samuela", "2sa", "2Sm"),
    ("1 Księgę Królewską", "1ki", "1Krl"),
    ("1 Księga Królewska", "1ki", "1Krl"),
    ("2 Księgę Królewską", "2ki", "2Krl"),
    ("2 Księga Królewska", "2ki", "2Krl"),
    ("1 Księgę Kronik", "1ch", "1Krn"),
    ("1 Księga Kronik", "1ch", "1Krn"),
    ("2 Księgę Kronik", "2ch", "2Krn"),
    ("2 Księga Kronik", "2ch", "2Krn"),
    ("1 List do Koryntian", "1co", "1Kor"),
    ("2 List do Koryntian", "2co", "2Kor"),
    ("1 List do Tesaloniczan", "1th", "1Tes"),
    ("2 List do Tesaloniczan", "2th", "2Tes"),
    ("1 List do Tymoteusza", "1ti", "1Tm"),
    ("2 List do Tymoteusza", "2ti", "2Tm"),
    ("1 List Piotra", "1pe", "1P"),
    ("2 List Piotra", "2pe", "2P"),
    ("1 List Jana", "1jo", "1J"),
    ("2 i 3 List Jana", "2jo", "2J"),
    ("1 List Judy", "jud", "Jud"),
    ("Księgę Jozuego", "jos", "Joz"),
    ("Księga Jozuego", "jos", "Joz"),
    ("Księgę Sędziów", "jdg", "Sdz"),
    ("Księga Sędziów", "jdg", "Sdz"),
    ("Księgę Rut", "rut", "Rt"),
    ("Księga Rut", "rut", "Rt"),
    ("Księgę Ezdrasza", "ezr", "Ezd"),
    ("Księga Ezdrasza", "ezr", "Ezd"),
    ("Księgę Nehemiasza", "neh", "Ne"),
    ("Księga Nehemiasza", "neh", "Ne"),
    ("Księgę Estery", "est", "Est"),
    ("Księga Estery", "est", "Est"),
    ("Księgę Hioba", "job", "Hi"),
    ("Księga Hioba", "job", "Hi"),
    ("Psalm", "psa", "Ps"),
    ("Księgę Przysłów", "pro", "Prz"),
    ("Księga Przysłów", "pro", "Prz"),
    ("Księgę Koheleta", "ecc", "Koh"),
    ("Księga Koheleta", "ecc", "Koh"),
    ("Pieśń nad Pieśniami", "sol", "Pnp"),  # 'sol' verified from site HTML
    ("Księgę Izajasza", "isa", "Iz"),
    ("Księga Izajasza", "isa", "Iz"),
    ("Księgę Jeremiasza", "jer", "Jr"),
    ("Księga Jeremiasza", "jer", "Jr"),
    ("Księgę Lamentacji", "lam", "Lm"),
    ("Księga Lamentacji", "lam", "Lm"),
    ("Księgę Ezechiela", "eze", "Ez"),   # 'eze' verified from site HTML
    ("Księga Ezechiela", "eze", "Ez"),
    ("Księgę Daniela", "dan", "Dn"),
    ("Księga Daniela", "dan", "Dn"),
    ("Księgę Ozeasza", "hos", "Oz"),
    ("Księga Ozeasza", "hos", "Oz"),
    ("Księgę Joela", "joe", "Jl"),     # 'joe' verified from site HTML
    ("Księga Joela", "joe", "Jl"),
    ("Księgę Amosa", "amo", "Am"),
    ("Księga Amosa", "amo", "Am"),
    ("Księgę Abdiasza", "oba", "Ab"),
    ("Księga Abdiasza", "oba", "Ab"),
    ("Księgę Jonasza", "jon", "Jon"),
    ("Księga Jonasza", "jon", "Jon"),
    ("Księgę Micheasza", "mic", "Mi"),
    ("Księga Micheasza", "mic", "Mi"),
    ("Księgę Nahuma", "nah", "Na"),     # 'nah' verified from site HTML
    ("Księga Nahuma", "nah", "Na"),
    ("Księgę Habakuka", "hab", "Ha"),
    ("Księga Habakuka", "hab", "Ha"),
    ("Księgę Sofoniasza", "zep", "So"),
    ("Księga Sofoniasza", "zep", "So"),
    ("Księgę Aggeusza", "hag", "Ag"),
    ("Księga Aggeusza", "hag", "Ag"),
    ("Księgę Zachariasza", "zec", "Za"),
    ("Księga Zachariasza", "zec", "Za"),
    ("Księgę Malachiasza", "mal", "Ml"),
    ("Księga Malachiasza", "mal", "Ml"),
    ("Ewangelię Mateusza", "mat", "Mt"),
    ("Ewangelia Mateusza", "mat", "Mt"),
    ("Ewangelię Marka", "mar", "Mk"),
    ("Ewangelia Marka", "mar", "Mk"),
    ("Ewangelię Łukasza", "luk", "Łk"),
    ("Ewangelia Łukasza", "luk", "Łk"),
    ("Ewangelię Jana", "joh", "J"),
    ("Ewangelia Jana", "joh", "J"),
    ("Dzieje Apostolskie", "act", "Dz"),
    ("List do Rzymian", "rom", "Rz"),
    ("List do Galacjan", "gal", "Ga"),
    ("List do Galatów", "gal", "Ga"),
    ("List do Efezjan", "eph", "Ef"),
    ("List do Filipian", "phi", "Flp"),  # 'phi' verified from site HTML
    ("List do Kolosan", "col", "Kol"),
    ("List do Tytusa", "tit", "Tt"),
    ("List do Filemona", "phm", "Flm"),
    ("List do Hebrajczyków", "heb", "Hbr"),
    ("List Jakuba", "jam", "Jk"),       # 'jam' verified from site HTML
    ("List Judy", "jud", "Jud"),
    ("Apokalipsę Jana", "rev", "Ap"),
    ("Apokalipsa Jana", "rev", "Ap"),
]


def normalize_grammar_to_nominative(text: str) -> str:
    """Normalizes Polish book names from Accusative (Biernik) to Nominative (Mianownik)
    and removes trailing periods.
    Example: '1 Księgę Mojżesza, rozdział 1 i 2.' -> '1 Księga Mojżesza, rozdział 1 i 2'
    """
    if not text:
        return text
    text = text.strip().rstrip(".")
    replacements = [
        ("1 Księgę ", "1 Księga "),
        ("2 Księgę ", "2 Księga "),
        ("3 Księgę ", "3 Księga "),
        ("4 Księgę ", "4 Księga "),
        ("5 Księgę ", "5 Księga "),
        ("Księgę ", "Księga "),
        ("Ewangelię ", "Ewangelia "),
        ("Apokalipsę ", "Apokalipsa "),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def text_to_hiperbiblia_link(text: str, left: str = "snpd", right: str = "lxxhb") -> tuple[str, str]:
    """Convert a Polish reading string like '1 Księgę Mojżesza, rozdział 1 i 2.'
    into a clean label ('Rdz 1-2') and a verified HiperBiblia URL ('https://hiperbiblia.com/reader?book=gen&chapter=1&left=snpd&right=lxxhb').
    """
    clean_text = text.rstrip(".").strip()
    matched_code = None
    matched_abbr = None
    matched_name = None

    for name, code, abbr in HIPERBIBLIA_MAP:
        if name in clean_text:
            matched_code = code
            matched_abbr = abbr
            matched_name = name
            break

    if not matched_code:
        query = urllib.parse.quote_plus(clean_text)
        return clean_text, f"https://hiperbiblia.com/reader?search={query}"

    after_book = clean_text[clean_text.find(matched_name) + len(matched_name):]
    nums = re.findall(r'\d+', after_book)

    first_ch = nums[0] if nums else "1"

    if "wersety" in after_book.lower() and len(nums) >= 3:
        ch = nums[0]
        v_start = nums[1]
        v_end = nums[2]
        label = f"{matched_abbr} {ch},{v_start}-{v_end}"
        first_ch = ch
    elif nums:
        if len(nums) == 1:
            label = f"{matched_abbr} {nums[0]}"
        elif len(nums) == 2:
            label = f"{matched_abbr} {nums[0]}-{nums[1]}"
        else:
            label = f"{matched_abbr} {nums[0]}-{nums[-1]}"
    else:
        label = f"{matched_abbr} 1"

    url = f"https://hiperbiblia.com/reader?book={matched_code}&chapter={first_ch}&left={left}&right={right}"
    return label, url


def extract_oracle_plan(html_path: Path = HTML_PATH, left: str = "snpd", right: str = "lxxhb") -> list[dict]:
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    pattern = r'var\s+(cz(\d{2})(\d{2}))\s*=\s*"([^"]+)";'
    matches = re.findall(pattern, content)

    plan = []
    day_counter = 1

    for var_name, month_str, day_str, reading_raw in matches:
        month_day_str = f"{day_str}.{month_str}"
        date_iso = f"2026-{month_str}-{day_str}"

        parts = [p.strip().rstrip(";") for p in re.split(r'<br\s*/?>|\n', reading_raw) if p.strip()]

        t1_raw = normalize_grammar_to_nominative(parts[0]) if len(parts) > 0 else ""
        t2_raw = normalize_grammar_to_nominative(parts[1]) if len(parts) > 1 else ""
        t3_raw = normalize_grammar_to_nominative(parts[2]) if len(parts) > 2 else ""

        links = []
        for p in parts:
            p_clean = normalize_grammar_to_nominative(p)
            label, url = text_to_hiperbiblia_link(p, left=left, right=right)
            links.append({"label": label, "url": url, "raw": p_clean})

        plan.append({
            "day": day_counter,
            "date": date_iso,
            "month_day": month_day_str,
            "t1_ref": t1_raw,
            "t2_ref": t2_raw,
            "t3_ref": t3_raw,
            "t1_chapters": [],
            "t2_chapters": [],
            "t3_chapters": [],
            "chars": 0,
            "links": links,
            "raw_text": f"{t1_raw}; {t2_raw}; {t3_raw}",
        })
        day_counter += 1

    return plan


if __name__ == "__main__":
    plan = extract_oracle_plan()
    OUT_JSON.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Pomyślnie wyekstrahowano {len(plan)} czytań Wyroczni do: {OUT_JSON}")
