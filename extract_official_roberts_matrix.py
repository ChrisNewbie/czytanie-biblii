#!/usr/bin/env python3
"""Extractor for the Official Polish Christadelphian Bible Companion Matrix from prawdy-biblijne-index.html.

Extracts all 365 daily reading strings (var czMMDD = "...") into a structured JSON / Python mapping
to ensure 100% fidelity with the official Polish Christadelphian website.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HTML_PATH = Path(__file__).resolve().parent / "prawdy-biblijne-index.html"
OUT_JSON = Path(__file__).resolve().parent / "official_christadelphian_plan.json"


def parse_official_matrix(html_path: Path) -> dict[str, str]:
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    
    # Match pattern: var czMMDD = "...";
    pattern = r'var\s+(cz\d{4})\s*=\s*"([^"]+)";'
    matches = re.findall(pattern, content)

    print(f"Znaleziono {len(matches)} oficjalnych wpisów czytań w pliku HTML.")
    
    matrix = {}
    for var_name, reading_html in matches:
        # Clean <br /> tags to standard formatting
        clean_text = reading_html.replace("<br />", "\n").replace("<br>", "\n").strip()
        matrix[var_name] = clean_text
    
    return matrix


if __name__ == "__main__":
    if not HTML_PATH.exists():
        print(f"Nie znaleziono pliku: {HTML_PATH}")
    else:
        matrix = parse_official_matrix(HTML_PATH)
        OUT_JSON.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Zapisano oficjalną macierz do: {OUT_JSON}")
        if "cz0101" in matrix:
            print(f"Przykładowe czytanie na 1 Stycznia (cz0101):\n{matrix['cz0101']}")
        if "cz0812" in matrix:
            print(f"\nPrzykładowe czytanie na DZISIAJ (12 Sierpnia - cz0812):\n{matrix['cz0812']}")
