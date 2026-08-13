#!/usr/bin/env python3
"""Export Robert Roberts Bible Reading Plan to iCal (.ics) Calendar file."""
from __future__ import annotations

import datetime
from pathlib import Path


def export_ics(plan: list[dict], output_file: Path, start_date: datetime.date | None = None):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if not start_date:
        start_date = datetime.date(2026, 1, 1)

    events = []
    for day in plan:
        day_num = day["day"]
        curr_date = start_date + datetime.timedelta(days=day_num - 1)
        next_date = curr_date + datetime.timedelta(days=1)
        dtstart = curr_date.strftime("%Y%m%d")
        dtend = next_date.strftime("%Y%m%d")

        summary = f"Biblia (Dzień {day_num}): {day['t1_ref']}; {day['t2_ref']}; {day['t3_ref']}"

        desc_lines = [
            f"Oficjalny Plan Czytania Biblii — Dzień {day_num}",
            f"1. ST (Prawo/Historia): {day['t1_ref']}",
            f"2. ST (Poezja/Prorocy): {day['t2_ref']}",
            f"3. NT (x2 w roku): {day['t3_ref']}",
            "",
            "Linki HiperBiblia.com (Czytnik Interliniarny):"
        ]
        for link in day.get("links", []):
            label = link.get("label") or f"{link.get('abbr', '')} {link.get('num', '')}".strip()
            desc_lines.append(f"- {label}: {link['url']}")

        description = "\\n".join(desc_lines)

        events.append(f"""BEGIN:VEVENT
UID:roberts-plan-day-{day_num}-{dtstart}@biblia-czytanie
DTSTAMP:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART;VALUE=DATE:{dtstart}
DTEND;VALUE=DATE:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
STATUS:CONFIRMED
END:VEVENT""")

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Biblia Czytanie//Plan Robertsa 365//PL
X-WR-CALNAME:Biblia — Plan Robertsa (HiperBiblia)
X-WR-TIMEZONE:Europe/Warsaw
{''.join(events)}
END:VCALENDAR
"""
    output_file.write_text(ics_content, encoding="utf-8")
    print(f"Zapisano plik kalendarza iCal: {output_file}")


if __name__ == "__main__":
    from roberts_engine import build_synchronous_roberts_plan
    plan = build_synchronous_roberts_plan(year=2026)
    export_ics(plan, Path("output/Biblia_Plan_Robertsa_2026.ics"), datetime.date(2026, 1, 1))
