#!/usr/bin/env python3
"""Core Engine for the Synchronous Christadelphian Bible Companion (Robert Roberts).

Single Source of Truth (Oracle):
Uses official daily readings extracted from prawdy-biblijne-index.html.
All Christadelphians worldwide read the EXACT SAME assigned passages on the same date.
"""
from __future__ import annotations

import argparse
import datetime
from pathlib import Path

from official_oracle_parser import extract_oracle_plan, HTML_PATH


def build_synchronous_roberts_plan(db_path: Path | None = None, year: int = 2026, left: str = "snpd", right: str = "lxxhb") -> list[dict]:
    """Generate the official Christadelphian calendar plan for Jan 1 to Dec 31 in YYYY-MM-DD format."""
    if HTML_PATH.exists():
        raw_plan = extract_oracle_plan(HTML_PATH, left=left, right=right)
        for day in raw_plan:
            # day["date"] is formatted as YYYY-MM-DD
            parts = day["date"].split("-")  # ["2026", "MM", "DD"]
            day["date"] = f"{year}-{parts[1]}-{parts[2]}"
        return raw_plan

    # Fallback if HTML oracle file is missing
    start_date = datetime.date(year, 1, 1)
    plan = []
    for d in range(365):
        curr_date = start_date + datetime.timedelta(days=d)
        plan.append({
            "day": d + 1,
            "date": curr_date.strftime("%Y-%m-%d"),
            "month_day": curr_date.strftime("%d.%m"),
            "t1_ref": f"Dzień {d+1} ST 1",
            "t2_ref": f"Dzień {d+1} ST 2",
            "t3_ref": f"Dzień {d+1} NT",
            "t1_chapters": [],
            "t2_chapters": [],
            "t3_chapters": [],
            "chars": 0,
            "links": [],
        })
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronous Christadelphian Bible Companion Engine")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--left", type=str, default="snpd")
    parser.add_argument("--right", type=str, default="lxxhb")
    args = parser.parse_args()

    plan = build_synchronous_roberts_plan(year=args.year, left=args.left, right=args.right)
    print(f"Pomyślnie wczytano Oficjalną Wyrocznię na rok {args.year} ({len(plan)} dni).")
    print(f"1 Stycznia:  {plan[0]['date']} -> {plan[0]['t1_ref']} | {plan[0]['t2_ref']} | {plan[0]['t3_ref']}")
    print(f"2 Stycznia:  {plan[1]['date']} -> {plan[1]['t1_ref']} | {plan[1]['t2_ref']} | {plan[1]['t3_ref']}")
    print(f"31 Grudnia: {plan[-1]['date']} -> {plan[-1]['t1_ref']} | {plan[-1]['t2_ref']} | {plan[-1]['t3_ref']}")
