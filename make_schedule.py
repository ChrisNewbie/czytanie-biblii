#!/usr/bin/env python3
"""Generate a compact Bible reading plan from the Deon SQLite database.

The plan measures volume by the number of characters in verse texts, aggregated
per chapter. A chapter is indivisible; a day is a contiguous range of chapters.

Two modes:
  * mixed (default): several parallel tracks per day, each advancing through its
    own books in canonical order. --tracks 6 (default) splits the canon by genre
    so a dull stretch in one track (genealogies, sacrifice law) always runs
    alongside livelier material, and similar books (the synoptics) never follow
    each other back to back; --tracks 3 is the older Old Testament / New
    Testament / Psalms layout. Psalms are always their own track: each psalm is
    read once and whole on its own day, evenly spread, so some days carry none.
  * canonical: a single track, Genesis -> Revelation, balanced by characters

The first column is the day number (1, 2, 3, ...); the plan carries no dates, so
one plan works for any start date. Use dodaj_daty.py to stamp a date column onto
this CSV later, without the database.

Output is a small CSV (no verse text) with, per day, the reference ranges, the
character count and one durable Deon link per chapter. Deon's otworz.php?skrot=
resolves a single chapter and the skrot must be encoded in ISO-8859-2 (its
rozdzial.php?id= target is session-bound and useless as a shareable address).
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
import urllib.parse
from pathlib import Path

DEON_BASE = "https://biblia.deon.pl/otworz.php?skrot="
PSALMS_BOOK_ID = 23
DEFAULT_DB = Path(__file__).resolve().parent.parent / "Bible-downloader" / "Biblia.db"

# Track layouts. Each track is (column title, inclusive book_id ranges); books
# keep their canonical order inside a track. The book_id ranges follow the Deon
# database numbering of the Biblia Tysiaclecia canon (1 Rdz ... 73 Ap).
TRACK_LAYOUTS: dict[int, list[tuple[str, list[tuple[int, int]]]]] = {
    3: [
        ("Stary Testament", [(1, 22), (24, 46)]),
        ("Nowy Testament", [(47, 73)]),
        ("Psalm", [(23, 23)]),
    ],
    6: [
        ("Pięcioksiąg i historyczne", [(1, 21)]),
        ("Prorocy", [(29, 46)]),
        ("Mądrościowe", [(22, 22), (24, 28)]),
        ("Psalm", [(23, 23)]),
        ("Ewangelie i Dzieje", [(47, 51)]),
        ("Listy i Apokalipsa", [(52, 73)]),
    ],
}


def deon_link(abbreviation: str, chapter_number: int) -> str:
    skrot = f"{abbreviation} {chapter_number}"
    return DEON_BASE + urllib.parse.quote(skrot, encoding="iso-8859-2", safe="")


def load_chapters(db_path: Path) -> list[dict]:
    """Return all chapters in canonical order with their character counts."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT c.chapter_id,
                   c.book_id,
                   b.abbreviation AS abbr,
                   c.chapter_number AS num,
                   COALESCE(SUM(LENGTH(v.verse_text)), 0) AS chars
            FROM chapters c
            JOIN books b ON b.book_id = c.book_id
            LEFT JOIN verses v ON v.chapter_id = c.chapter_id
            GROUP BY c.chapter_id
            ORDER BY c.book_id, c.chapter_number
            """
        ).fetchall()
    finally:
        conn.close()
    return [dict(row) for row in rows]


def compress_refs(chapters: list[dict]) -> str:
    """Turn a contiguous chapter list into a reference like 'Rdz 48-50; Wj 1'."""
    segments: list[dict] = []
    for ch in chapters:
        if segments and segments[-1]["abbr"] == ch["abbr"] and ch["num"] == segments[-1]["end"] + 1:
            segments[-1]["end"] = ch["num"]
        else:
            segments.append({"abbr": ch["abbr"], "start": ch["num"], "end": ch["num"]})
    parts = []
    for seg in segments:
        if seg["start"] == seg["end"]:
            parts.append(f"{seg['abbr']} {seg['start']}")
        else:
            parts.append(f"{seg['abbr']} {seg['start']}-{seg['end']}")
    return "; ".join(parts)


def day_links(chapters: list[dict]) -> str:
    return " ".join(deon_link(ch["abbr"], ch["num"]) for ch in chapters)


def _count_groups(weights: list[int], capacity: int) -> int:
    groups = 1
    current = 0
    for weight in weights:
        if current and current + weight > capacity:
            groups += 1
            current = 0
        current += weight
    return groups


def _pack_by_capacity(chapters: list[dict], capacity: int) -> list[list[dict]]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    current_sum = 0
    for ch in chapters:
        if current and current_sum + ch["chars"] > capacity:
            groups.append(current)
            current = []
            current_sum = 0
        current.append(ch)
        current_sum += ch["chars"]
    if current:
        groups.append(current)
    return groups


def _split_group(group: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split a group in two contiguous parts minimizing the heavier part."""
    total = sum(ch["chars"] for ch in group)
    best_index = 1
    best_cost = None
    prefix = 0
    for index in range(len(group) - 1):
        prefix += group[index]["chars"]
        cost = max(prefix, total - prefix)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_index = index + 1
    return group[:best_index], group[best_index:]


def balanced_partition(chapters: list[dict], days: int) -> list[list[dict]]:
    """Split a chapter sequence into exactly `days` contiguous, balanced groups.

    Minimize the heaviest day: binary-search the smallest capacity that fits the
    chapters into at most `days` greedy groups, then, if that leaves fewer than
    `days` groups, keep splitting the heaviest multi-chapter group (which never
    raises the maximum) until exactly `days` non-empty groups remain.
    """
    if days >= len(chapters):
        return [[ch] for ch in chapters]

    weights = [ch["chars"] for ch in chapters]
    low = max(weights)
    high = sum(weights)
    while low < high:
        mid = (low + high) // 2
        if _count_groups(weights, mid) <= days:
            high = mid
        else:
            low = mid + 1
    groups = _pack_by_capacity(chapters, low)

    while len(groups) < days:
        heaviest = max(
            (g for g in groups if len(g) > 1),
            key=lambda g: sum(ch["chars"] for ch in g),
        )
        position = groups.index(heaviest)
        left, right = _split_group(heaviest)
        groups[position : position + 1] = [left, right]
    return groups


def distribute_one_per_day(chapters: list[dict], days: int) -> list[list[dict]]:
    """Place each chapter whole on its own distinct day, evenly spread, in order.

    Exactly one chapter per used day (never two together), each chapter exactly
    once regardless of its length; the remaining days stay empty. Used for Psalms
    so every psalm gets a full day of its own. Falls back to length-based spread
    only if there are more chapters than days (no room for one-per-day).
    """
    count = len(chapters)
    if count > days:
        return distribute_by_length(chapters, days)
    per_day: list[list[dict]] = [[] for _ in range(days)]
    previous = -1
    for index, ch in enumerate(chapters):
        target = int((index + 0.5) * days / count)
        day = min(max(target, previous + 1), days - 1)
        per_day[day].append(ch)
        previous = day
    return per_day


def distribute_by_length(chapters: list[dict], days: int) -> list[list[dict]]:
    """Spread chapters across the days proportionally to their character length.

    Each chapter is placed on the day matching the position of its character
    midpoint in the track. Long chapters get lonely days; short ones cluster, so
    the per-day character load of the track stays even. Reading order is kept.
    """
    per_day: list[list[dict]] = [[] for _ in range(days)]
    total = sum(ch["chars"] for ch in chapters)
    if total == 0:
        return per_day
    seen = 0
    for ch in chapters:
        midpoint = seen + ch["chars"] / 2
        day = min(int(midpoint / total * days), days - 1)
        per_day[day].append(ch)
        seen += ch["chars"]
    return per_day


def select_track(chapters: list[dict], ranges: list[tuple[int, int]]) -> list[dict]:
    return [c for c in chapters if any(lo <= c["book_id"] <= hi for lo, hi in ranges)]


def spread_track(track: list[dict], days: int, is_psalms: bool) -> list[list[dict]]:
    """Lay one track out over the days, keeping its canonical reading order.

    Psalms get one whole psalm per day on evenly spread days. A track with more
    chapters than days must run every day, so it is cut into `days` balanced
    contiguous portions; a shorter track is spread by character length instead,
    which leaves the days in between empty rather than forcing tiny portions.
    """
    if is_psalms:
        return distribute_one_per_day(track, days)
    if len(track) > days:
        return balanced_partition(track, days)
    return distribute_by_length(track, days)


def smooth_daily_load(
    per_track_days: list[list[list[dict]]], days: int, distinct: list[bool], max_passes: int = 200
) -> list[list[list[dict]]]:
    """Even out the daily character totals by nudging chapters one day sideways.

    Every track is laid out sensibly on its own, but independent tracks stack
    their heavy days on top of each other by accident, so some days end up two
    or three times the average. This is a local search: a chapter moves to a
    neighbouring day whenever that day, with the chapter added, would still be
    lighter than the day it left — which strictly lowers the spread and repeats
    until nothing improves. Chapters stay whole and in canonical order inside
    their track, a track that ran every day keeps running every day, and a track
    limited to one chapter per day (psalms) keeps that limit.
    """
    load = [0] * days
    items: list[list[list]] = []
    counts: list[list[int]] = []
    dense: list[bool] = []
    for track_days in per_track_days:
        track_items = []
        for day, portion in enumerate(track_days):
            for ch in portion:
                track_items.append([ch, day])
                load[day] += ch["chars"]
        items.append(track_items)
        counts.append([len(portion) for portion in track_days])
        dense.append(all(track_days))

    for _ in range(max_passes):
        moved = False
        for track, track_items in enumerate(items):
            for index, item in enumerate(track_items):
                chapter, day = item
                weight = chapter["chars"]
                if dense[track] and counts[track][day] == 1:
                    continue
                previous = track_items[index - 1][1] if index else -1
                following = track_items[index + 1][1] if index + 1 < len(track_items) else days
                for new_day in (day - 1, day + 1):
                    if not 0 <= new_day < days:
                        continue
                    if new_day < day and (new_day < previous or (distinct[track] and new_day == previous)):
                        continue
                    if new_day > day and (new_day > following or (distinct[track] and new_day == following)):
                        continue
                    if load[new_day] + weight >= load[day]:
                        continue
                    load[day] -= weight
                    load[new_day] += weight
                    counts[track][day] -= 1
                    counts[track][new_day] += 1
                    item[1] = new_day
                    moved = True
                    break
        if not moved:
            break

    smoothed: list[list[list[dict]]] = []
    for track_items in items:
        track_days = [[] for _ in range(days)]
        for chapter, day in track_items:
            track_days[day].append(chapter)
        smoothed.append(track_days)
    return smoothed


def build_mixed_rows(chapters: list[dict], days: int, tracks: int) -> tuple[list[list], list[str], list[int]]:
    layout = TRACK_LAYOUTS[tracks]
    is_psalms = [ranges == [(PSALMS_BOOK_ID, PSALMS_BOOK_ID)] for _, ranges in layout]
    per_track_days = [
        spread_track(select_track(chapters, ranges), days, psalms)
        for (_, ranges), psalms in zip(layout, is_psalms)
    ]
    per_track_days = smooth_daily_load(per_track_days, days, is_psalms)

    header = ["dzien"] + [title for title, _ in layout] + ["znaki", "linki"]
    rows: list[list] = []
    day_chars: list[int] = []
    for day in range(days):
        track_day = [track[day] for track in per_track_days]
        all_day = [ch for portion in track_day for ch in portion]
        chars = sum(c["chars"] for c in all_day)
        day_chars.append(chars)
        rows.append(
            [day + 1]
            + [compress_refs(portion) for portion in track_day]
            + [chars, day_links(all_day)]
        )
    return rows, header, day_chars


def build_canonical_rows(chapters: list[dict], days: int) -> tuple[list[list], list[str], list[int]]:
    groups = balanced_partition(chapters, days)
    header = ["dzien", "czytanie", "znaki", "linki"]
    rows: list[list] = []
    day_chars: list[int] = []
    for day, group in enumerate(groups):
        chars = sum(c["chars"] for c in group)
        day_chars.append(chars)
        rows.append(
            [
                day + 1,
                compress_refs(group),
                chars,
                day_links(group),
            ]
        )
    return rows, header, day_chars


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to the Deon SQLite database.")
    parser.add_argument("--days", type=int, default=340, help="Number of reading days (default 340: buffer for missed days).")
    parser.add_argument("--mode", choices=["mixed", "canonical"], default="mixed", help="Reading plan layout.")
    parser.add_argument(
        "--tracks",
        type=int,
        choices=sorted(TRACK_LAYOUTS),
        default=6,
        help="Parallel tracks per day in mixed mode: 6 splits the canon by genre (default), 3 is Old Testament / New Testament / Psalms.",
    )
    parser.add_argument("--out", type=Path, default=Path("harmonogram.csv"), help="Output CSV path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.db.exists():
        print(f"Brak pliku bazy: {args.db}", file=sys.stderr)
        return 2
    if args.days < 1:
        print("--days musi być dodatnie", file=sys.stderr)
        return 2

    chapters = load_chapters(args.db)
    if args.mode == "mixed":
        rows, header, day_chars = build_mixed_rows(chapters, args.days, args.tracks)
    else:
        rows, header, day_chars = build_canonical_rows(chapters, args.days)

    # utf-8-sig adds a BOM so Polish Excel detects UTF-8; LibreOffice strips it fine.
    with args.out.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)

    lo = min(day_chars)
    hi = max(day_chars)
    avg = sum(day_chars) / len(day_chars)
    layout = f"{args.mode}, {args.tracks} wątki" if args.mode == "mixed" else args.mode
    print(f"Zapisano {len(rows)} dni do {args.out} (tryb: {layout}).")
    print(f"Znaki dziennie -> min: {lo}  średnia: {avg:.0f}  max: {hi}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
