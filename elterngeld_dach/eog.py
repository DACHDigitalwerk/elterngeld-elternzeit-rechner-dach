# -*- coding: utf-8 -*-
"""
Berechnungsmodul für die Schweizer Erwerbsersatzordnung (EOG)
und das Vaterschaftsentschädigungsgesetz (VAEg) 2026.
"""

from typing import List
from .rates import (
    CH_MSE_PCT,
    CH_MSE_MAX_TAGGELD,
    CH_MSE_MAX_MONATSLOHN,
    CH_MSE_DAUER_TAGE,
    CH_VATERSCHAFT_DAUER_TAGE,
    CH_VATERSCHAFT_MAX_TAGGELD,
)
from .models import ChEogResult


def calculate_eog(monatslohn: float) -> ChEogResult:
    """
    Berechnet Mutterschafts- und Vaterschaftsentschädigung nach Schweizer EOG/VAEg.
    
    1. Mutterschaftsentschädigung (MSE):
       - 80 % des durchschnittlichen Voreinkommens.
       - Maximal 220 CHF pro Kalendertag (Erreicht bei 8.250 CHF Monatslohn: 8.250 * 0.8 / 30 = 220).
       - Dauer: 14 Wochen = 98 Kalendertage.
    
    2. Urlaub für den anderen Elternteil / Vaterschaftsurlaub:
       - 80 % des Voreinkommens, max. 220 CHF pro Tag.
       - Dauer: 2 Wochen = 14 Taggelder (bzw. 10 bezahlte Arbeitstage).
    
    3. Betreuungsentschädigung (Art. 16n ff. EOG):
       - Bis zu 14 Wochen (98 Taggelder) bei schwer beeinträchtigten Kindern.
    """
    hinweise: List[str] = []

    massgebender_lohn = min(CH_MSE_MAX_MONATSLOHN, max(0.0, monatslohn))
    if monatslohn > CH_MSE_MAX_MONATSLOHN:
        hinweise.append(
            f"Der Monatslohn ({monatslohn:,.2f} CHF) liegt über dem Höchstbetrag "
            f"von {CH_MSE_MAX_MONATSLOHN:,.2f} CHF. Die Entschädigung wird auf das "
            f"gesetzliche Maximum von {CH_MSE_MAX_TAGGELD:.2f} CHF/Tag gekappt."
        )

    # Tagessatz: Monatslohn / 30 * 80 %
    raw_tagessatz = (monatslohn / 30.0) * CH_MSE_PCT
    mse_tagessatz = min(CH_MSE_MAX_TAGGELD, max(0.0, raw_tagessatz))
    mse_tagessatz = round(mse_tagessatz, 2)

    mse_wochen = 14
    mse_tage = CH_MSE_DAUER_TAGE
    mse_gesamt = round(mse_tagessatz * mse_tage, 2)

    vaterschaft_tage = CH_VATERSCHAFT_DAUER_TAGE
    vaterschaft_tagessatz = mse_tagessatz
    vaterschaft_gesamt = round(vaterschaft_tagessatz * vaterschaft_tage, 2)

    betreuung_tagessatz = mse_tagessatz
    betreuung_max_tage = 98

    hinweise.append(
        f"Mutterschaftsurlaub (14 Wochen / 98 Tage): Gesamtentschädigung {mse_gesamt:,.2f} CHF."
    )
    hinweise.append(
        f"Vaterschaftsurlaub (2 Wochen / 14 Taggelder = 10 Arbeitstage): Gesamtentschädigung {vaterschaft_gesamt:,.2f} CHF."
    )

    return ChEogResult(
        monatslohn=monatslohn,
        massgebender_lohn=massgebender_lohn,
        mse_tagessatz=mse_tagessatz,
        mse_wochen=mse_wochen,
        mse_tage=mse_tage,
        mse_gesamt=mse_gesamt,
        vaterschaft_tagessatz=vaterschaft_tagessatz,
        vaterschaft_tage=vaterschaft_tage,
        vaterschaft_gesamt=vaterschaft_gesamt,
        betreuung_tagessatz=betreuung_tagessatz,
        betreuung_max_tage=betreuung_max_tage,
        hinweise=hinweise,
    )
