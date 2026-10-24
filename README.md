# 👶 DACH Elterngeld-, Mutterschutz- & Elternzeit-Rechner 2026 (BEEG, MSchG, KBGG, EOG)

[![CI](https://github.com/DACHDigitalwerk/elterngeld-elternzeit-rechner-dach/actions/workflows/ci.yml/badge.svg)](https://github.com/DACHDigitalwerk/elterngeld-elternzeit-rechner-dach/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Hochpräzise, modulare Python-Bibliothek und CLI-Tool zur gesetzeskonformen Berechnung und Optimierung von **Elterngeld, ElterngeldPlus, Mutterschaftsgeld, Wochengeld und Schweizer Mutterschafts- bzw. Vaterschaftsentschädigung 2026** für Deutschland, Österreich und die Schweiz.

🌐 **Interaktives Web-Tool & Timeline-Monatsplaner:**  
Besuchen Sie unser kostenloses, 100 % clientseitiges Web-Tool:  
👉 **[DACH Elterngeld- & Elternzeit-Planer 2026](https://dachdigitalwerk.github.io/elterngeld-elternzeit-rechner/)**

---

## 🚀 Kernfunktionen

### 1. 🇩🇪 Deutschland (BEEG & MuSchG)
- **Gesetzliche Ersatzrate (§ 2 BEEG):**
  - Standard: 67 % bei Nettoeinkommen zwischen 1.000 € und 1.200 €
  - Geringverdiener-Bonus: schrittweiser Anstieg auf bis zu 100 % bei < 1.000 € (je 2 € um 0,1 %-Punkte)
  - Degressive Absenkung auf 65 % bei > 1.200 € (je 20 € um 0,1 %-Punkte)
- **Basiselterngeld:** 300 € bis 1.800 € monatlich (12 bis 14 Bezugsmonate)
- **ElterngeldPlus:** 150 € bis 900 € monatlich (doppelte Bezugsdauer)
- **Geschwisterbonus:** +10 % Zuschlag (mind. 75 € Basis bzw. 37,50 € Plus)
- **Mehrlingszuschlag:** +300 € Basis bzw. +150 € Plus je weiterem Mehrling
- **Einkommensgrenze 2025/2026:** 175.000 € zu versteuerndes Jahreseinkommen gem. Haushaltsbegleitgesetz (§ 1 Abs. 8 BEEG)
- **Mutterschaftsgeld-Anrechnung:** Vollständige Gegenrechnung gem. § 3 BEEG
- **Teilzeit während Elternzeit:** Max. 32 Wochenstunden (§ 1 Abs. 6 BEEG) und Partnerschaftsbonus-Prüfung (24–32 Std.)

### 2. 🇦🇹 Österreich (MSchG & KBGG)
- **Wochengeld (§ 162 ASVG):** 100 % des durchschnittlichen Nettoeinkommens der letzten 3 Monate zzgl. 17 % Sonderzahlungszuschlag (16 Wochen Schutzfrist, bei Kaiserschnitt/Mehrlingen 20 Wochen)
- **Einkommensabhängiges KBG (ea KBG):** 80 % des Letztgehalts (max. 73,88 € pro Tag = ~ 2.216,40 €/Monat für bis zu 365–426 Tage)
- **Pauschales KBG-Konto:** Flexibel wählbar von 365 bis 1.063 Tage (Tagessatz zwischen 16,93 € und 39,12 €)
- **Zuverdienstgrenzen:** 8.600 € / Jahr (ea KBG) bzw. 60 % des Letzteinkommens (KBG-Konto)

### 3. 🇨🇭 Schweiz (EOG & VAEg)
- **Mutterschaftsentschädigung (MSE):** 80 % des durchschnittlichen Lohns vor der Niederkunft, max. 220 CHF pro Tag (Deckelung ab 8.250 CHF Monatslohn) für 14 Wochen (98 Kalendertage)
- **Vaterschaftsentschädigung (Urlaub für den anderen Elternteil):** 80 % Lohn, max. 220 CHF pro Tag für 2 Wochen (14 Taggelder bzw. 10 Arbeitstage)

---

## 📦 Installation

```bash
pip install git+https://github.com/DACHDigitalwerk/elterngeld-elternzeit-rechner-dach.git
```

Oder lokal klonen:
```bash
git clone https://github.com/DACHDigitalwerk/elterngeld-elternzeit-rechner-dach.git
cd elterngeld-elternzeit-rechner-dach
pip install -e .
```

---

## 💻 Verwendung

### CLI (Kommandozeile)

```bash
# Deutschland: 2.500 EUR Netto mit Geschwisterbonus
dach-elterngeld de --netto 2500 --geschwisterbonus

# Deutschland: Teilzeit mit 25 Wochenstunden und 1.000 EUR Netto
dach-elterngeld de --netto 2500 --teilzeit-netto 1000 --teilzeit-stunden 25

# Österreich: Wochengeld & Einkommensabhängiges KBG
dach-elterngeld at --netto 2200 --modell ea

# Schweiz: Mutterschafts- und Vaterschaftsentschädigung
dach-elterngeld ch --brutto 7500
```

JSON-Ausgabe:
```bash
dach-elterngeld de --netto 2800 --json
```

### Python-API

```python
from elterngeld_dach import calculate_germany_elterngeld, calculate_austria_benefits, calculate_switzerland_benefits

# Deutschland
de_res = calculate_germany_elterngeld(
    net_income_before=2400.0,
    has_qualifying_siblings=True,
    multiple_birth_count=1,
)
print(f"Basiselterngeld: {de_res['monthly_basis_elterngeld']:.2f} €")
print(f"ElterngeldPlus: {de_res['monthly_plus_elterngeld']:.2f} €")

# Schweiz
ch_res = calculate_switzerland_benefits(monthly_gross_salary=8000.0)
print(f"MSE Tagessatz: {ch_res['daily_mse']:.2f} CHF")
print(f"MSE Gesamtsumme: {ch_res['mse_total_payout']:.2f} CHF")
```

---

## 🧪 Tests

```bash
pytest -v
```

---

## ⚖️ Rechtlicher Hinweis
Dieses Open-Source-Werkzeug dient der technischen Berechnung und Orientierung. Es stellt keine Rechts- oder Steuerberatung im Sinne des § 2 RDG bzw. § 5 StBerG dar. Für verbindliche Bescheide sind die Elterngeldstellen, Gebietskrankenkassen bzw. Ausgleichskassen zuständig.

---

## 📄 Lizenz
MIT License. Siehe [LICENSE](LICENSE) für Details.
