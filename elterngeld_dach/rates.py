# -*- coding: utf-8 -*-
"""
Amtliche Grenzwerte, Leistungs- und Freibeträge für Elterngeld,
Mutterschutz und Elternzeit 2026 im DACH-Raum.
"""

# ==============================================================================
# DEUTSCHLAND: Bundeselterngeld- und Elternzeitgesetz (BEEG) & MuSchG
# ==============================================================================
DE_MIN_BASIS_ELTERNGELD = 300.0
DE_MAX_BASIS_ELTERNGELD = 1800.0

DE_MIN_PLUS_ELTERNGELD = 150.0
DE_MAX_PLUS_ELTERNGELD = 900.0

DE_GESCHWISTERBONUS_PCT = 0.10
DE_GESCHWISTERBONUS_MIN_BASIS = 75.0
DE_GESCHWISTERBONUS_MIN_PLUS = 37.50

DE_MEHRLINGSZUSCHLAG_BASIS = 300.0
DE_MEHRLINGSZUSCHLAG_PLUS = 150.0

# Einkommensgrenze 2025/2026 (Haushaltsbegleitgesetz)
DE_EINKOMMENSGRENZE_2026 = 175000.0  # zu versteuerndes Einkommen

# Maximale Wochenstunden Teilzeit während Elternzeit (§ 1 Abs. 6 BEEG)
DE_MAX_TEILZEIT_WOCHENSTUNDEN = 32.0

# ==============================================================================
# ÖSTERREICH: Mutterschutzgesetz (MSchG) & Kinderbetreuungsgeldgesetz (KBGG)
# ==============================================================================
AT_WOCHENGELD_PCT = 1.00  # 100 % des durchschnittlichen Nettoeinkommens
AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_STANDARD = 16  # 8 Wochen vor + 8 Wochen nach
AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_MEHRLING_KS = 20  # 8 Wochen vor + 12 Wochen nach

# Einkommensabhängiges Kinderbetreuungsgeld (ea KBG)
AT_EA_KBG_PCT = 0.80
AT_EA_KBG_MAX_TAGESSATZ = 73.88  # Euro pro Kalendertag (~ 2.216,40 € / Monat)
AT_EA_KBG_MAX_TAGE_EINZEL = 365
AT_EA_KBG_MAX_TAGE_BEIDE = 426
AT_EA_KBG_ZUVERDIENSTGRENZE = 8600.0  # Euro pro Kalenderjahr

# Pauschales Kinderbetreuungsgeld-Konto
AT_KBG_KONTO_GESAMTBETRAG_EINZEL = 14355.20  # Gesamtbetrag Pauschale
AT_KBG_KONTO_MIN_TAGE = 365
AT_KBG_KONTO_MAX_TAGE = 1063
AT_KBG_KONTO_MIN_TAGESSATZ = 16.93
AT_KBG_KONTO_MAX_TAGESSATZ = 39.12

# ==============================================================================
# SCHWEIZ: Erwerbsersatzgesetz (EOG) & VAEg
# ==============================================================================
CH_MSE_PCT = 0.80  # 80 % des durchschnittlichen Voreinkommens
CH_MSE_MAX_TAGGELD = 220.0  # CHF pro Kalendertag
CH_MSE_MAX_MONATSLOHN = 8250.0  # CHF Monatslohn (8.250 * 0.80 / 30 = 220)
CH_MSE_DAUER_TAGE = 98  # 14 Wochen (98 Kalendertage)

CH_VATERSCHAFT_DAUER_TAGE = 14  # 14 Taggelder bzw. 10 Arbeitstage
CH_VATERSCHAFT_MAX_TAGGELD = 220.0  # CHF pro Tag
