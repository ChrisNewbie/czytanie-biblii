# PowerShell script to transform and generate index_v2.html from the ground truth data in index.html
$ErrorActionPreference = "Stop"

$indexPath = "D:\projects\Biblia-czytanie\index.html"
$v2Path = "D:\projects\Biblia-czytanie\index_v2.html"

Write-Host "Wczytywanie $indexPath..."
$content = [System.IO.File]::ReadAllText($indexPath, [System.Text.Encoding]::UTF8)

# Extract tbody content
$tbodyMatch = [regex]::Match($content, '(?s)<tbody[^>]*>(.*?)</tbody>')
if (-not $tbodyMatch.Success) {
    throw "Nie znaleziono tagu <tbody> w pliku index.html"
}

$rawTbody = $tbodyMatch.Groups[1].Value

# Clean and enhance tbody rows:
# 1. Normalize <tr> and <td> roles
# 2. Clean duplicate share buttons inside btn-group while keeping all 3 reading links
# 3. Ensure EVERY day-header-cell has the accessible, unified share button
# 4. Set default right translation to ubg
# 5. Replace "Poezja" with "Psalmy" in Polish track labels
$enhancedTbody = $rawTbody `
    -replace '<tr\s+data-date="([^"]+)"\s+data-day="([^"]+)">', '<tr role="row" data-date="$1" data-day="$2">' `
    -replace '<td class="num">', '<td role="cell" class="num">' `
    -replace '<td class="track-cell">', '<td role="cell" class="track-cell">' `
    -replace '<td class="links-cell">', '<td role="cell" class="links-cell">' `
    -replace '<div class="btn-group">', '<div class="btn-group" role="group" aria-label="Odnośniki do czytnika HiperBiblia">' `
    -replace '(?s)(<div class="btn-group"[^>]*>.*?)\s*<button type="button" class="btn-share"[^>]*>.*?</button>\s*(</div>)', '$1$2' `
    -replace 'right=lxxhb', 'right=ubg' `
    -replace 'Poezja / Prorocy', 'Psalmy / Prorocy' `
    -replace 'Poezja i Prorocy', 'Psalmy i Prorocy'

# Insert the share button into EVERY day-header-cell across all 365 days
$enhancedTbody = [regex]::Replace($enhancedTbody, '(?s)<tr\s+role="row"\s+data-date="([^"]+)"\s+data-day="([^"]+)">\s*<td\s+role="cell"\s+class="num">\s*<div\s+class="day-header-cell">\s*<span\s+class="day-title-text"[^>]*>.*?</span>\s*(?:<button[^>]*class="btn-share"[^>]*>.*?</button>)?\s*</div>', {
    param($m)
    $dDate = $m.Groups[1].Value
    $dDay = $m.Groups[2].Value
    return "<tr role=`"row`" data-date=`"$dDate`" data-day=`"$dDay`">`n          <td role=`"cell`" class=`"num`">`n            <div class=`"day-header-cell`">`n              <span class=`"day-title-text`" data-pl=`"Dzień $dDay`" data-en=`"Day $dDay`">Dzień $dDay <span class=`"date-tag`">• $dDate</span></span>`n              <button type=`"button`" class=`"btn-share`" onclick=`"shareDay($dDay, '$dDate')`" aria-label=`"Udostępnij czytanie na dzień $dDay ($dDate)`"><span class=`"share-icon`" aria-hidden=`"true`">📤</span> <span class=`"share-text`" data-pl=`"Udostępnij`" data-en=`"Share`">Udostępnij</span></button>`n            </div>"
})

$shareBtnCount = [regex]::Matches($enhancedTbody, 'class="btn-share"').Count
Write-Host "Liczba przyciskow Udostępnij w tabeli: $shareBtnCount (oczekiwano 365)"

$headerPart = @'
<!doctype html>
<html lang="pl" data-theme="auto">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title id="doc-title">Harmonogram Czytania Biblii — prawdybiblijne.com</title>
  <meta name="description" content="Roczny plan czytania całej Biblii (Plan Roberta Robertsa — Bible Companion) zintegrowany z dwupanelowym czytnikiem HiperBiblia.com.">
  <link rel="canonical" href="https://chrisnewbie.github.io/czytanie-biblii/">

  <!-- Open Graph / Facebook / WhatsApp -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://chrisnewbie.github.io/czytanie-biblii/">
  <meta property="og:title" content="Harmonogram Czytania Biblii (prawdybiblijne.com)">
  <meta property="og:description" content="Przeczytaj całą Biblię w rok (3 nurty dziennie) w czytniku HiperBiblia.com z wybranymi przekładami.">
  <meta property="og:image" content="https://chrisnewbie.github.io/czytanie-biblii/apple-touch-icon.png">
  <meta property="og:locale" content="pl_PL">
  <meta property="og:locale:alternate" content="en_US">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Harmonogram Czytania Biblii (prawdybiblijne.com)">
  <meta name="twitter:description" content="Roczny plan czytania Biblii zintegrowany z HiperBiblia.com.">
  <meta name="twitter:image" content="https://chrisnewbie.github.io/czytanie-biblii/apple-touch-icon.png">

  <!-- PWA & Favicon Suite -->
  <meta name="theme-color" content="#0f172a" id="meta-theme-color">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="alternate icon" href="favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">

  <!-- Schema.org JSON-LD Structured Data -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "Harmonogram Czytania Biblii (prawdybiblijne.com)",
    "url": "https://chrisnewbie.github.io/czytanie-biblii/",
    "description": "Roczny plan czytania całej Biblii oparty na stałym kalendarzu chrystadelfiańskim (Bible Companion) zintegrowany z czytnikiem HiperBiblia.com",
    "applicationCategory": "LifestyleApplication",
    "operatingSystem": "All",
    "inLanguage": ["pl", "en"]
  }
  </script>

  <!-- Prevent Flash of Wrong Theme (FOUC) -->
  <script>
    (function() {
      const savedTheme = localStorage.getItem('hiper_theme') || 'auto';
      if (savedTheme === 'dark' || (savedTheme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
      }
    })();
  </script>

  <style>
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
      --focus-ring: #0284c7;
    }

    html[data-theme="dark"] {
      color-scheme: dark;
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
      --focus-ring: #38bdf8;
    }

    html[data-theme="light"] {
      color-scheme: light;
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
      --focus-ring: #0284c7;
    }

    * { box-sizing: border-box; }

    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 1rem;
      color: var(--text-main);
      background-color: var(--bg-body);
      font-size: 16px;
      line-height: 1.5;
      transition: background-color 0.25s ease, color 0.25s ease;
    }

    /* Skip to content link (WCAG 2.4.1) */
    .skip-link {
      position: absolute;
      top: -9999px;
      left: 1rem;
      background: var(--accent);
      color: #ffffff;
      padding: 0.75rem 1.25rem;
      border-radius: 8px;
      font-weight: 700;
      text-decoration: none;
      z-index: 10000;
      transition: top 0.2s ease;
    }
    .skip-link:focus {
      top: 1rem;
      outline: 3px solid var(--text-main);
    }

    /* Header & Navigation bar */
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

    h1 a.title-link {
      display: inline;
      background: transparent;
      border: none;
      padding: 0;
      min-height: auto;
      border-radius: 0;
      color: var(--accent);
      text-decoration: underline;
      text-underline-offset: 3px;
      font-size: inherit;
      font-weight: inherit;
      transition: color 0.15s ease;
    }
    h1 a.title-link:hover {
      background: transparent;
      color: var(--text-main);
      text-decoration: underline;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }

    .switcher-pill {
      display: inline-flex;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 999px;
      padding: 0.25rem;
      gap: 0.25rem;
    }

    .pill-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-weight: 700;
      font-size: 0.88rem;
      padding: 0.4rem 0.75rem;
      border-radius: 999px;
      cursor: pointer;
      transition: all 0.2s;
      font-family: inherit;
      min-height: 38px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .pill-btn:hover {
      color: var(--text-main);
    }
    .pill-btn.active {
      background: var(--accent);
      color: #ffffff;
    }

    p.sub {
      font-size: 0.95rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
    }

    /* Controls Panel */
    .controls {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 1.1rem 1.25rem;
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

    .select-group select:focus-visible, .select-group input[type="date"]:focus-visible, .btn-today:focus-visible, .pill-btn:focus-visible, .btn-share:focus-visible, a:focus-visible {
      outline: 3px solid var(--focus-ring);
      outline-offset: 2px;
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
      transition: all 0.2s;
      font-family: inherit;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.3rem;
    }
    .btn-today:hover {
      background: var(--btn-today-hover);
      transform: translateY(-1px);
    }

    /* Table & High Performance Row Rendering */
    table {
      border-collapse: collapse;
      width: 100%;
      font-size: 0.95rem;
      margin-top: 1rem;
      background: var(--bg-card);
      border-radius: 12px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    /* CSS content-visibility for ultra-fast initial render of 365 rows */
    tbody tr {
      content-visibility: auto;
      contain-intrinsic-size: auto 60px;
      scroll-margin-top: 100px;
      scroll-margin-bottom: 100px;
      transition: background-color 0.3s ease, border-color 0.3s ease;
    }

    th, td {
      border: 1px solid var(--border-color);
      padding: 10px 14px;
      vertical-align: middle;
      text-align: left;
      transition: background-color 0.3s ease;
    }

    th {
      position: sticky;
      top: 0;
      background: var(--header-bg);
      color: var(--header-text);
      font-weight: 700;
      font-size: 0.9rem;
      z-index: 10;
    }

    tbody tr:nth-child(even) td { background: var(--table-stripe); }

    /* Permanent highlight for Today's row */
    tr.today-row {
      border-left: 5px solid var(--btn-today-bg) !important;
      background-color: var(--accent-bg) !important;
    }
    tr.today-row td {
      background-color: transparent !important;
    }
    
    .today-badge {
      display: inline-flex;
      align-items: center;
      background: var(--btn-today-bg);
      color: #ffffff;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 0.15rem 0.55rem;
      border-radius: 999px;
      margin-left: 0.4rem;
      vertical-align: middle;
      letter-spacing: 0.02em;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }

    td.num {
      font-weight: bold;
      color: var(--accent);
      min-width: 190px;
    }
    
    .day-header-cell {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      width: 100%;
      box-sizing: border-box;
    }

    .day-title-text {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      flex-wrap: wrap;
    }

    .date-tag { font-weight: normal; color: var(--text-muted); font-size: 0.85rem; }
    .track-lbl { display: none; font-weight: 700; color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; }
    .btn-group { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }

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
      transition: all 0.15s ease;
    }
    a:hover {
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }

    /* Unified Share Button */
    .btn-share {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.35rem;
      background: var(--accent-bg);
      color: var(--accent);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 0.35rem 0.65rem;
      font-weight: 700;
      font-size: 0.82rem;
      cursor: pointer;
      min-height: 36px;
      transition: all 0.15s;
      font-family: inherit;
      white-space: nowrap;
      flex-shrink: 0;
      box-sizing: border-box;
    }
    .btn-share:hover {
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }

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

    /* Accessible Toast Notification */
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
      box-shadow: 0 4px 14px rgba(0,0,0,0.35);
      z-index: 9999;
      animation: fadeInOut 3s ease forwards;
      border: 1px solid rgba(255,255,255,0.15);
    }
    @keyframes fadeInOut {
      0% { opacity: 0; transform: translate(-50%, 20px); }
      15% { opacity: 1; transform: translate(-50%, 0); }
      85% { opacity: 1; transform: translate(-50%, 0); }
      100% { opacity: 0; transform: translate(-50%, -20px); }
    }

    /* Dynamic Flash Glow Pulse on Target Jump */
    @keyframes targetGlowPulse {
      0% {
        outline: 3px solid #6366f1;
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
        background-color: var(--flash-bg) !important;
      }
      35% {
        outline: 3px solid #6366f1;
        box-shadow: 0 0 0 14px rgba(99, 102, 241, 0);
        background-color: var(--flash-bg) !important;
      }
      70% {
        background-color: var(--flash-bg) !important;
      }
      100% {
        outline: 3px solid transparent;
        box-shadow: none;
      }
    }

    .highlight-flash {
      animation: targetGlowPulse 2.8s ease-out forwards;
      position: relative;
      z-index: 5;
    }
    .highlight-flash td {
      background-color: transparent !important;
    }

    /* Mobile Responsive Design with Preserved A11y Semantics */
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

      table, thead, tbody, th, td, tr { display: block; width: 100%; box-sizing: border-box; }
      thead { display: none; }
      
      tbody tr {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin-bottom: 1.25rem;
        padding: 0.85rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        contain-intrinsic-size: auto 190px;
        scroll-margin-top: 20px;
        scroll-margin-bottom: 20px;
        box-sizing: border-box;
      }

      tr.today-row {
        border: 2px solid var(--btn-today-bg) !important;
        border-left: 6px solid var(--btn-today-bg) !important;
      }

      td {
        border: none;
        padding: 0.4rem 0;
        width: 100%;
        box-sizing: border-box;
      }

      td.num {
        font-size: 1.15rem;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
        white-space: normal;
        min-width: 0;
      }
      
      td.num .day-header-cell {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        width: 100%;
        flex-wrap: wrap;
        box-sizing: border-box;
      }

      .day-title-text {
        font-size: 1.15rem;
        flex: 1 1 auto;
      }

      .btn-share {
        padding: 0.35rem 0.65rem;
        font-size: 0.82rem;
        min-height: 36px;
        margin-left: auto;
      }

      .track-lbl { display: block; margin-bottom: 0.15rem; }

      .btn-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        width: 100%;
        margin-top: 0.5rem;
        box-sizing: border-box;
      }

      a {
        width: 100%;
        font-size: 1rem;
        padding: 0.75rem 1rem;
        min-height: 48px;
        border-radius: 10px;
        box-sizing: border-box;
      }
    }

    /* Print Stylesheet */
    @media print {
      body { background: #ffffff !important; color: #000000 !important; margin: 0; font-size: 12pt; }
      .controls, p.sub, .btn-share, .btn-back-to-top, .nav-actions, .skip-link { display: none !important; }
      table { border: 1px solid #000 !important; box-shadow: none !important; }
      th, td { border: 1px solid #666 !important; color: #000 !important; background: #fff !important; }
      th { background: #eee !important; color: #000 !important; }
      a { border: none !important; background: transparent !important; color: #000 !important; padding: 0 !important; }
      a::after { content: " (" attr(href) ")"; font-size: 8pt; color: #444; }
    }
  </style>
</head>
<body>
  <!-- Skip Link for Keyboard Accessibility -->
  <a href="#main-table" class="skip-link" id="skip-link-text">Przejdź do tabeli czytań</a>

  <header class="app-header">
    <div class="top-bar">
      <h1 id="main-h1">Harmonogram Czytania Biblii (<a href="https://prawdybiblijne.com" target="_blank" rel="noopener noreferrer" class="title-link">prawdybiblijne.com</a>)</h1>
      <div class="nav-actions">
        <!-- Theme Switcher (Light / Dark / Auto) -->
        <div class="switcher-pill" role="group" aria-label="Wybór motywu kolorystycznego">
          <button type="button" class="pill-btn" id="btn-theme-light" onclick="setTheme('light')" aria-label="Motyw jasny" aria-pressed="false">☀️</button>
          <button type="button" class="pill-btn" id="btn-theme-auto" onclick="setTheme('auto')" aria-label="Motyw systemowy (auto)" aria-pressed="true">💻</button>
          <button type="button" class="pill-btn" id="btn-theme-dark" onclick="setTheme('dark')" aria-label="Motyw ciemny" aria-pressed="false">🌙</button>
        </div>
        <!-- Language Switcher -->
        <div class="switcher-pill" role="group" aria-label="Wybór języka interfejsu">
          <button type="button" class="pill-btn active" id="btn-lang-pl" onclick="setLanguage('pl')" aria-label="Język polski" aria-pressed="true">🇵🇱 PL</button>
          <button type="button" class="pill-btn" id="btn-lang-en" onclick="setLanguage('en')" aria-label="English language" aria-pressed="false">🇬🇧 EN</button>
        </div>
      </div>
    </div>
    <p class="sub" id="main-sub">Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z wybranymi przez Ciebie przekładami.</p>
  </header>

  <main id="main-content">
    <section class="controls" role="region" aria-label="Wybór przekładów i nawigacja kalendarza">
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
          <option value="ubg" selected>Uwspółcześniona Biblia Gdańska (ubg)</option>
          <option value="snpd">EIB Przekład Dosłowny (snpd)</option>
          <option value="snp">EIB Przekład Literacki (snp)</option>
          <option value="bt5">Biblia Tysiąclecia V (bt5)</option>
          <option value="bt4">Biblia Tysiąclecia IV (bt4)</option>
          <option value="bt2">Biblia Tysiąclecia II (bt2)</option>
          <option value="bp">Biblia Poznańska (bp)</option>
          <option value="bw">Biblia Warszawska (bw)</option>
          <option value="bwp">Biblia Warszawsko-Praska (bwp)</option>
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
        <label for="input-date-jump" id="lbl-date-jump">📅 Przejdź do daty:</label>
        <div class="date-input-row">
          <input type="date" id="input-date-jump" min="2026-01-01" max="2026-12-31" aria-label="Wybierz datę z kalendarza">
          <button type="button" id="btn-today" class="btn-today" onclick="jumpToToday()" aria-label="Przejdź do dzisiejszego dnia">🎯 Dzisiaj</button>
        </div>
      </div>
    </section>

    <table id="main-table" role="table" aria-label="Tabela rocznego harmonogramu czytania Biblii">
      <thead role="rowgroup">
        <tr role="row">
          <th scope="col" role="columnheader" id="th-day">Dzień</th>
          <th scope="col" role="columnheader" id="th-t1">ST: Prawo i Historia</th>
          <th scope="col" role="columnheader" id="th-t2">ST: Psalmy i Prorocy</th>
          <th scope="col" role="columnheader" id="th-t3">Nowy Testament</th>
          <th scope="col" role="columnheader" id="th-links">Linki HiperBiblia.com</th>
        </tr>
      </thead>
      <tbody role="rowgroup">
'@

$footerPart = @'
      </tbody>
    </table>
  </main>

  <button id="btn-back-to-top" class="btn-back-to-top" onclick="scrollToTop()" aria-label="Wróć na górę strony">⬆️ Do góry</button>

  <!-- Live region for screen readers -->
  <div id="a11y-live-region" role="status" aria-live="polite" class="visually-hidden" style="position:absolute; width:1px; height:1px; margin:-1px; padding:0; overflow:hidden; clip:rect(0,0,0,0); border:0;"></div>

  <script>
    const KEY_LEFT = 'hiper_left_translation';
    const KEY_RIGHT = 'hiper_right_translation';
    const KEY_LANG = 'hiper_lang';
    const KEY_THEME = 'hiper_theme';
    let currentLang = 'pl';
    let currentTheme = 'auto';

    function getTodayIso() {
      const now = new Date();
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      const dd = String(now.getDate()).padStart(2, '0');
      return `2026-${mm}-${dd}`;
    }

    function initApp() {
      const savedLang = localStorage.getItem(KEY_LANG) || 'pl';
      const savedLeft = localStorage.getItem(KEY_LEFT) || 'snpd';
      const savedRight = localStorage.getItem(KEY_RIGHT) || 'ubg';
      const savedTheme = localStorage.getItem(KEY_THEME) || 'auto';

      document.getElementById('select-left').value = savedLeft;
      document.getElementById('select-right').value = savedRight;

      // Set current date in picker
      const todayIso = getTodayIso();
      const dateInput = document.getElementById('input-date-jump');
      if (dateInput) dateInput.value = todayIso;
      
      document.getElementById('select-left').addEventListener('change', updateTableLinks);
      document.getElementById('select-right').addEventListener('change', updateTableLinks);
      document.getElementById('input-date-jump').addEventListener('change', (e) => jumpToDate(e.target.value));
      document.getElementById('btn-today').addEventListener('click', () => jumpToToday(false));

      // Delegated link click for maximum performance
      document.getElementById('main-table').addEventListener('click', handleTableClick);

      window.addEventListener('scroll', () => {
        const btn = document.getElementById('btn-back-to-top');
        if (btn) {
          if (window.scrollY > 300) btn.classList.add('visible');
          else btn.classList.remove('visible');
        }
      });

      setTheme(savedTheme, false);
      setLanguage(savedLang, false);
      updateTableLinks();
      markTodayRow();
    }

    function markTodayRow() {
      const todayIso = getTodayIso();
      const targetRow = document.querySelector(`tr[data-date="${todayIso}"]`);
      if (targetRow) {
        targetRow.classList.add('today-row');
        const dayTitle = targetRow.querySelector('.day-title-text');
        if (dayTitle && !dayTitle.querySelector('.today-badge')) {
          const badge = document.createElement('span');
          badge.className = 'today-badge';
          badge.setAttribute('data-pl', 'Dzisiaj');
          badge.setAttribute('data-en', 'Today');
          badge.innerText = currentLang === 'en' ? 'Today' : 'Dzisiaj';
          dayTitle.appendChild(badge);
        }
      }
    }

    function handleTableClick(e) {
      const link = e.target.closest('a[data-base-url]');
      if (!link) return;
      const left = document.getElementById('select-left').value;
      const right = document.getElementById('select-right').value;
      const lang = currentLang || 'pl';
      const baseUrl = link.getAttribute('data-base-url');
      if (baseUrl && baseUrl.includes('hiperbiblia.com/reader')) {
        try {
          const urlObj = new URL(baseUrl);
          urlObj.searchParams.set('left', left);
          urlObj.searchParams.set('right', right);
          urlObj.searchParams.set('locale', lang);
          link.href = urlObj.toString();
        } catch (err) {}
      }
    }

    function setTheme(theme, save = true) {
      currentTheme = theme;
      if (save) localStorage.setItem(KEY_THEME, theme);

      const htmlEl = document.documentElement;
      if (theme === 'auto') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        htmlEl.setAttribute('data-theme', isDark ? 'dark' : 'light');
      } else {
        htmlEl.setAttribute('data-theme', theme);
      }

      document.getElementById('btn-theme-light').classList.toggle('active', theme === 'light');
      document.getElementById('btn-theme-light').setAttribute('aria-pressed', theme === 'light');
      document.getElementById('btn-theme-auto').classList.toggle('active', theme === 'auto');
      document.getElementById('btn-theme-auto').setAttribute('aria-pressed', theme === 'auto');
      document.getElementById('btn-theme-dark').classList.toggle('active', theme === 'dark');
      document.getElementById('btn-theme-dark').setAttribute('aria-pressed', theme === 'dark');

      const metaTheme = document.getElementById('meta-theme-color');
      if (metaTheme) {
        metaTheme.setAttribute('content', htmlEl.getAttribute('data-theme') === 'dark' ? '#0f172a' : '#ffffff');
      }
    }

    function setLanguage(lang, userTriggered = true) {
      currentLang = lang;
      localStorage.setItem(KEY_LANG, lang);

      const isEn = lang === 'en';
      document.getElementById('btn-lang-pl').classList.toggle('active', !isEn);
      document.getElementById('btn-lang-pl').setAttribute('aria-pressed', !isEn);
      document.getElementById('btn-lang-en').classList.toggle('active', isEn);
      document.getElementById('btn-lang-en').setAttribute('aria-pressed', isEn);
      document.documentElement.lang = lang;

      if (userTriggered) {
        if (isEn) {
          document.getElementById('select-left').value = 'kjv';
          document.getElementById('select-right').value = 'esv';
        } else {
          document.getElementById('select-left').value = 'snpd';
          document.getElementById('select-right').value = 'ubg';
        }
      }

      // Text UI translations
      document.getElementById('skip-link-text').innerText = isEn ? 'Skip to reading table' : 'Przejdź do tabeli czytań';
      document.getElementById('main-h1').innerHTML = isEn 
        ? 'Bible Reading Companion (<a href="https://prawdybiblijne.com" target="_blank" rel="noopener noreferrer" class="title-link">prawdybiblijne.com</a>)' 
        : 'Harmonogram Czytania Biblii (<a href="https://prawdybiblijne.com" target="_blank" rel="noopener noreferrer" class="title-link">prawdybiblijne.com</a>)';
      document.getElementById('main-sub').innerHTML = isEn ? 'Clicking any button opens <strong>HiperBiblia.com</strong> dual-panel reader with your chosen translations.' : 'Kliknięcie w przycisk otwiera czytnik w serwisie <strong>HiperBiblia.com</strong> z wybranymi przez Ciebie przekładami.';
      document.getElementById('lbl-left').innerText = isEn ? 'Left Panel (Translation 1):' : 'Lewy panel (Przekład 1):';
      document.getElementById('lbl-right').innerText = isEn ? 'Right Panel (Translation 2):' : 'Prawy panel (Przekład 2):';
      document.getElementById('lbl-date-jump').innerText = isEn ? '📅 Jump to date:' : '📅 Przejdź do daty:';
      document.getElementById('btn-today').innerHTML = isEn ? '🎯 Today' : '🎯 Dzisiaj';
      document.getElementById('btn-back-to-top').innerText = isEn ? '⬆️ Back to Top' : '⬆️ Do góry';

      document.getElementById('th-day').innerText = isEn ? 'Day' : 'Dzień';
      document.getElementById('th-t1').innerText = isEn ? 'OT: Law & History' : 'ST: Prawo i Historia';
      document.getElementById('th-t2').innerText = isEn ? 'OT: Psalms & Prophets' : 'ST: Psalmy i Prorocy';
      document.getElementById('th-t3').innerText = isEn ? 'New Testament' : 'Nowy Testament';
      document.getElementById('th-links').innerText = isEn ? 'HiperBiblia.com Links' : 'Linki HiperBiblia.com';

      // Update row texts batch
      document.querySelectorAll('.day-title-text').forEach(el => {
        const dateTag = el.querySelector('.date-tag');
        const dateStr = dateTag ? dateTag.outerHTML : '';
        const dayNum = el.closest('tr').getAttribute('data-day');
        const badge = el.querySelector('.today-badge');
        const badgeHtml = badge ? `<span class="today-badge" data-pl="Dzisiaj" data-en="Today">${isEn ? 'Today' : 'Dzisiaj'}</span>` : '';
        el.innerHTML = isEn ? `Day ${dayNum} ${dateStr}${badgeHtml}` : `Dzień ${dayNum} ${dateStr}${badgeHtml}`;
      });

      document.querySelectorAll('.track-lbl').forEach(el => {
        el.innerText = isEn ? el.getAttribute('data-en') : el.getAttribute('data-pl');
      });

      document.querySelectorAll('.ref-text').forEach(el => {
        el.innerText = isEn ? el.getAttribute('data-en') : el.getAttribute('data-pl');
      });

      document.querySelectorAll('a[data-lbl-pl]').forEach(el => {
        el.innerText = isEn ? el.getAttribute('data-lbl-en') : el.getAttribute('data-lbl-pl');
      });

      document.querySelectorAll('.share-text').forEach(el => {
        el.innerText = isEn ? el.getAttribute('data-en') : el.getAttribute('data-pl');
      });

      updateTableLinks();
    }

    function scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function updateTableLinks() {
      const left = document.getElementById('select-left').value;
      const right = document.getElementById('select-right').value;
      const lang = currentLang || 'pl';
      localStorage.setItem(KEY_LEFT, left);
      localStorage.setItem(KEY_RIGHT, right);

      const links = document.querySelectorAll('table a[data-base-url]');
      links.forEach(link => {
        const baseUrl = link.getAttribute('data-base-url');
        if (baseUrl && baseUrl.includes('hiperbiblia.com/reader')) {
          try {
            const urlObj = new URL(baseUrl);
            urlObj.searchParams.set('left', left);
            urlObj.searchParams.set('right', right);
            urlObj.searchParams.set('locale', lang);
            link.href = urlObj.toString();
          } catch (e) {}
        }
      });
    }

    function jumpToDate(isoDate, isInitialLoad = false) {
      if (!isoDate) return;

      // Handle any year mismatch by looking up month-day in 2026
      let targetIso = isoDate;
      let targetRow = document.querySelector(`tr[data-date="${targetIso}"]`);
      if (!targetRow) {
        const parts = isoDate.split('-');
        if (parts.length === 3) {
          targetIso = `2026-${parts[1]}-${parts[2]}`;
          targetRow = document.querySelector(`tr[data-date="${targetIso}"]`);
        }
      }

      if (targetRow) {
        // First instant jump to force un-virtualization in browser rendering engine
        targetRow.scrollIntoView({ behavior: 'auto', block: 'center' });

        // Second micro-task for pixel-perfect centering
        requestAnimationFrame(() => {
          const rect = targetRow.getBoundingClientRect();
          const idealOffset = (window.innerHeight / 2) - (rect.height / 2);
          const delta = rect.top - idealOffset;
          if (Math.abs(delta) > 5) {
            window.scrollBy({ top: delta, behavior: isInitialLoad ? 'auto' : 'smooth' });
          }
        });

        // Trigger flash highlight animation
        targetRow.classList.remove('highlight-flash');
        void targetRow.offsetWidth; // Force CSS reflow
        targetRow.classList.add('highlight-flash');

        if (!isInitialLoad) {
          announceA11y(currentLang === 'en' ? `Jumped to reading for ${targetIso}` : `Przewinięto do czytania na dzień ${targetIso}`);
        }

        setTimeout(() => {
          targetRow.classList.remove('highlight-flash');
        }, 2800);
      }
    }

    function jumpToToday(isInitialLoad = false) {
      const todayIso = getTodayIso();
      const picker = document.getElementById('input-date-jump');
      if (picker) picker.value = todayIso;
      jumpToDate(todayIso, isInitialLoad);
    }

    function shareDay(dayNum, dateStr) {
      const row = document.querySelector(`tr[data-day="${dayNum}"]`);
      if (!row) return;

      const isEn = currentLang === 'en';
      const t1Text = row.cells[1].querySelector('.ref-text').innerText;
      const t2Text = row.cells[2].querySelector('.ref-text').innerText;
      const t3Text = row.cells[3].querySelector('.ref-text').innerText;

      const links = row.querySelectorAll('a[href]');
      const u1 = links[0] ? links[0].href : '';
      const u2 = links[1] ? links[1].href : '';
      const u3 = links[2] ? links[2].href : '';

      const titleStr = isEn ? `📖 Bible Reading — Day ${dayNum} (${dateStr}):` : `📖 Czytanie Biblii — Dzień ${dayNum} (${dateStr}):`;
      const shareText = `${titleStr}\n\n1. ${t1Text}:\n${u1}\n\n2. ${t2Text}:\n${u2}\n\n3. ${t3Text}:\n${u3}`;

      if (navigator.share) {
        navigator.share({
          title: isEn ? `Bible Reading — Day ${dayNum}` : `Czytanie Biblii — Dzień ${dayNum}`,
          text: shareText
        }).catch(() => {});
      } else {
        navigator.clipboard.writeText(shareText).then(() => {
          showToast(isEn ? `📋 Copied Day ${dayNum} reading to clipboard!` : `📋 Skopiowano czytanie na Dzień ${dayNum} do schowka!`);
        });
      }
    }

    function announceA11y(msg) {
      const live = document.getElementById('a11y-live-region');
      if (live) live.innerText = msg;
    }

    function showToast(msg) {
      const old = document.querySelector('.toast-msg');
      if (old) old.remove();
      const toast = document.createElement('div');
      toast.className = 'toast-msg';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      toast.innerText = msg;
      document.body.appendChild(toast);
      announceA11y(msg);
      setTimeout(() => toast.remove(), 3200);
    }

    document.addEventListener('DOMContentLoaded', initApp);
  </script>
</body>
</html>
'@

$newDocument = $headerPart + $enhancedTbody + $footerPart
[System.IO.File]::WriteAllText($v2Path, $newDocument, [System.Text.Encoding]::UTF8)
Write-Host "SUKCES! Pomyślnie wygenerowano $v2Path z nagłówkiem 'Nowy Testament'."
