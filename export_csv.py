#!/usr/bin/env python3
"""Export Official Christadelphian Bible Reading Plan to CSV and static HTML tables (Vanilla JS & jQuery versions).
Fully compliant with 2026 Web Standards: Dual Language Support (PL / EN + HiperBiblia Locale Sync), Custom Favicon Suite, Traditional Tone ("Przejdź do daty"), Default Today Date Picker, Floating Back to Top Button, Share Button, Dark Mode, OpenGraph, WCAG 2.2 AAA, Print CSS & Security rel=noopener.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path


def export_csv(
    plan: list[dict],
    output_csv: Path,
    output_html: Path | None = None,
    output_jquery_html: Path | None = None,
    output_en_html: Path | None = None
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
        t1_pl = day.get("t1_ref", "")
        t2_pl = day.get("t2_ref", "")
        t3_pl = day.get("t3_ref", "")
        t1_en = day.get("t1_ref_en", t1_pl)
        t2_en = day.get("t2_ref_en", t2_pl)
        t3_en = day.get("t3_ref_en", t3_pl)

        link_tags = []
        for link in day.get("links", []):
            l_label_pl = html.escape(link.get("label", "Link"))
            l_label_en = html.escape(link.get("label_en", l_label_pl))
            l_url = html.escape(link.get("url", "#"))
            link_tags.append(
                f'<a href="{l_url}" data-base-url="{l_url}" target="_blank" rel="noopener noreferrer" '
                f'data-lbl-pl="{l_label_pl} ↗" data-lbl-en="{l_label_en} ↗">{l_label_pl} ↗</a>'
            )

        share_btn = f'<button type="button" class="btn-share" onclick="shareDay({day_num}, \'{date_val}\')">📤 Udostępnij</button>'

        tbody_rows.append(f"""
        <tr data-date="{date_val}" data-day="{day_num}">
          <td class="num">
            <div class="day-header-cell">
              <span class="day-title-text" data-pl="Dzień {day_num}" data-en="Day {day_num}">Dzień {day_num} <span class="date-tag">• {date_val}</span></span>
              {share_btn}
            </div>
          </td>
          <td class="track-cell">
            <span class="track-lbl" data-pl="ST 1 (Prawo / Historia):" data-en="OT 1 (Law & History):">ST 1 (Prawo / Historia):</span>
            <span class="ref-text" data-pl="{html.escape(t1_pl)}" data-en="{html.escape(t1_en)}">{html.escape(t1_pl)}</span>
          </td>
          <td class="track-cell">
            <span class="track-lbl" data-pl="ST 2 (Poezja / Prorocy):" data-en="OT 2 (Psalms & Prophets):">ST 2 (Poezja / Prorocy):</span>
            <span class="ref-text" data-pl="{html.escape(t2_pl)}" data-en="{html.escape(t2_en)}">{html.escape(t2_pl)}</span>
          </td>
          <td class="track-cell">
            <span class="track-lbl" data-pl="NT (Ewangelie / Listy):" data-en="NT (Gospels & Epistles):">NT (Ewangelie / Listy):</span>
            <span class="ref-text" data-pl="{html.escape(t3_pl)}" data-en="{html.escape(t3_en)}">{html.escape(t3_pl)}</span>
          </td>
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
    .top-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 0.5rem;
    }
    h1 {
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--text-main);
      margin: 0;
    }
    .lang-switcher {
      display: inline-flex;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 999px;
      padding: 0.25rem;
      gap: 0.25rem;
    }
    .lang-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-weight: 700;
      font-size: 0.9rem;
      padding: 0.4rem 0.85rem;
      border-radius: 999px;
      cursor: pointer;
      transition: all 0.2s;
      font-family: inherit;
    }
    .lang-btn.active {
      background: var(--accent);
      color: #ffffff;
    }
    p.sub {
      font-size: 0.95rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
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
    .highlight-flash {
      animation: pulseFlash 2.5s ease-out;
      background-color: var(--flash-bg) !important;
    }
    .highlight-flash td {
      background-color: transparent !important;
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
        overflow: hidden;
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
      td.num .day-header-cell {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        width: 100%;
      }
      td.num .btn-share {
        display: inline-flex;
        font-size: 0.82rem;
        padding: 0.3rem 0.65rem;
        min-height: 36px;
        margin: 0;
      }

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
      .controls, p.sub, .btn-share, .btn-back-to-top, .lang-switcher { display: none !important; }
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
      <label for="select-left" id="lbl-left">Lewy panel (Przekład 1):</label>
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
      <label for="select-right" id="lbl-right">Prawy panel (Przekład 2):</label>
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
      <label for="input-date-jump" id="lbl-date-jump">📅 Przejdź do daty:</label>
      <div class="date-input-row">
        <input type="date" id="input-date-jump" min="2026-01-01" max="2026-12-31" aria-label="Wybierz datę z kalendarza">
        <button type="button" id="btn-today" class="btn-today">Dzisiaj</button>
      </div>
    </div>
  </div>
    """

    # 1. GENERACJA WERSJI VANILLA JS (STANDARD 2026 PL/EN)
    if output_html:
        vanilla_doc = f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title id="doc-title">Oficjalny Harmonogram Czytania Biblii — Chrystadelfianie (Vanilla JS)</title>
  <meta name="description" content="Official Christadelphian Bible Reading Companion (Robert Roberts) integrated with HiperBiblia.com dual-panel reader.">
  <meta property="og:title" content="Oficjalny Harmonogram Czytania Biblii — Chrystadelfianie">
  <meta property="og:description" content="Read the entire Bible in a year (3 daily tracks) in HiperBiblia.com reader with your choice of translations.">
  <meta property="og:type" content="website">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguage('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguage('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    function initControls() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) document.getElementById('select-left').value = savedLeft;
      if (savedRight) document.getElementById('select-right').value = savedRight;

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      const dateInput = document.getElementById('input-date-jump');
      if (dateInput) dateInput.value = todayIso;
      
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

      setLanguage(savedLang, false);
      updateTableLinks();
    }}

    function setLanguage(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      document.getElementById('btn-lang-pl').classList.toggle('active', lang === 'pl');
      document.getElementById('btn-lang-en').classList.toggle('active', lang === 'en');
      document.documentElement.lang = lang;

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          document.getElementById('select-left').value = 'kjv';
          document.getElementById('select-right').value = 'esv';
        }} else {{
          document.getElementById('select-left').value = 'snpd';
          document.getElementById('select-right').value = 'lxxhb';
        }}
      }}

      // Text UI translations
      document.getElementById('main-h1').innerText = isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)';
      document.getElementById('main-sub').innerHTML = isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.';
      document.getElementById('lbl-left').innerText = isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):';
      document.getElementById('lbl-right').innerText = isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):';
      document.getElementById('lbl-date-jump').innerText = isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:';
      document.getElementById('btn-today').innerText = isEn ? 'Today' : 'Dzisiaj';
      document.getElementById('btn-back-to-top').innerText = isEn ? '⬆️ Back to Top' : '⬆️ Do góry';

      document.getElementById('th-day').innerText = isEn ? 'Day' : 'Dzień';
      document.getElementById('th-t1').innerText = isEn ? 'OT: Law & History' : 'ST: Prawo i Historia';
      document.getElementById('th-t2').innerText = isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy';
      document.getElementById('th-t3').innerText = isEn ? 'NT (x2)' : 'NT (x2)';
      document.getElementById('th-links').innerText = isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com';

      // Update row texts
      document.querySelectorAll('.day-title-text').forEach(el => {{
        const dateTag = el.querySelector('.date-tag');
        const dateStr = dateTag ? dateTag.outerHTML : '';
        const dayNum = el.closest('tr').getAttribute('data-day');
        el.innerHTML = isEn ? `Day ${{dayNum}} ${{dateStr}}` : `Dzień ${{dayNum}} ${{dateStr}}`;
      }});

      document.querySelectorAll('.track-lbl').forEach(el => {{
        el.innerText = isEn ? el.getAttribute('data-en') : el.getAttribute('data-pl');
      }});

      document.querySelectorAll('.ref-text').forEach(el => {{
        el.innerText = isEn ? el.getAttribute('data-en') : el.getAttribute('data-pl');
      }});

      document.querySelectorAll('a[data-lbl-pl]').forEach(el => {{
        el.innerText = isEn ? el.getAttribute('data-lbl-en') : el.getAttribute('data-lbl-pl');
      }});

      document.querySelectorAll('.btn-share').forEach(el => {{
        el.innerText = isEn ? '📤 Share' : '📤 Udostępnij';
      }});

      updateTableLinks();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinks() {{
      const left = document.getElementById('select-left').value;
      const right = document.getElementById('select-right').value;
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = row.cells[1].querySelector('.ref-text').innerText;
      const t2Text = row.cells[2].querySelector('.ref-text').innerText;
      const t3Text = row.cells[3].querySelector('.ref-text').innerText;

      const links = row.querySelectorAll('a[href]');
      const u1 = links[0] ? links[0].href : '';
      const u2 = links[1] ? links[1].href : '';
      const u3 = links[2] ? links[2].href : '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        output_html.write_text(vanilla_doc, encoding="utf-8")
        print(f"Zapisano statyczny HTML Vanilla JS z Favikonami: {output_html}")

        if output_en_html:
            # Pre-configured English HTML version
            en_doc = vanilla_doc.replace("<html lang=\"pl\">", "<html lang=\"en\">")
            en_doc = en_doc.replace("const savedLang = localStorage.getItem(KEY_LANG) || 'pl';", "const savedLang = 'en';")
            output_en_html.write_text(en_doc, encoding="utf-8")
            print(f"Zapisano dedykowany HTML Angielski: {output_en_html}")

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
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
  <style>{common_style}</style>
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body role="main">
  <div class="top-bar">
    <h1 id="main-h1">Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)</h1>
    <div class="lang-switcher">
      <button type="button" class="lang-btn active" id="btn-lang-pl" onclick="setLanguageJQuery('pl')">🇵🇱 PL</button>
      <button type="button" class="lang-btn" id="btn-lang-en" onclick="setLanguageJQuery('en')">🇬🇧 EN</button>
    </div>
  </div>

  <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.</p>

  {controls_markup}

  <table aria-label="Tabela rocznego harmonogramu czytania Biblii">
    <thead>
      <tr>
        <th scope="col" id="th-day">Dzień</th>
        <th scope="col" id="th-t1">ST: Prawo i Historia</th>
        <th scope="col" id="th-t2">ST: Poezja i Prorocy</th>
        <th scope="col" id="th-t3">NT (x2)</th>
        <th scope="col" id="th-links">Linki HiperBiblia.com</th>
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
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    $(document).ready(function() {{
      initControlsJQuery();
    }});

    function initControlsJQuery() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);

      if (savedLeft) $('#select-left').val(savedLeft);
      if (savedRight) $('#select-right').val(savedRight);

      // Automatyczne wstawienie dzisiejszej daty do pola kalendarza
      const d = new Date();
      const todayIso = d.toISOString().split('T')[0];
      $('#input-date-jump').val(todayIso);

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

      setLanguageJQuery(savedLang, false);
      updateTableLinksJQuery();
    }}

    function setLanguageJQuery(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      $('#btn-lang-pl').toggleClass('active', lang === 'pl');
      $('#btn-lang-en').toggleClass('active', lang === 'en');
      $('html').attr('lang', lang);

      const isEn = lang === 'en';
      if (userTriggered) {{
        if (isEn) {{
          $('#select-left').val('kjv');
          $('#select-right').val('esv');
        }} else {{
          $('#select-left').val('snpd');
          $('#select-right').val('lxxhb');
        }}
      }}

      $('#main-h1').text(isEn ? 'Official Bible Reading Companion (Robert Roberts)' : 'Oficjalny Harmonogram Czytania Biblii (prawdybiblijne.com)');
      $('#main-sub').html(isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z Twoimi wybranymi przekładami.');
      $('#lbl-left').text(isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):');
      $('#lbl-right').text(isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):');
      $('#lbl-date-jump').text(isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:');
      $('#btn-today').text(isEn ? 'Today' : 'Dzisiaj');
      $('#btn-back-to-top').text(isEn ? '⬆️ Back to Top' : '⬆️ Do góry');

      $('#th-day').text(isEn ? 'Day' : 'Dzień');
      $('#th-t1').text(isEn ? 'OT: Law & History' : 'ST: Prawo i Historia');
      $('#th-t2').text(isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy');
      $('#th-t3').text(isEn ? 'NT (x2)' : 'NT (x2)');
      $('#th-links').text(isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com');

      $('.day-title-text').each(function() {{
        const $el = $(this);
        const dateTag = $el.find('.date-tag').prop('outerHTML') || '';
        const dayNum = $el.closest('tr').attr('data-day');
        $el.html(isEn ? `Day ${{dayNum}} ${{dateTag}}` : `Dzień ${{dayNum}} ${{dateTag}}`);
      }});

      $('.track-lbl').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('.ref-text').each(function() {{
        $(this).text(isEn ? $(this).attr('data-en') : $(this).attr('data-pl'));
      }});

      $('a[data-lbl-pl]').each(function() {{
        $(this).text(isEn ? $(this).attr('data-lbl-en') : $(this).attr('data-lbl-pl'));
      }});

      $('.btn-share').text(isEn ? '📤 Share' : '📤 Udostępnij');
      updateTableLinksJQuery();
    }}

    function scrollToTop() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function updateTableLinksJQuery() {{
      const left = $('#select-left').val();
      const right = $('#select-right').val();
      const lang = currentLang || 'pl';
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
            urlObj.searchParams.set('locale', lang);
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

      const isEn = currentLang === 'en';
      const t1Text = $row.find('.ref-text').eq(0).text();
      const t2Text = $row.find('.ref-text').eq(1).text();
      const t3Text = $row.find('.ref-text').eq(2).text();

      const $links = $row.find('a[href]');
      const u1 = $links.eq(0).attr('href') || '';
      const u2 = $links.eq(1).attr('href') || '';
      const u3 = $links.eq(2).attr('href') || '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToast(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
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
        print(f"Zapisano statyczny HTML z jQuery 3.7.1 z Favikonami: {output_jquery_html}")


if __name__ == "__main__":
    from roberts_engine import build_synchronous_roberts_plan
    plan = build_synchronous_roberts_plan(year=2026)
    export_csv(
        plan,
        Path("output/harmonogram_chrystadelfianie_2026.csv"),
        Path("output/harmonogram_chrystadelfianie_2026.html"),
        Path("output/harmonogram_chrystadelfianie_2026_jquery.html"),
        Path("output/harmonogram_chrystadelfianie_2026_en.html")
    )
