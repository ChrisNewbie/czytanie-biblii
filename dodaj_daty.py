#!/usr/bin/env python3
"""Stamp a date column onto a reading-plan CSV produced by make_schedule.py.

Needs no database and no make_schedule.py: it only reads the plan CSV, computes
data = start + (dzien - 1) days for every row and inserts it right after the
'dzien' column. Generate the dated plan for whatever start date you like, as
often as you like, from the same base CSV.

Alongside the CSV it also writes an HTML version with clickable Deon links,
because LibreOffice/Excel do not turn the CSV link column into hyperlinks.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import html
import sys
import urllib.parse
from pathlib import Path

LINKS_COLUMN = "linki"


def link_label(url: str) -> str:
    """Decode the human-readable skrot (e.g. 'Rdz 1') back out of a Deon URL."""
    _, _, query = url.partition("skrot=")
    if not query:
        return url
    return urllib.parse.unquote(query, encoding="iso-8859-2")


def render_cell(column: str, value: str) -> str:
    if column == LINKS_COLUMN:
        links = [
            f'<a href="{html.escape(url, quote=True)}">{html.escape(link_label(url))}</a>'
            for url in value.split()
        ]
        return " ".join(links)
    return html.escape(value)


def build_html(header: list[str], data_rows: list[list[str]], title: str) -> str:
    numeric = {"dzien", "znaki"}
    thead = "".join(f"<th>{html.escape(col)}</th>" for col in header)
    body_rows = []
    for row in data_rows:
        cells = []
        for column, value in zip(header, row):
            css = ' class="num"' if column in numeric else ""
            cells.append(f"<td{css}>{render_cell(column, value)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    tbody = "\n".join(body_rows)
    escaped_title = html.escape(title)
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escaped_title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 1.5rem; color: #1a1a1a; }}
  h1 {{ font-size: 1.2rem; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
  th, td {{ border: 1px solid #ccc; padding: 4px 8px; vertical-align: top; text-align: left; }}
  th {{ position: sticky; top: 0; background: #f0f0f0; }}
  tr:nth-child(even) td {{ background: #fafafa; }}
  td.num {{ text-align: right; white-space: nowrap; }}
  a {{ margin-right: 6px; white-space: nowrap; }}
</style>
</head>
<body>
<h1>{escaped_title}</h1>
<table>
<thead><tr>{thead}</tr></thead>
<tbody>
{tbody}
</tbody>
</table>
</body>
</html>
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Plan CSV from make_schedule.py.")
    parser.add_argument("start", type=datetime.date.fromisoformat, help="First reading day (YYYY-MM-DD).")
    parser.add_argument("--out", type=Path, help="Output CSV (default: <input>_<start>.csv).")
    parser.add_argument("--no-html", action="store_true", help="Skip the HTML file with clickable links.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.input.exists():
        print(f"Brak pliku wejściowego: {args.input}", file=sys.stderr)
        return 2

    # utf-8-sig transparently strips the BOM that make_schedule.py writes.
    with args.input.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if not rows:
        print("Pusty plik CSV.", file=sys.stderr)
        return 2

    header = rows[0]
    if "dzien" not in header:
        print("Brak kolumny 'dzien' w nagłówku.", file=sys.stderr)
        return 2
    if "data" in header:
        print("Kolumna 'data' już istnieje — nic do zrobienia.", file=sys.stderr)
        return 2

    day_index = header.index("dzien")
    new_header = header[: day_index + 1] + ["data"] + header[day_index + 1 :]

    out_rows = [new_header]
    for row in rows[1:]:
        if not row:
            continue
        day_number = int(row[day_index])
        date = (args.start + datetime.timedelta(days=day_number - 1)).isoformat()
        out_rows.append(row[: day_index + 1] + [date] + row[day_index + 1 :])

    out_path = args.out or args.input.with_name(f"{args.input.stem}_{args.start.isoformat()}.csv")
    with out_path.open("w", newline="", encoding="utf-8-sig") as handle:
        csv.writer(handle).writerows(out_rows)
    print(f"Zapisano {len(out_rows) - 1} dni do {out_path} (start: {args.start.isoformat()}).")

    if not args.no_html:
        html_path = out_path.with_suffix(".html")
        title = f"Harmonogram czytania — start {args.start.isoformat()} ({len(out_rows) - 1} dni)"
        html_path.write_text(build_html(new_header, out_rows[1:], title), encoding="utf-8")
        print(f"Zapisano HTML z klikalnymi linkami do {html_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
