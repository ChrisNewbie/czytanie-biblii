# 📖 Oficjalny Pakiet Czytania Biblii (Plan Roberta Robertsa — Rok 2026)

Witaj w oficjalnym suicie narzędziowym do rocznego czytania Biblii dla chrystadelfian. Projekt stanowi oficjalny, w 100% zweryfikowany pakiet czytań oparty na stałym kalendarzu chrystadelfiańskim (**Bible Companion** autorstwa Roberta Robertsa z 1883 roku).

![Build Status](https://img.shields.io/badge/Wyrocznia-Oficjalny%20Kalendarz-blue)
![PWA Ready](https://img.shields.io/badge/PWA-Gotowe-green)
![License](https://img.shields.io/badge/Licencja-MIT-orange)

---

## 🌟 Główne Cechy Projektu

* 🏛️ **Single Source of Truth**: Wskaźniki czytań wyekstrahowane bezpośrednio z oficjalnej Wyroczni `prawdy-biblijne-index.html`.
* 🔗 **Integracja z HiperBiblia.com**: Wszystkie czytania (3 nurty dziennie) otwierają dwupanelowy czytnik w serwisie **HiperBiblia.com** z możliwością bieżącej zmiany przekładów lewego i prawego panelu.
* 📱 **Pełna Responsywność (RWD & Dark Mode)**: Strona automatycznie zmienia się w wygodne karty na smartfonach, wspiera natywny tryb ciemny oraz wysokie przyciski dotykowe (min. 48px).
* 📤 **Przycisk "Udostępnij"**: Natychmiastowe udostępnianie fragmentów dziennych znajomym (WhatsApp, Signal, Messenger, SMS) z bezpośrednimi linkami.
* 📅 **Natywna Kontrolka Kalendarza**: Wybór dowolnego dnia roku z natywnego kalendarza telefonu i płynny skok z rozświetleniem widoku.
* 📦 **Wieloformatowość**: Wygenerowane produkty dla każdego urządzenia (PWA, HTML, EPUB Kindle, iCal, CSV).

---

## 📁 Gotowe Produkty w Katalogu `output/`

| Format | Opis | Zastosowanie |
| :--- | :--- | :--- |
| 🌐 **[Harmonogram HTML (Vanilla JS)](output/harmonogram_chrystadelfianie_2026.html)** | Szybka strona HTML (Standard 2026) | Komputery, telefony, przeglądarki WWW |
| ⚙️ **[Harmonogram HTML (jQuery 3.7.1)](output/harmonogram_chrystadelfianie_2026_jquery.html)** | Strona HTML zasilana jQuery 3.7.1 | Wersja porównawcza |
| 📲 **[Aplikacja PWA Web App](output/pwa/index.html)** | Aplikacja z paskiem postępu i checkboxami | Działa w trybie Offline na smartfonach |
| 📖 **[E-book EPUB dla Kindle](output/Biblia_Plan_Robertsa_2026.epub)** | Kompletny e-book z aktywnym spisem treści | Czytniki e-booków Kindle, PocketBook, Kobo |
| 📅 **[Kalendarz iCal (.ics)](output/Biblia_Plan_Robertsa_2026.ics)** | Plik zdarzeń dla kalendarza | Google Calendar, Apple Calendar, Outlook |
| 📊 **[Arkusz CSV z BOM](output/harmonogram_chrystadelfianie_2026.csv)** | Surowe dane z kodowaniem UTF-8-sig | Microsoft Excel, Google Sheets |

---

## 🛠️ Uruchamianie Generatora Suity

Cały pakiet budowany jest deterministycznie za pomocą jednego polecenia Pythona:

```bash
python build_roberts_suite.py --year 2026 --left snpd --right lxxhb
```

### Opcje CLI:
* `--year`: Rok kalendarzowy (domyślnie: `2026`).
* `--left`: Domyślny kod lewego przekładu w HiperBiblia.com (domyślnie: `snpd` - EIB Dosłowny).
* `--right`: Domyślny kod prawego przekładu w HiperBiblia.com (domyślnie: `lxxhb` - Septuaginta).
* `--out-dir`: Katalog wyjściowy (domyślnie: `output`).

---

## 📜 Licencja

Projekt udostępniany jest na licencji MIT. Wolno kopiować, modyfikować i rozpowszechniać do celów edukacyjnych i religijnych.
