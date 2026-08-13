#!/usr/bin/env python3
"""Export Official Christadelphian Bible Reading Plan to PWA Web Application.
Includes Dual Language (PL / EN + HiperBiblia Locale Sync), Floating Back to Top Button, Web Share API + Clipboard Toast for sharing daily reading links.
"""
from __future__ import annotations

import json
from pathlib import Path

PWA_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Oficjalny Plan Czytania Biblii — Chrystadelfianie</title>
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#0f172a">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-primary: #0f172a;
      --bg-card: #1e293b;
      --bg-card-today: #1e1b4b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --border: #334155;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      padding: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
      font-size: 16px;
      line-height: 1.5;
    }}

    header {{
      margin-bottom: 2rem;
      text-align: center;
    }}

    .top-bar-pwa {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 0.5rem;
    }}

    h1 {{
      font-size: 1.8rem;
      font-weight: 700;
      background: linear-gradient(to right, #38bdf8, #818cf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin: 0;
    }}

    .lang-switcher {{
      display: inline-flex;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.25rem;
      gap: 0.25rem;
    }}
    .lang-btn {{
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
    }}
    .lang-btn.active {{
      background: var(--accent);
      color: #0f172a;
    }}

    .subtitle {{
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-bottom: 1.25rem;
      text-align: center;
    }}

    .translation-controls {{
      display: flex;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid var(--border);
      padding: 1rem 1.25rem;
      border-radius: 12px;
      margin: 0 auto 1.5rem auto;
      max-width: 850px;
    }}

    .select-group {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      flex: 1;
      min-width: 240px;
      text-align: left;
    }}

    .select-group label {{
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--text-muted);
    }}

    .select-group select, .select-group input[type="date"] {{
      background: #0f172a;
      color: var(--accent);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.6rem 0.85rem;
      font-family: inherit;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      min-height: 48px;
    }}

    .select-group select:focus, .select-group input[type="date"]:focus {{
      outline: 2px solid var(--accent);
    }}

    .progress-container {{
      background-color: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem;
      margin-bottom: 2rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}

    .progress-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.95rem;
      font-weight: 600;
    }}

    .progress-bar-bg {{
      background-color: var(--border);
      height: 12px;
      border-radius: 999px;
      overflow: hidden;
    }}

    .progress-bar-fill {{
      background: linear-gradient(to right, #10b981, #38bdf8);
      height: 100%;
      width: 0%;
      transition: width 0.3s ease;
    }}

    .controls {{
      display: flex;
      gap: 1rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      align-items: center;
    }}

    .search-input {{
      flex: 1;
      min-width: 240px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      color: var(--text-main);
      font-family: inherit;
      font-size: 1rem;
      min-height: 48px;
    }}

    .search-input:focus {{ outline: 2px solid var(--accent); }}

    .today-btn {{
      background: #4f46e5;
      color: white;
      border: none;
      padding: 0.75rem 1.25rem;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
      font-family: inherit;
      font-size: 1rem;
      min-height: 48px;
      transition: background 0.2s;
    }}
    .today-btn:hover {{ background: #4338ca; }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.25rem;
    }}

    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      transition: border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
      position: relative;
    }}

    .card.today {{
      background: var(--bg-card-today);
      border: 2px solid #818cf8;
      box-shadow: 0 0 20px rgba(129, 140, 248, 0.25);
    }}

    .card.done {{
      border-color: #059669;
      background: rgba(6, 78, 59, 0.4);
    }}

    @keyframes pulseFlashPwa {{
      0% {{ border-color: #eab308; box-shadow: 0 0 25px rgba(234, 179, 8, 0.6); }}
      50% {{ border-color: #eab308; box-shadow: 0 0 35px rgba(234, 179, 8, 0.8); }}
      100% {{ border-color: var(--border); box-shadow: none; }}
    }}
    .card.highlight-flash {{
      animation: pulseFlashPwa 2.5s ease-out;
      border: 2px solid #eab308 !important;
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .card-top-right {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .day-badge {{
      font-weight: 800;
      font-size: 1.2rem;
      color: var(--accent);
    }}

    .today-tag {{
      background: #818cf8;
      color: #0f172a;
      font-weight: 800;
      font-size: 0.8rem;
      padding: 0.2rem 0.6rem;
      border-radius: 999px;
      margin-left: 0.5rem;
    }}

    .date-label {{
      font-size: 0.9rem;
      color: var(--text-muted);
    }}

    .checkbox-btn {{
      appearance: none;
      width: 28px;
      height: 28px;
      border: 2px solid var(--border);
      border-radius: 8px;
      cursor: pointer;
      display: grid;
      place-content: center;
      transition: all 0.2s;
    }}

    .checkbox-btn:checked {{
      background-color: #10b981;
      border-color: #10b981;
    }}

    .checkbox-btn:checked::before {{
      content: "✓";
      color: white;
      font-weight: bold;
      font-size: 18px;
    }}

    .btn-pwa-share {{
      background: rgba(255, 255, 255, 0.08);
      color: var(--accent);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.35rem 0.65rem;
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      transition: all 0.15s;
      font-family: inherit;
    }}
    .btn-pwa-share:hover {{
      background: var(--accent);
      color: #0f172a;
    }}

    /* Floating Back to Top Button */
    .btn-back-to-top {{
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      z-index: 999;
      background: var(--accent);
      color: #0f172a;
      border: none;
      border-radius: 999px;
      padding: 0.75rem 1.25rem;
      font-weight: 800;
      font-size: 0.95rem;
      box-shadow: 0 4px 14px rgba(0,0,0,0.4);
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
    }}
    .btn-back-to-top.visible {{
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
    }}
    .btn-back-to-top:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0,0,0,0.5);
    }}

    .toast-msg {{
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
    }}
    @keyframes fadeInOut {{
      0% {{ opacity: 0; transform: translate(-50%, 20px); }}
      15% {{ opacity: 1; transform: translate(-50%, 0); }}
      85% {{ opacity: 1; transform: translate(-50%, 0); }}
      100% {{ opacity: 0; transform: translate(-50%, -20px); }}
    }}

    .track {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      font-size: 0.95rem;
    }}

    .track-title {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 700;
      color: var(--text-muted);
    }}

    .hiper-link {{
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 0.65rem 1rem;
      border-radius: 10px;
      text-decoration: none;
      font-size: 1rem;
      font-weight: 700;
      min-height: 48px;
      transition: all 0.15s;
    }}

    .hiper-link:hover {{
      border-color: var(--accent);
      background: rgba(56, 189, 248, 0.2);
      color: var(--accent);
    }}

    /* Smartfon RWD Style */
    @media (max-width: 768px) {{
      body {{ padding: 0.75rem; }}
      h1 {{ font-size: 1.4rem; }}
      .subtitle {{ font-size: 0.9rem; }}

      .translation-controls {{
        flex-direction: column;
        padding: 0.85rem;
        gap: 0.75rem;
      }}
      .select-group select, .select-group input[type="date"] {{ width: 100%; }}

      .controls {{
        flex-direction: column;
        align-items: stretch;
      }}
      .today-btn {{ width: 100%; text-align: center; }}
      .search-input {{ width: 100%; }}
      
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="top-bar-pwa">
      <h1 id="pwa-h1">Oficjalny Plan Czytania Biblii — Chrystadelfianie</h1>
      <div class="lang-switcher">
        <button type="button" class="lang-btn active" id="btn-pwa-lang-pl" onclick="setPwaLanguage('pl')">🇵🇱 PL</button>
        <button type="button" class="lang-btn" id="btn-pwa-lang-en" onclick="setPwaLanguage('en')">🇬🇧 EN</button>
      </div>
    </div>
    <p class="subtitle" id="pwa-sub">Wyrocznia czytań z integracją czytnika HiperBiblia.com (3 nurty dziennie)</p>

    <div class="translation-controls">
      <div class="select-group">
        <label for="select-left" id="pwa-lbl-left">Lewy panel (Przekład 1):</label>
        <select id="select-left" onchange="onTranslationChange()">
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
        <label for="select-right" id="pwa-lbl-right">Prawy panel (Przekład 2):</label>
        <select id="select-right" onchange="onTranslationChange()">
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
        <label for="pwa-date-jump" id="pwa-lbl-date">📅 Skocz do daty:</label>
        <input type="date" id="pwa-date-jump" min="2026-01-01" max="2026-12-31" onchange="jumpToDatePwa(this.value)">
      </div>
    </div>
  </header>

  <div class="progress-container">
    <div class="progress-header">
      <span id="pwa-lbl-progress-title">Twój roczny postęp w czytaniu</span>
      <span id="progress-text">0 / 365 dni (0%)</span>
    </div>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill" id="progress-fill"></div>
    </div>
  </div>

  <div class="controls">
    <button class="today-btn" id="pwa-btn-today" onclick="scrollToToday()">📅 Przejdź do dzisiejszego dnia</button>
    <input type="text" id="search" class="search-input" placeholder="Szukaj po dacie lub księdze...">
  </div>

  <div class="grid" id="plan-grid"></div>

  <button id="btn-back-to-top-pwa" class="btn-back-to-top" onclick="scrollToTopPwa()" aria-label="Wróć na górę strony">⬆️ Do góry</button>

  <script>
    const PLAN_DATA = {plan_json};
    const STORAGE_KEY = 'roberts_plan_completed_days';
    const KEY_LEFT = 'hiper_left_translation';
    const KEY_RIGHT = 'hiper_right_translation';
    const KEY_LANG = 'hiper_lang';
    let currentLang = 'pl';

    function initTranslationControls() {{
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT);
      const savedRight = localStorage.getItem(KEY_RIGHT);
      if (savedLeft) document.getElementById('select-left').value = savedLeft;
      if (savedRight) document.getElementById('select-right').value = savedRight;

      window.addEventListener('scroll', () => {{
        const btn = document.getElementById('btn-back-to-top-pwa');
        if (btn) {{
          if (window.scrollY > 300) btn.classList.add('visible');
          else btn.classList.remove('visible');
        }}
      }});

      setPwaLanguage(savedLang, false);
    }}

    function setPwaLanguage(lang, userTriggered = true) {{
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      document.getElementById('btn-pwa-lang-pl').classList.toggle('active', lang === 'pl');
      document.getElementById('btn-pwa-lang-en').classList.toggle('active', lang === 'en');
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

      document.getElementById('pwa-h1').innerText = isEn ? 'Official Bible Reading Companion — Christadelphians' : 'Oficjalny Plan Czytania Biblii — Chrystadelfianie';
      document.getElementById('pwa-sub').innerText = isEn ? 'Oracle readings integrated with HiperBiblia.com dual-panel reader (3 daily tracks)' : 'Wyrocznia czytań z integracją czytnika HiperBiblia.com (3 nurty dziennie)';
      document.getElementById('pwa-lbl-left').innerText = isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):';
      document.getElementById('pwa-lbl-right').innerText = isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):';
      document.getElementById('pwa-lbl-date').innerText = isEn ? '📅 Jump to date:' : '📅 Skocz do daty:';
      document.getElementById('pwa-lbl-progress-title').innerText = isEn ? 'Your Annual Reading Progress' : 'Twój roczny postęp w czytaniu';
      document.getElementById('pwa-btn-today').innerText = isEn ? '📅 Jump to Today' : '📅 Przejdź do dzisiejszego dnia';
      document.getElementById('search').placeholder = isEn ? 'Search by date or book (e.g. 12.08, Genesis, Psalms, Matthew)...' : 'Szukaj po dacie lub księdze (np. 12.08, Mojżesza, Psalm, Mateusza)...';
      document.getElementById('btn-back-to-top-pwa').innerText = isEn ? '⬆️ Back to Top' : '⬆️ Do góry';

      render(document.getElementById('search').value);
    }}

    function scrollToTopPwa() {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function onTranslationChange() {{
      const left = document.getElementById('select-left').value;
      const right = document.getElementById('select-right').value;
      localStorage.setItem(KEY_LEFT, left);
      localStorage.setItem(KEY_RIGHT, right);
      render(document.getElementById('search').value);
    }}

    function buildHiperUrl(baseUrl, left, right) {{
      if (!baseUrl || !baseUrl.includes('hiperbiblia.com/reader')) return baseUrl;
      try {{
        const urlObj = new URL(baseUrl);
        urlObj.searchParams.set('left', left);
        urlObj.searchParams.set('right', right);
        urlObj.searchParams.set('locale', currentLang || 'pl');
        return urlObj.toString();
      }} catch (e) {{
        return baseUrl;
      }}
    }}

    function getTodayIso() {{
      const d = new Date();
      return d.toISOString().split('T')[0];
    }}

    function getCompleted() {{
      try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }} catch {{ return []; }}
    }}

    function toggleDay(dayNum) {{
      let completed = getCompleted();
      if (completed.includes(dayNum)) {{
        completed = completed.filter(d => d !== dayNum);
      }} else {{
        completed.push(dayNum);
      }}
      localStorage.setItem(STORAGE_KEY, JSON.stringify(completed));
      render(document.getElementById('search').value);
    }}

    function updateProgress(completedCount, total) {{
      const isEn = currentLang === 'en';
      const percent = Math.round((completedCount / total) * 100);
      document.getElementById('progress-text').innerText = `${{completedCount}} / ${{total}} ${{isEn ? 'days' : 'dni'}} (${{percent}}%)`;
      document.getElementById('progress-fill').style.width = `${{percent}}%`;
    }}

    function jumpToDatePwa(isoDate) {{
      if (!isoDate) return;
      const card = document.querySelector(`[data-date="${{isoDate}}"]`);
      if (card) {{
        card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        card.classList.add('highlight-flash');
        setTimeout(() => card.classList.remove('highlight-flash'), 2500);
      }}
    }}

    function scrollToToday() {{
      const todayIso = getTodayIso();
      const picker = document.getElementById('pwa-date-jump');
      if (picker) picker.value = todayIso;
      jumpToDatePwa(todayIso);
    }}

    function shareDayPwa(dayNum, dateStr, t1Text, t2Text, t3Text, u1, u2, u3) {{
      const isEn = currentLang === 'en';
      const titleStr = isEn ? `📖 Bible Reading — Day ${{dayNum}} (${{dateStr}}):` : `📖 Czytanie Biblii — Dzień ${{dayNum}} (${{dateStr}}):`;
      const shareText = `${{titleStr}}\n\n1. ${{t1Text}}:\n${{u1}}\n\n2. ${{t2Text}}:\n${{u2}}\n\n3. ${{t3Text}}:\n${{u3}}`;

      if (navigator.share) {{
        navigator.share({{
          title: isEn ? `Bible Reading — Day ${{dayNum}}` : `Czytanie Biblii — Dzień ${{dayNum}}`,
          text: shareText
        }}).catch(() => {{}});
      }} else {{
        navigator.clipboard.writeText(shareText).then(() => {{
          showToastPwa(isEn ? `📋 Copied Day ${{dayNum}} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${{dayNum}} do schowka!`);
        }});
      }}
    }}

    function showToastPwa(msg) {{
      const old = document.querySelector('.toast-msg');
      if (old) old.remove();
      const toast = document.createElement('div');
      toast.className = 'toast-msg';
      toast.innerText = msg;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3200);
    }}

    function render(filter = '') {{
      const grid = document.getElementById('plan-grid');
      grid.innerHTML = '';
      const completed = getCompleted();
      const todayIso = getTodayIso();
      const isEn = currentLang === 'en';

      const leftTrans = document.getElementById('select-left').value;
      const rightTrans = document.getElementById('select-right').value;

      updateProgress(completed.length, PLAN_DATA.length);
      const query = filter.toLowerCase().trim();

      PLAN_DATA.forEach(day => {{
        const isDone = completed.includes(day.day);
        const isToday = day.date === todayIso;

        const t1 = isEn ? (day.t1_ref_en || day.t1_ref) : day.t1_ref;
        const t2 = isEn ? (day.t2_ref_en || day.t2_ref) : day.t2_ref;
        const t3 = isEn ? (day.t3_ref_en || day.t3_ref) : day.t3_ref;

        const matchText = `${{day.day}} ${{day.date || ''}} ${{day.month_day || ''}} ${{t1}} ${{t2}} ${{t3}}`.toLowerCase();
        if (query && !matchText.includes(query)) return;

        const card = document.createElement('div');
        card.className = `card ${{isToday ? 'today' : ''}} ${{isDone ? 'done' : ''}}`;
        card.setAttribute('data-date', day.date);

        const raw1 = day.links[0] || {{ url: '#', label: '', label_en: '' }};
        const raw2 = day.links[1] || {{ url: '#', label: '', label_en: '' }};
        const raw3 = day.links[2] || {{ url: '#', label: '', label_en: '' }};

        const u1 = buildHiperUrl(raw1.url, leftTrans, rightTrans);
        const u2 = buildHiperUrl(raw2.url, leftTrans, rightTrans);
        const u3 = buildHiperUrl(raw3.url, leftTrans, rightTrans);

        const lbl1 = isEn ? (raw1.label_en || raw1.label) : raw1.label;
        const lbl2 = isEn ? (raw2.label_en || raw2.label) : raw2.label;
        const lbl3 = isEn ? (raw3.label_en || raw3.label) : raw3.label;

        const t1Esc = t1.replace(/'/g, "\\'");
        const t2Esc = t2.replace(/'/g, "\\'");
        const t3Esc = t3.replace(/'/g, "\\'");

        card.innerHTML = `
          <div class="card-top">
            <div>
              <span class="day-badge">${{isEn ? 'Day' : 'Dzień'}} ${{day.day}}</span>
              <span class="date-label"> • ${{day.date}}</span>
              ${{isToday ? `<span class="today-tag">${{isEn ? 'Today' : 'Dzisiaj'}}</span>` : ''}}
            </div>
            <div class="card-top-right">
              <button type="button" class="btn-pwa-share" onclick="shareDayPwa(${{day.day}}, '${{day.date}}', '${{t1Esc}}', '${{t2Esc}}', '${{t3Esc}}', '${{u1}}', '${{u2}}', '${{u3}}')">${{isEn ? '📤 Share' : '📤 Udostępnij'}}</button>
              <input type="checkbox" class="checkbox-btn" ${{isDone ? 'checked' : ''}} onchange="toggleDay(${{day.day}})">
            </div>
          </div>
          <div class="track">
            <span class="track-title">${{isEn ? 'OT: Law & History' : 'ST: Prawo i Historia'}}</span>
            <div><a class="hiper-link" href="${{u1}}" target="_blank" rel="noopener">${{t1}} (${{lbl1}}) ↗</a></div>
          </div>
          <div class="track">
            <span class="track-title">${{isEn ? 'OT: Psalms & Prophets' : 'ST: Poezja i Prorocy'}}</span>
            <div><a class="hiper-link" href="${{u2}}" target="_blank" rel="noopener">${{t2}} (${{lbl2}}) ↗</a></div>
          </div>
          <div class="track">
            <span class="track-title">${{isEn ? 'New Testament (x2)' : 'Nowy Testament (x2)'}}</span>
            <div><a class="hiper-link" href="${{u3}}" target="_blank" rel="noopener">${{t3}} (${{lbl3}}) ↗</a></div>
          </div>
        `;
        grid.appendChild(card);
      }});
    }}

    document.getElementById('search').addEventListener('input', (e) => render(e.target.value));
    initTranslationControls();
    render();
    setTimeout(scrollToToday, 400);
  </script>
</body>
</html>
"""

MANIFEST_JSON = """{
  "name": "Official Christadelphian Bible Reading Plan",
  "short_name": "Bible Companion",
  "start_url": "index.html",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#1e293b",
  "icons": [
    {
      "src": "https://hiperbiblia.com/favicon.ico",
      "sizes": "64x64",
      "type": "image/x-icon"
    }
  ]
}
"""


def export_pwa(plan: list[dict], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    html_content = PWA_HTML_TEMPLATE.replace("{plan_json}", json.dumps(plan, ensure_ascii=False))
    (output_dir / "index.html").write_text(html_content, encoding="utf-8")
    (output_dir / "manifest.json").write_text(MANIFEST_JSON, encoding="utf-8")
    print(f"Wygenerowano oficjalne PWA Wyroczni (PL / EN) z Locale Sync w: {output_dir}")


if __name__ == "__main__":
    from roberts_engine import build_synchronous_roberts_plan
    plan = build_synchronous_roberts_plan(year=2026)
    export_pwa(plan, Path("web"))
