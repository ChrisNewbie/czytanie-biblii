#!/usr/bin/env python3
"""Export Official Christadelphian Bible Reading Plan to EPUB 3 E-book for Kindle and e-readers."""
from __future__ import annotations

import html
import io
from pathlib import Path
import zipfile


def build_month_xhtml(month_num: int, days_in_month: list[dict]) -> str:
    month_names = [
        "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
        "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
    ]
    m_name = month_names[month_num]

    days_html = []
    for day in days_in_month:
        day_num = day["day"]
        date_str = f" ({day['date']})" if day.get("date") else ""

        links = day.get("links", [])
        l1 = links[0] if len(links) > 0 else {"url": "#", "label": day.get("t1_ref", "")}
        l2 = links[1] if len(links) > 1 else {"url": "#", "label": day.get("t2_ref", "")}
        l3 = links[2] if len(links) > 2 else {"url": "#", "label": day.get("t3_ref", "")}

        t1_link = f'<a href="{html.escape(l1["url"])}">{html.escape(day["t1_ref"])} ({html.escape(l1["label"])})</a>'
        t2_link = f'<a href="{html.escape(l2["url"])}">{html.escape(day["t2_ref"])} ({html.escape(l2["label"])})</a>'
        t3_link = f'<a href="{html.escape(l3["url"])}">{html.escape(day["t3_ref"])} ({html.escape(l3["label"])})</a>'

        days_html.append(f"""
        <section class="day-section" id="day_{day_num}">
          <h2>Dzień {day_num}{html.escape(date_str)}</h2>
          <div class="reading-track">
            <span class="track-label">ST (Prawo i Historia):</span>
            <span class="track-content">{t1_link}</span>
          </div>
          <div class="reading-track">
            <span class="track-label">ST (Poezja i Prorocy):</span>
            <span class="track-content">{t2_link}</span>
          </div>
          <div class="reading-track">
            <span class="track-label">Nowy Testament (x2):</span>
            <span class="track-content">{t3_link}</span>
          </div>
          <hr />
        </section>
        """)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pl">
<head>
  <title>{m_name}</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
  <h1>{m_name}</h1>
  {''.join(days_html)}
</body>
</html>
"""


def export_epub(plan: list[dict], output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    months: list[list[dict]] = [[] for _ in range(12)]
    for i, day in enumerate(plan):
        month_idx = min(i // 31, 11)
        if day.get("date"):
            try:
                m = int(day["date"].split("-")[1]) - 1
                if 0 <= m < 12:
                    month_idx = m
            except Exception:
                pass
        months[month_idx].append(day)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # 1. mimetype
        z.writestr("mimetype", b"application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # 2. META-INF/container.xml
        container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        z.writestr("META-INF/container.xml", container_xml)

        # 3. OEBPS/styles.css
        styles_css = """
body { font-family: sans-serif; line-height: 1.5; margin: 1em; }
h1 { font-size: 1.6em; color: #1a202c; border-bottom: 2px solid #3182ce; padding-bottom: 0.3em; }
h2 { font-size: 1.2em; color: #2b6cb0; margin-top: 1em; }
.day-section { margin-bottom: 1.5em; }
.reading-track { margin: 0.4em 0; }
.track-label { font-weight: bold; color: #4a5568; display: inline-block; min-width: 180px; }
.track-content a { color: #2b6cb0; text-decoration: none; font-weight: bold; }
hr { border: 0; border-top: 1px solid #e2e8f0; margin-top: 1em; }
"""
        z.writestr("OEBPS/styles.css", styles_css)

        # 4. Write Month XHTML files
        manifest_items = ['<item id="styles" href="styles.css" media-type="text/css"/>']
        spine_items = []
        nav_toc_items = []

        month_names = [
            "", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
            "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
        ]

        for m_num in range(1, 13):
            m_days = months[m_num - 1]
            if not m_days:
                continue
            filename = f"month_{m_num:02d}.xhtml"
            z.writestr(f"OEBPS/{filename}", build_month_xhtml(m_num, m_days))
            manifest_items.append(f'<item id="m_{m_num}" href="{filename}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="m_{m_num}"/>')
            nav_toc_items.append(f'<li><a href="{filename}">{month_names[m_num]}</a></li>')

        # 5. OEBPS/nav.xhtml
        nav_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="pl">
<head><title>Spis Treści</title></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Spis Treści — Oficjalny Plan Czytania Biblii</h1>
    <ol>
      {''.join(nav_toc_items)}
    </ol>
  </nav>
</body>
</html>"""
        z.writestr("OEBPS/nav.xhtml", nav_xhtml)
        manifest_items.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')

        # 6. OEBPS/content.opf
        content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="BookId">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="BookId">urn:uuid:roberts-official-bible-plan-365</dc:identifier>
    <dc:title>Oficjalny Plan Czytania Biblii — Chrystadelfianie</dc:title>
    <dc:language>pl</dc:language>
    <dc:creator>Robert Roberts</dc:creator>
    <meta property="dcterms:modified">2026-08-12T12:00:00Z</meta>
  </metadata>
  <manifest>
    {''.join(manifest_items)}
  </manifest>
  <spine>
    {''.join(spine_items)}
  </spine>
</package>"""
        z.writestr("OEBPS/content.opf", content_opf)

    output_file.write_bytes(buf.getvalue())
    print(f"Zapisano E-book EPUB dla Kindle: {output_file}")


if __name__ == "__main__":
    from roberts_engine import build_synchronous_roberts_plan
    plan = build_synchronous_roberts_plan(year=2026)
    export_epub(plan, Path("output/Biblia_Plan_Robertsa_2026.epub"))
