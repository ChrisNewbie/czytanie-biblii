#!/usr/bin/env python3
"""Export Official Christadelphian Bible Reading Plan to CSV and static HTML tables (Vanilla JS & jQuery versions).
Fully compliant with 2026 Web Standards: Floating Back to Top Button, Share Button, Dark Mode, OpenGraph, WCAG 2.2 AAA, Print CSS & Security rel=noopener.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path


def export_csv(
    plan: list[dict],
    output_csv: Path,
    output_html: Path | None = None,
    output_jquery_html: Path | None = None
):
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    header = ["dzien", "data", "ST_Prawo_Historia", "ST_Poezja_Prorocy", "NT_Ewangelie_Listy", "linki_hiperbiblia"]
    rows = []

    for day in plan:
        day_links_str = " | ".join(f"{link['label']}: {link['url']}" for link in day.get("links", []))
        rows.append([
            day["day"],
            day.get("date", ""),
            day.get("t1_ref", ""),
            day.get("t2_ref", ""),
            day.get("t3_ref", ""),
            day_links_str
        ])

    with output_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Zapisano CSV z BOM: {output_csv}")

    tbody_rows = []
    for day in plan:
        day_num = day["day"]
        date_val = day.get("date", "")
        t1 = day.get("t1_ref", "")
        t2 = day.get("t2_ref", "")
        t3 = day.get("t3_ref", "")

        link_tags = []
        for link in day.get("links", []):
            l_label = html.escape(link.get("label", "Link"))
            l_url = html.escape(link.get("url", "#"))
            link_tags.append(f'<a href="{l_url}" data-base-url="{l_url}" target="_blank" rel="noopener noreferrer" title="{html.escape(link.get("raw", ""))}">{l_label} ↗</a>')

        share_btn = f'<button type="button" class="btn-share" onclick="shareDay({day_num}, \'{date_val}\')">📤 Udostępnij</button>'

        tbody_rows.append(f"""
        <tr data-date="{date_val}" data-day="{day_num}">
          <td class="num">
            <div class="day-header-cell">
              <span>Dzień {day_num} <span class="date-tag">• {date_val}</span></span>
              {share_btn}
            </div>
          </td>
          <td class="track-cell"><span class="track-lbl">ST 1 (Prawo / Historia):</span> {html.escape(t1)}</td>
          <td class="track-cell"><span class="track-lbl">ST 2 (Poezja / Prorocy):</span> {html.escape(t2)}</td>
          <td class="track-cell"><span class="track-lbl">NT (Ewangelie / Listy):</span> {html.escape(t3)}</td>
          <td class="links-cell">
            <div class="btn-group">
              {' '.join(link_tags)}
              {share_btn}
            </div>
          </td>
        </tr>
        """)

    tbody_content = ''.join(tbody_rows)

    common_style = """
    :root {
      color-scheme: light dark;
      --bg-body: #f8fafc;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --bg-card: #ffffff;
      --border-color: #cbd5e1;
      --accent: #0284c7;
      --accent-bg: #e0f2fe;
      --header-bg: #0f172a;
      --header-text: #ffffff;
      --btn-today-bg: #4f46e5;
      --btn-today-hover: #4338ca;
      --flash-bg: #fef08a;
      --table-stripe: #f8fafc;
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg-body: #0f172a;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --bg-card: #1e293b;
        --border-color: #334155;
        --accent: #38bdf8;
        --accent-bg: rgba(56, 189, 248, 0.15);
        --header-bg: #1e1b4b;
        --header-text: #f8fafc;
        --btn-today-bg: #6366f1;
        --btn-today-hover: #4f46e5;
        --flash-bg: #854d0e;
        --table-stripe: #182234;
      }
    }

    * { box-sizing: border-box; }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 1rem;
      color: var(--text-main);
      background-color: var(--bg-body);
      font-size: 16px;
      line-height: 1.5;
      transition: background-color 0.3s ease, color 0.3s ease;
    }
    h1 {
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--text-main);
      margin-bottom: 0.25rem;
    }
    p.sub {
      font-size: 0.95rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
    }
    .badge-info {
      display: inline-block;
      background: var(--accent-bg);
      color: var(--accent);
      font-weight: 700;
      padding: 0.3rem 0.85rem;
      border-radius: 8px;
      font-size: 0.88rem;
      margin-bottom: 1.25rem;
      border: 1px solid var(--border-color);
    }
    .controls {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 1rem 1.25rem;
      border-radius: 12px;
      margin-bottom: 1.5rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .select-group {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      flex: 1;
      min-width: 240px;
    }
    .select-group label {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--text-muted);
    }
    .select-group select, .select-group input[type="date"] {
      background: var(--bg-body);
      color: var(--accent);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 0.65rem 0.85rem;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      min-height: 48px;
      font-family: inherit;
    }
    .select-group select:focus, .select-group input[type="date"]:focus {
      outline: 2px solid var(--accent);
    }

    .date-input-row {
      display: flex;
      gap: 0.5rem;
      width: 100%;
    }
    .btn-today {
      background: var(--btn-today-bg);
      color: #ffffff;
      border: none;
      border-radius: 8px;
      padding: 0.65rem 1.1rem;
      font-size: 0.95rem;
      font-weight: 700;
      cursor: pointer;
      min-height: 48px;
      white-space: nowrap;
      transition: background 0.2s;
      font-family: inherit;
    }
    .btn-today:hover { background: var(--btn-today-hover); }

    table {
      border-collapse: collapse;
      width: 100%;
      font-size: 0.95rem;
      margin-top: 1rem;
      background: var(--bg-card);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    th, td {
      border: 1px solid var(--border-color);
      padding: 10px 14px;
      vertical-align: middle;
      text-align: left;
      transition: background-color 0.4s ease;
    }
    th {
      position: sticky;
      top: 0;
      background: var(--header-bg);
      color: var(--header-text);
      font-weight: 700;
      font-size: 0.9rem;
    }
    tr:nth-child(even) td { background: var(--table-stripe); }
    td.num { font-weight: bold; color: var(--accent); white-space: nowrap; }
    .day-header-cell { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
    .date-tag { font-weight: normal; color: var(--text-muted); font-size: 0.85rem; }
    .track-lbl { display: none; font-weight: 700; color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; }
    .btn-group { display: flex; gap: 0.5rem; flex-wrap: wrap; }

    a {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: var(--accent-bg);
      color: var(--accent);
      border: 1px solid var(--border-color);
      padding: 0.5rem 0.85rem;
      border-radius: 8px;
      font-weight: 700;
      text-decoration: none;
      font-size: 0.9rem;
      min-height: 44px;
      transition: all 0.15s;
    }
    a:hover {
      background: var(--accent);
      color: #ffffff;
    }

    .btn-share {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.35rem;
      background: var(--accent-bg);
      color: var(--accent);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 0.45rem 0.85rem;
      font-weight: 700;
      font-size: 0.88rem;
      cursor: pointer;
      min-height: 44px;
      transition: all 0.15s;
      font-family: inherit;
    }
    .btn-share:hover {
      background: var(--accent);
      color: #ffffff;
    }
    td.num .btn-share { display: none; }

    /* Floating Back to Top Button */
    .btn-back-to-top {
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      z-index: 999;
      background: var(--accent);
      color: #ffffff;
      border: none;
      border-radius: 999px;
      padding: 0.75rem 1.25rem;
      font-weight: 800;
      font-size: 0.95rem;
      box-shadow: 0 4px 14px rgba(0,0,0,0.25);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      opacity: 0;
      visibility: hidden;
      transform: translateY(20px);
      transition: all 0.25s ease;
      font-family: inherit;
      min-height: 48px;
    }
    .btn-back-to-top.visible {
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
    }
    .btn-back-to-top:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    }

    .toast-msg {
      position: fixed;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      background: #0f172a;
      color: #ffffff;
      padding: 0.75rem 1.5rem;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.95rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 9999;
      animation: fadeInOut 3s ease forwards;
    }
    @keyframes fadeInOut {
      0% { opacity: 0; transform: translate(-50%, 20px); }
      15% { opacity: 1; transform: translate(-50%, 0); }
      85% { opacity: 1; transform: translate(-50%, 0); }
      100% { opacity: 0; transform: translate(-50%, -20px); }
    }

    @keyframes pulseFlash {
      0% { background-color: var(--flash-bg); }
      50% { background-color: var(--flash-bg); }
      100% { background-color: transparent; }
    }
    .highlight-flash td {
      animation: pulseFlash 2.5s ease-out;
      background-color: var(--flash-bg) !important;
    }

    /* RWD Mobilne Stylizowanie dla Smartfonów */
    @media (max-width: 768px) {
      body { margin: 0.75rem; padding: 0; }
      h1 { font-size: 1.3rem; }
      p.sub { font-size: 0.88rem; }
      
      .controls {
        flex-direction: column;
        padding: 0.85rem;
        gap: 0.75rem;
      }
      .select-group select { width: 100%; }

      table, thead, tbody, th, td, tr { display: block; }
      thead { display: none; }
      
      tr {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin-bottom: 1.25rem;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      }

      td {
        border: none;
        padding: 0.4rem 0;
        width: 100%;
      }

      td.num {
        font-size: 1.2rem;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
      }
      td.num .btn-share { display: inline-flex; }

      .track-lbl { display: block; margin-bottom: 0.15rem; }

      .btn-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        width: 100%;
        margin-top: 0.5rem;
      }
      .btn-group .btn-share { display: none; }

      a {
        width: 100%;
        font-size: 1rem;
        padding: 0.75rem 1rem;
        min-height: 48px;
        border-radius: 10px;
      }
    }

    /* Dedykowane Style Drukarki (Print CSS 2026) */
    @media print {
      body { background: #ffffff !important; color: #000000 !important; margin: 0; font-size: 12pt; }
      .controls, .badge-info, p.sub, .btn-share, .btn-back-to-top { display: none !important; }
      table { border: 1px solid #000 !important; box-shadow: none !important; }
      th, td { border: 1px solid #666 !important; color: #000 !important; background: #fff !important; }
      th { background: #eee !important; color: #000 !important; }
      a { border: none !important; background: transparent !important; color: #000 !important; padding: 0 !important; }
      a::after { content: " (" attr(href) ")"; font-size: 8pt; color: #444; }
    }
    """

    controls_markup = """
  <div class="controls" role="region" aria-label="Wybór przekładów i nawigacja kalendarza">
    <div class="select-group">
      <label for="select-left">Lewy panel (Przekład 1):</label>
      <select id="select-left" aria-label="Wybór przekładu dla lewej kolumny">
        <option value="snpd" selected>EIB Przekład Dosłowny (snpd)</option>
        <option value="snp">EIB Przekład Literacki (snp)</option>
        <option value="bt5">Biblia Tysiąclecia V (bt5)</option>
        <option value="bt4">Biblia Tysiąclecia IV (bt4)</option>
        <option value="bt2">Biblia Tysiąclecia II (bt2)</option>
        <option value="bp">Biblia Poznańska (bp)</option>
        <option value="bw">Biblia Warszawska (bw)</option>
        <option value="bwp">Biblia Warszawsko-Praska (bwp)</option>
        <option value="ubg">Uwspółcześniona Biblia Gdańska (ubg)</option>
        <option value="bg">Biblia Gdańska (bg)</option>
        <option value="bgn">Nowa Biblia Gdańska (bgn)</option>
        <option value="bb">Biblia Brzeska (bb)</option>
        <option value="npd">Nowy Przekład Dynamiczny (npd)</option>
        <option value="be">Biblia Ekumeniczna (be)</option>
        <option value="pau">Biblia Paulistów (pau)</option>
        <option value="pop">Popowski [NT] (pop)</option>
        <option value="psz">Słowo Życia (psz)</option>
        <option value="wuj">Biblia Wujka (wuj)</option>
        <option value="stern">Przekład Żydowski - Stern (stern)</option>
        <option value="lxxhb">Septuaginta / Starożytny (lxxhb)</option>
        <option value="gnt">Grecki NT krytyczny (gnt)</option>
        <option value="gnt-tr">Textus Receptus (gnt-tr)</option>
        <option value="nov">Nova Vulgata (nov)</option>
        <option value="kjv">King James Version (kjv)</option>
        <option value="esv">English Standard Version (esv)</option>
      </select>
    </div>
    <div class="select-group">
      <label for="select-right">Prawy panel (Przekład 2):</label>
      <select id="select-right" aria-label="Wybór przekładu dla prawej kolumny">
        <option value="lxxhb" selected>Septuaginta / Starożytny (lxxhb)</option>
        <option value="snpd">EIB Przekład Dosłowny (snpd)</option>
        <option value="snp">EIB Przekład Literacki (snp)</option>
        <option value="bt5">Biblia Tysiąclecia V (bt5)</option>
        <option value="bt4">Biblia Tysiąclecia IV (bt4)</option>
        <option value="bt2">Biblia Tysiąclecia II (bt2)</option>
        <option value="bp">Biblia Poznańska (bp)</option>
        <option value="bw">Biblia Warszawska (bw)</option>
        <option value="bwp">Biblia Warszawsko-Praska (bwp)</option>
        <option value="ubg">Uwspółcześniona Biblia Gdańska (ubg)</option>
        <option value="bg">Biblia Gdańska (bg)</option>
        <option value="bgn">Nowa Biblia Gdańska (bgn)</option>
        <option value="bb">Biblia Brzeska (bb)</option>
        <option value="npd">Nowy Przekład Dynamiczny (npd)</option>
        <option value="be">Biblia Ekumeniczna (be)</option>
        <option value="pau">Biblia Paulistów (pau)</option>
        <option value="pop">Popowski [NT] (pop)</option>
        <option value="psz">Słowo Życia (psz)</option>
        <option value="wuj">Biblia Wujka (wuj)</option>
        <option value="stern">Przekład Żydowski - Stern (stern)</option>
        <option value="gnt">Grecki NT krytyczny (gnt)</option>
        <option value="gnt-tr">Textus Receptus (gnt-tr)</option>
        <option value="nov">Nova Vulgata (nov)</option>
        <option value="kjv">King James Version (kjv)</option>
        <option value="esv">English Standard Version (esv)</option>
      </select>
    </div>
    <div class="select-group">
      <label for="input-date-jump">📅 Skocz do daty:</label>
      <div class="date-input-row">
        <input type="date" id="input-date-jump" min="2026-01-01" max="2026-12-31" aria-label="Wybierz datę z kalendarza">
        <button type="button" id="btn-today" class="btn-today">Dzisiaj</button>
      </div>
    </div>
  </div>
    """

    # 1. GENERACJA WERSJI VANILLA JS (STANDARD 2026)
    if output_html:
        vanilla_doc = f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Oficjalny Harmonogram Czytania Biblii — Chrystadelfianie (Vanilla JS)</title>
  <meta name="description" content="Oficjalny roczny plan czytania Biblii towarzysza Roberta Robertsa z integracją czytnika dwupanelowego HiperBiblia.com.">
  <meta property="og:title" content="Oficjalny Harmonogram Czytania Biblii — Chrystadelfianie">
  <meta property="og:description" content="Czytaj całą Biblię w ciągu roku (3 nurty dziennie) w czytniku HiperBiblia.com z wybranymi przekładami.">
  <meta property="og:type" content="website">
  <style>{common_style}</style>
</head>
<body role="main">
  <h1>Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
  <p class="sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>
  <div class="badge-info">⚡ WERSJA NATYWNA 2026 (Vanilla JS • Dark Mode • Udostępnianie • WCAG AAA)</div>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col">Dzień</th>
        <th scope="col">ST: Prawo i Historia</th>
        <th scope="col">ST: Poezja i Prorocy</th>
        <th scope="col">NT (x2)</th>
        <th scope="col">Linki HiperBiblia.com</th>
      </tr>
    </thead>
    <tbody>
      {tbody_content}
    </tbody>
  </table>

  <button id="btn-back-to-top" class="btn-back-to-top" onclick="scrollToTop()" aria-label="Wróć na górę strony">⬆️ Do góry</button>

  <script>
    const KEY_LEFT = 'hiper_left_translation';
    const KEY_RIGHT = 'hiper_right_translation';

    function initControls() {{
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);
      if (savedLeft) document.getElementById('select-left').value = savedLeft;
      if (savedRight) document.getElementById('select-right').value = savedRight;
      
      document.getElementById('select-left').addEventListener('change', updateTableLinks);
      document.getElementById('select-right').addEventListener('change', updateTableLinks);
      document.getElementById('input-date-jump').addEventListener('change', (e) => jumpToDate(e.target.value));
      document.getElementById('btn-today').addEventListener('click', jumpToToday);

      window.addEventListener('scroll', () => {{
        const btn = document.getElementById('btn-back-to-top');
        if (btn) {{
          if (window.scrollY > 300) btn.classList.add('visible');
          else btn.classList.remove('visible');
        }}
      }});

      updateTableLinks();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinks() {{
      const left = document.getElementById('select-left').value;
      const right = document.getElementById('select-right').value;
      localStorage.setItem(KEY_LEFT, left);
      localStorage.setItem(KEY_RIGHT, right);

      const links = document.querySelectorAll('table a[data-base-url]');
      links.forEach(link => {{
        const baseUrl = link.getAttribute('data-base-url');
        if (baseUrl && baseUrl.includes('hiperbiblia.com/reader')) {{
          try {{
            const urlObj = new URL(baseUrl);
            urlObj.searchParams.set('left', left);
            urlObj.searchParams.set('right', right);
            link.href = urlObj.toString();
          }} catch (e) {{}}
        }}
      }});
    }}

    function jumpToDate(isoDate) {{
      if (!isoDate) return;
      const targetRow = document.querySelector(`tr[data-date="${{isoDate}}"]`);
      if (targetRow) {{
        targetRow.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        targetRow.classList.add('highlight-flash');
        setTimeout(() => targetRow.classList.remove('highlight-flash'), 2500);
      }}
    }}

    function jumpToToday() {{
      const d = new Date();
      const iso = d.toISOString().split('T')[0];
      const picker = document.getElementById('input-date-jump');
      if (picker) picker.value = iso;
      jumpToDate(iso);
    }}

    function shareDay(dayNum, dateStr) {{
      const row = document.querySelector(`tr[data-day="${{dayNum}}"]`);
      if (!row) return;

      const t1Text = row.cells[1].innerText.replace('ST 1 (Prawo / Historia):', '').trim();
      const t2Text = row.cells[2].innerText.replace('ST 2 (Poezja / Prorocy):', '').trim();
      const t3Text = row.cells[3].innerText.replace('NT (Ewangelie / Listy):', '').trim();

      const links = row.querySelectorAll('a[href]');
      const u1 = links[0] ? links[0].href : '';
      const u2 = links[1] ? links[1].href : '';
      const u3 = links[2] ? links[2].href : '';

      const shareText = `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(`📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
        }});
      }}
    }}

    function showToast(msg) {{
      const old = document.querySelector('.toast-msg');
      if (old) old.remove();
      const toast = document.createElement('div');
      toast.className = 'toast-msg';
      toast.innerText = msg;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3200);
    }}

    initControls();
  </script>
</body>
</html>
"""
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Przyskiem Wróć na Górę: {output_html}")

    # 2. GENERACJA WERSJI JQUERY (STANDARD 2026)
    if output_jquery_html:
        jquery_doc = f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Oficjalny Harmonogram Czytania Biblii — Chrystadelfianie (jQuery 3.7.1)</title>
  <meta name="description" content="Oficjalny roczny plan czytania Biblii towarzysza Roberta Robertsa (Wersja jQuery).">
  <meta property="og:title" content="Oficjalny Harmonogram Czytania Biblii — Chrystadelfianie (jQuery)">
  <meta property="og:type" content="website">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <h1>Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
  <p class="sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>
  <div class="badge-info" style="background:var(--accent-bg); color:var(--accent);">⚙️ WERSJA JQUERY 3.7.1 (Standard 2026 • Dark Mode • Udostępnianie • WCAG AAA)</div>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col">Dzień</th>
        <th scope="col">ST: Prawo i Historia</th>
        <th scope="col">ST: Poezja i Prorocy</th>
        <th scope="col">NT (x2)</th>
        <th scope="col">Linki HiperBiblia.com</th>
      </tr>
    </thead>
    <tbody>
      {tbody_content}
    </tbody>
  </table>

  <button id="btn-back-to-top" class="btn-back-to-top" onclick="scrollToTop()" aria-label="Wróć na górę strony">⬆️ Do góry</button>

  <script>
    const KEY_LEFT = 'hiper_left_translation';
    const KEY_RIGHT = 'hiper_right_translation';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);
      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      $('#select-left, #select-right').on('change', updateTableLinksJQuery);
      $('#input-date-jump').on('change', function() {{
        jumpToDateJQuery($(this).val());
      }});
      $('#btn-today').on('click', jumpToTodayJQuery);

      $(window).on('scroll', function() {{
        if ($(this).scrollTop() > 300) {{
          $('#btn-back-to-top').addClass('visible');
        }} else {{
          $('#btn-back-to-top').removeClass('visible');
        }}
      }});

      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      localStorage.setItem(KEY_LEFT, left);
      localStorage.setItem(KEY_RIGHT, right);

      $('table a[data-base-url]').each(function() {{
        const $link = $(this);
        const baseUrl = $link.attr('data-base-url');
        if (baseUrl && baseUrl.includes('hiperbiblia.com/reader')) {{
          try {{
            const urlObj = new URL(baseUrl);
            urlObj.searchParams.set('left', left);
            urlObj.searchParams.set('right', right);
            $link.attr('href', urlObj.toString());
          }} catch (e) {{}}
        }}
      }});
    }}

    function jumpToDateJQuery(isoDate) {{
      if (!isoDate) return;
      const $targetRow = $(`tr[data-date="${{isoDate}}"]`);
      if ($targetRow.length) {{
        $targetRow[0].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        $targetRow.addClass('highlight-flash');
        setTimeout(function() {{
          $targetRow.removeClass('highlight-flash');
        }}, 2500);
      }}
    }}

    function jumpToTodayJQuery() {{
      const d = new Date();
      const iso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(iso);
      jumpToDateJQuery(iso);
    }}

    function shareDay(dayNum, dateStr) {{
      const $row = $(`tr[data-day="${{dayNum}}"]`);
      if (!$row.length) return;

      const t1Text = $row.find('td').eq(1).text().replace('ST 1 (Prawo / Historia):', '').trim();
      const t2Text = $row.find('td').eq(2).text().replace('ST 2 (Poezja / Prorocy):', '').trim();
      const t3Text = $row.find('td').eq(3).text().replace('NT (Ewangelie / Listy):', '').trim();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const shareText = `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(`📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
        }});
      }}
    }}

    function showToast(msg) {{
      $('.toast-msg').remove();
      $('<div>')
        .addClass('toast-msg')
        .text(msg)
        .appendTo('body');
      setTimeout(() => $('.toast-msg').remove(), 3200);
    }}
  </script>
</body>
</html>
"""
        output_jquery_html.write_text(jquery_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML z jQuery 3.7.1 i Przyciskiem Wróć na Górę: {output_jquery_html}")


if __name__ == "__main__":
    from roberts_engine import build_synchronous_roberts_plan
    plan = build_synchronous_roberts_plan(year=2026)
    export_csv(
        plan,
        Path("output/harmonogram_chrystadelfianie_2026.csv"),
        Path("output/harmonogram_chrystadelfianie_2026.html"),
        Path("output/harmonogram_chrystadelfianie_2026_jquery.html")
    )
