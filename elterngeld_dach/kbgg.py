# -*- coding: utf-8 -*-
"""
Berechnungsmodul für das österreichische Mutterschutzgesetz (MSchG)
und Kinderbetreuungsgeldgesetz (KBGG) 2026.
"""

from typing import List, Optional
from .rates import (
    AT_WOCHENGELD_PCT,
    AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_STANDARD,
    AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_MEHRLING_KS,
    AT_EA_KBG_PCT,
    AT_EA_KBG_MAX_TAGESSATZ,
    AT_EA_KBG_MAX_TAGE_EINZEL,
    AT_EA_KBG_MAX_TAGE_BEIDE,
    AT_EA_KBG_ZUVERDIENSTGRENZE,
    AT_KBG_KONTO_GESAMTBETRAG_EINZEL,
    AT_KBG_KONTO_MIN_TAGE,
    AT_KBG_KONTO_MAX_TAGE,
    AT_KBG_KONTO_MIN_TAGESSATZ,
    AT_KBG_KONTO_MAX_TAGESSATZ,
)
from .models import AtKbgResult


def calculate_kbgg(
    netto_monat: float,
    ist_kaiserschnitt_oder_mehrling: bool = False,
    pauschale_tage: int = 365,
    beide_eltern: bool = False,
    inkl_sonderzahlungen: bool = True,
) -> AtKbgResult:
    """
    Berechnet Wochengeld und KBG nach österreichischem Recht (2026).
    
    1. Wochengeld (§ 162 ASVG):
       - 100 % des durchschnittlichen Nettoentgelts der letzten 3 Monate vor Mutterschutz.
       - Zzgl. Sonderzahlungszuschlag (i.d.R. ca. 17 % für 13./14. Monatsgehalt).
       - Dauer: 8 Wochen vor der Geburt + 8 Wochen danach (Standard) oder 12 Wochen (Kaiserschnitt/Mehrlinge).
    
    2. Einkommensabhängiges Kinderbetreuungsgeld (ea KBG):
       - 80 % des Letztgehalts (Erwerbseinkommen der letzten 6 Monate).
       - Gedeckelt auf max. 73,88 € pro Kalendertag (im Jahr 2026).
       - Dauer: bis zu 365 Tage (1 Elternteil) bzw. 426 Tage (beide Eltern).
    
    3. Pauschales KBG-Konto:
       - Flexibel zwischen 365 und 1.063 Tagen wählbar.
       - Tagessatz staffelt sich von 16,93 € bis 39,12 €/Tag.
    """
    hinweise: List[str] = []

    # 1. Wochengeld
    # Netto inkl. Sonderzahlungen: 100% Netto + 17% SZ-Zuschlag, wenn inkl_sonderzahlungen
    sz_faktor = 1.17 if inkl_sonderzahlungen else 1.00
    monat_mit_sz = netto_monat * sz_faktor
    wochengeld_tagessatz = round(monat_mit_sz / 30.0, 2)
    wochengeld_monat = round(wochengeld_tagessatz * 30.0, 2)

    wochen_nach = 12 if ist_kaiserschnitt_oder_mehrling else 8
    wochen_schutz = 8 + wochen_nach
    wochengeld_gesamt = round(wochengeld_tagessatz * (wochen_schutz * 7), 2)

    hinweise.append(
        f"Wochengeld: {wochen_schutz} Wochen Schutzfrist ({8} Wochen vor + {wochen_nach} Wochen nach Geburt). "
        f"Tagessatz: {wochengeld_tagessatz:.2f} € (inkl. 13./14. Gehaltsaufschlag)."
    )

    # 2. Einkommensabhängiges KBG
    # 80 % des Nettoentgelts (auf den Tag gerechnet)
    # Gesetzliche Berechnungsformel: Netto monatlich * 12 / 365 * 0.80
    raw_ea_tagessatz = (netto_monat * 12.0 / 365.0) * AT_EA_KBG_PCT
    ea_tagessatz = min(AT_EA_KBG_MAX_TAGESSATZ, max(0.0, raw_ea_tagessatz))
    ea_tagessatz = round(ea_tagessatz, 2)
    ea_monat_30 = round(ea_tagessatz * 30.0, 2)

    ea_max_tage = AT_EA_KBG_MAX_TAGE_BEIDE if beide_eltern else AT_EA_KBG_MAX_TAGE_EINZEL
    ea_gesamt_max = round(ea_tagessatz * ea_max_tage, 2)

    if raw_ea_tagessatz > AT_EA_KBG_MAX_TAGESSATZ:
        hinweise.append(
            f"Ea KBG erreicht den gesetzlichen Höchstsatz 2026 von {AT_EA_KBG_MAX_TAGESSATZ:.2f} €/Tag "
            f"(~ {ea_monat_30:.2f} € / Monat)."
        )

    # 3. Pauschales KBG-Konto
    clamped_tage = min(AT_KBG_KONTO_MAX_TAGE, max(AT_KBG_KONTO_MIN_TAGE, pauschale_tage))
    
    # Tagessatz-Interpolation:
    # 365 Tage -> 39.12 €/Tag
    # 1063 Tage -> 16.93 €/Tag
    # Formel: Gesamtsumme für Einzelbezieher ist ca. 14.355,20 €
    # Tagessatz = 14355.20 / Tage, geklemmt auf min 16.93 und max 39.12
    raw_pauschale_tagessatz = AT_KBG_KONTO_GESAMTBETRAG_EINZEL / clamped_tage
    pauschale_tagessatz = min(AT_KBG_KONTO_MAX_TAGESSATZ, max(AT_KBG_KONTO_MIN_TAGESSATZ, raw_pauschale_tagessatz))
    pauschale_tagessatz = round(pauschale_tagessatz, 2)
    pauschale_monat_30 = round(pauschale_tagessatz * 30.0, 2)
    pauschale_gesamt = round(pauschale_tagessatz * clamped_tage, 2)

    return AtKbgResult(
        netto_monat=netto_monat,
        wochengeld_tagessatz=wochengeld_tagessatz,
        wochengeld_monat=wochengeld_monat,
        wochengeld_wochen=wochen_schutz,
        wochengeld_gesamt=wochengeld_gesamt,
        ea_kbg_tagessatz=ea_tagessatz,
        ea_kbg_monat_30=ea_monat_30,
        ea_kbg_max_tage=ea_max_tage,
        ea_kbg_gesamt_max=ea_gesamt_max,
        pauschale_tage=clamped_tage,
        pauschale_tagessatz=pauschale_tagessatz,
        pauschale_monat_30=pauschale_monat_30,
        pauschale_gesamt=pauschale_gesamt,
        ea_zuverdienstgrenze=AT_EA_KBG_ZUVERDIENSTGRENZE,
        pauschale_zuverdienstgrenze=18000.0,
        hinweise=hinweise,
    )
