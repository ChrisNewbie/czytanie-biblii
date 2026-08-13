#!/usr/bin/env python3
"""Master Builder Script for the Official Christadelphian Bible Reading Suite (Robert Roberts).

Single Source of Truth: Uses official daily readings from prawdy-biblijne-index.html.
Builds all products (PWA Web App, Kindle EPUB, iCal Calendar, CSV & HTML)
with complete custom Favicon suite for the fixed calendar year (Jan 1 to Dec 31).
"""
from __future__ import annotations

import argparse
import datetime
import shutil
from pathlib import Path
import sys

from export_csv import export_csv
from export_epub import export_epub
from export_ics import export_ics
from export_pwa import export_pwa
from generate_favicons import generate_icons
from roberts_engine import build_synchronous_roberts_plan


def main():
    parser = argparse.ArgumentParser(description="Master Builder for Official Christadelphian Bible Suite")
    parser.add_argument("--year", type=int, default=2026, help="Calendar year (default: 2026)")
    parser.add_argument("--left", type=str, default="snpd", help="Left translation code (default: snpd)")
    parser.add_argument("--right", type=str, default="lxxhb", help="Right translation code (default: lxxhb)")
    parser.add_argument("--out-dir", type=Path, default=Path("output"), help="Output directory")
    args = parser.parse_args()

    print(f"\n=== Budowanie Oficjalnego Pakietu Czytania Biblii (Wyrocznia: Rok {args.year}) ===")
    print(f"• Źródło prawd: prawdy-biblijne-index.html (Oficjalny serwis chrystadelfian)")
    print(f"• Zastosowanie: Stały kalendarz chrystadelfiański na świecie (1 Sty – 31 Gru)")
    print(f"• HiperBiblia parametry: left='{args.left}', right='{args.right}'")
    print(f"• Katalog wyjściowy: {args.out_dir.resolve()}\n")

    # 0. Generate complete Favicon suite in root directory
    root_dir = Path(".")
    generate_icons(root_dir)

    # 1. Generate plan directly from official Oracle
    plan = build_synchronous_roberts_plan(year=args.year, left=args.left, right=args.right)

    # 2. Export CSV & HTML tables (Vanilla JS & jQuery versions)
    csv_file = args.out_dir / f"harmonogram_chrystadelfianie_{args.year}.csv"
    html_file = args.out_dir / f"harmonogram_chrystadelfianie_{args.year}.html"
    jquery_html_file = args.out_dir / f"harmonogram_chrystadelfianie_{args.year}_jquery.html"
    export_csv(plan, csv_file, html_file, jquery_html_file)

    # 3. Create root index.html copy for GitHub Pages root hosting
    root_index = Path("index.html")
    shutil.copyfile(html_file, root_index)

    # Copy icons to output directory and PWA directory
    pwa_dir = args.out_dir / "pwa"
    pwa_dir.mkdir(parents=True, exist_ok=True)
    icon_files = ["favicon.svg", "favicon.ico", "favicon.png", "apple-touch-icon.png", "icon-512.png"]
    for icon_name in icon_files:
        src = root_dir / icon_name
        if src.exists():
            shutil.copyfile(src, args.out_dir / icon_name)
            shutil.copyfile(src, pwa_dir / icon_name)

    # 4. Export PWA
    export_pwa(plan, pwa_dir)

    # 5. Export Kindle EPUB
    epub_file = args.out_dir / f"Biblia_Plan_Robertsa_{args.year}.epub"
    export_epub(plan, epub_file)

    # 6. Export iCal (.ics)
    ics_file = args.out_dir / f"Biblia_Plan_Robertsa_{args.year}.ics"
    start_date = datetime.date(args.year, 1, 1)
    export_ics(plan, ics_file, start_date)

    print("\n=======================================================")
    print(f" SUKCES! Zbudowano oficjalny pakiet Wyroczni z Favikonami na rok {args.year}:")
    print(f" 1. GitHub Pages (root):   {root_index.resolve()}")
    print(f" 2. Aplikacja PWA:         {pwa_dir.resolve() / 'index.html'}")
    print(f" 3. Strona Vanilla JS:      {html_file.resolve()}")
    print(f" 4. Strona z jQuery 3.7.1:  {jquery_html_file.resolve()}")
    print(f" 5. E-book Kindle:         {epub_file.resolve()}")
    print(f" 6. Kalendarz iCal:        {ics_file.resolve()}")
    print(f" 7. Arkusz CSV:            {csv_file.resolve()}")
    print("=======================================================\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
