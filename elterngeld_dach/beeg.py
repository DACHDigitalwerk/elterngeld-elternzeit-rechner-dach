# -*- coding: utf-8 -*-
"""
Berechnungsmodul für das deutsche Bundeselterngeld- und
Elternzeitgesetz (BEEG) 2026.
"""

import math
from typing import Optional, List
from .rates import (
    DE_MIN_BASIS_ELTERNGELD,
    DE_MAX_BASIS_ELTERNGELD,
    DE_MIN_PLUS_ELTERNGELD,
    DE_MAX_PLUS_ELTERNGELD,
    DE_GESCHWISTERBONUS_PCT,
    DE_GESCHWISTERBONUS_MIN_BASIS,
    DE_GESCHWISTERBONUS_MIN_PLUS,
    DE_MEHRLINGSZUSCHLAG_BASIS,
    DE_MEHRLINGSZUSCHLAG_PLUS,
    DE_EINKOMMENSGRENZE_2026,
    DE_MAX_TEILZEIT_WOCHENSTUNDEN,
)
from .models import BeegResult


def calculate_ersatzrate(netto: float) -> float:
    """
    Berechnet die gesetzliche Ersatzrate nach § 2 Abs. 1 und Abs. 2 BEEG.
    
    Regeln:
    - Bei Netto < 1.000 €: Geringverdiener-Bonus (+0,1 %-Punkte je 2 € unter 1.000 € bis max 100 %)
    - Bei Netto zwischen 1.000 € und 1.200 €: Genau 67 %
    - Bei Netto > 1.200 €: Degressive Absenkung (-0,1 %-Punkte je 20 € über 1.200 € bis min 65 %)
    """
    if netto <= 0:
        return 1.00

    if netto < 1000.0:
        # § 2 Abs. 2 BEEG: je 2 Euro unter 1.000 € um 0,1 Prozentpunkte höher
        diff = 1000.0 - netto
        steps = diff / 2.0
        rate = 0.67 + (steps * 0.001)
        return min(1.00, round(rate, 4))
    
    if netto <= 1200.0:
        return 0.67

    # § 2 Abs. 1 BEEG: je 20 Euro über 1.200 € um 0,1 Prozentpunkte niedriger bis 65 %
    diff = netto - 1200.0
    steps = int(diff / 20.0)
    rate = 0.67 - (steps * 0.001)
    return max(0.65, round(rate, 4))


def calculate_beeg(
    netto_voreinkommen: float,
    zve: float = 0.0,
    has_geschwisterbonus: bool = False,
    mehrlinge_count: int = 1,
    teilzeit_netto: float = 0.0,
    teilzeit_stunden: float = 0.0,
    mutterschaftsgeld_tagessatz: float = 0.0,
    ist_mutter: bool = False,
) -> BeegResult:
    """
    Berechnet das Elterngeld nach deutschem Recht (§§ 1–4 BEEG 2026).
    """
    hinweise: List[str] = []
    
    # 1. Einkommensgrenzen-Prüfung (§ 1 Abs. 8 BEEG 2025/2026: 175.000 € zvE)
    if zve > DE_EINKOMMENSGRENZE_2026:
        reason = (
            f"Das zu versteuernde Einkommen (zvE) von {zve:,.2f} € übersteigt die "
            f"gesetzliche Obergrenze von {DE_EINKOMMENSGRENZE_2026:,.2f} € (§ 1 Abs. 8 BEEG)."
        )
        hinweise.append(reason)
        return BeegResult(
            netto_voreinkommen=netto_voreinkommen,
            ersatzrate=0.0,
            ersatzrate_prozent=0.0,
            is_geringverdiener=False,
            is_degressiv=False,
            basis_elterngeld_brutto=0.0,
            basis_elterngeld=0.0,
            elterngeld_plus=0.0,
            geschwisterbonus=0.0,
            has_geschwisterbonus=has_geschwisterbonus,
            mehrlingszuschlag_basis=0.0,
            mehrlingszuschlag_plus=0.0,
            mehrlinge_count=mehrlinge_count,
            zve=zve,
            is_eligible=False,
            ineligibility_reason=reason,
            teilzeit_netto=teilzeit_netto,
            teilzeit_stunden=teilzeit_stunden,
            is_teilzeit_eligible=True,
            hinweise=hinweise,
        )

    # 2. Teilzeit-Wochenstunden Check (§ 1 Abs. 6 BEEG: max 32h/Woche)
    is_teilzeit_eligible = True
    if teilzeit_stunden > DE_MAX_TEILZEIT_WOCHENSTUNDEN:
        is_teilzeit_eligible = False
        hinweise.append(
            f"Achtung: {teilzeit_stunden} Wochenstunden überschreiten die gesetzliche "
            f"Höchstgrenze von {DE_MAX_TEILZEIT_WOCHENSTUNDEN} h/Woche (§ 1 Abs. 6 BEEG). "
            f"In diesem Monat entfällt der Elterngeldanspruch!"
        )

    # 3. Ersatzrate ermitteln
    ersatzrate = calculate_ersatzrate(netto_voreinkommen)
    ersatzrate_prozent = round(ersatzrate * 100.0, 2)
    is_geringverdiener = netto_voreinkommen < 1000.0 and netto_voreinkommen > 0
    is_degressiv = netto_voreinkommen > 1200.0

    # 4. Basiselterngeld vor Zuschlägen
    # Ohne Teilzeit:
    raw_basis = netto_voreinkommen * ersatzrate
    basis_nominal = min(DE_MAX_BASIS_ELTERNGELD, max(DE_MIN_BASIS_ELTERNGELD, raw_basis))

    # Mit Teilzeit-Zuverdienst:
    if teilzeit_netto > 0 and is_teilzeit_eligible:
        einkommensverlust = max(0.0, netto_voreinkommen - teilzeit_netto)
        raw_basis_tz = einkommensverlust * ersatzrate
        basis_mit_tz = min(DE_MAX_BASIS_ELTERNGELD, max(DE_MIN_BASIS_ELTERNGELD, raw_basis_tz))
    else:
        basis_mit_tz = basis_nominal

    # 5. ElterngeldPlus berechnen
    # Gesetzliche Formel: Deckelungsbetrag ist die Hälfte des Basiselterngelds ohne Teilzeit!
    deckelungsbetrag = round(basis_nominal / 2.0, 2)
    if teilzeit_netto > 0 and is_teilzeit_eligible:
        einkommensverlust = max(0.0, netto_voreinkommen - teilzeit_netto)
        plus_vor_deckelung = max(DE_MIN_PLUS_ELTERNGELD, einkommensverlust * ersatzrate)
        plus_nominal = min(deckelungsbetrag, plus_vor_deckelung)
    else:
        plus_nominal = deckelungsbetrag

    # 6. Geschwisterbonus (§ 2a BEEG)
    # +10 %, mindestens 75 € (Basis) bzw. 37,50 € (Plus)
    bonus_basis = 0.0
    bonus_plus = 0.0
    if has_geschwisterbonus:
        bonus_basis = max(DE_GESCHWISTERBONUS_MIN_BASIS, round(basis_mit_tz * DE_GESCHWISTERBONUS_PCT, 2))
        bonus_plus = max(DE_GESCHWISTERBONUS_MIN_PLUS, round(plus_nominal * DE_GESCHWISTERBONUS_PCT, 2))
        hinweise.append(
            f"Geschwisterbonus aktiv: +{bonus_basis:.2f} € / Monat auf Basis bzw. "
            f"+{bonus_plus:.2f} € / Monat auf ElterngeldPlus."
        )

    # 7. Mehrlingszuschlag (§ 2a Abs. 4 BEEG)
    # +300 € Basis bzw. +150 € Plus je weiterem Mehrling
    additional_twins = max(0, mehrlinge_count - 1)
    mehrlingszuschlag_basis = additional_twins * DE_MEHRLINGSZUSCHLAG_BASIS
    mehrlingszuschlag_plus = additional_twins * DE_MEHRLINGSZUSCHLAG_PLUS
    if additional_twins > 0:
        hinweise.append(
            f"Mehrlingszuschlag für {additional_twins} weitere(s) Kind(er): "
            f"+{mehrlingszuschlag_basis:.2f} € / Monat (Basis) bzw. "
            f"+{mehrlingszuschlag_plus:.2f} € / Monat (Plus)."
        )

    # Finale Beträge
    final_basis = round(basis_mit_tz + bonus_basis + mehrlingszuschlag_basis, 2)
    final_plus = round(plus_nominal + bonus_plus + mehrlingszuschlag_plus, 2)

    # 8. Mutterschaftsgeld-Anrechnung prüfen (§ 3 BEEG)
    anrechnung_betrag = 0.0
    if ist_mutter and mutterschaftsgeld_tagessatz > 0:
        monatliches_muschgeld = round(mutterschaftsgeld_tagessatz * 30.0, 2)
        anrechnung_betrag = monatliches_muschgeld
        hinweise.append(
            f"Mutterschaftsgeld-Anrechnung: In den Lebensmonaten 1–2 nach der Geburt "
            f"wird das Mutterschaftsgeld ({monatliches_muschgeld:.2f} €/Monat) voll angerechnet. "
            f"Das Basiselterngeld ruht bzw. wird bis auf 0 € verrechnet, verbraucht aber die Anspruchsmonate."
        )

    # 9. Partnerschaftsbonus-Option prüfen (§ 4b BEEG)
    # Möglich bei gleichzeitiger Teilzeit comply 24–32 h/Woche
    partnerschaftsbonus_moeglich = (24.0 <= teilzeit_stunden <= 32.0)

    return BeegResult(
        netto_voreinkommen=netto_voreinkommen,
        ersatzrate=ersatzrate,
        ersatzrate_prozent=ersatzrate_prozent,
        is_geringverdiener=is_geringverdiener,
        is_degressiv=is_degressiv,
        basis_elterngeld_brutto=round(raw_basis, 2),
        basis_elterngeld=final_basis if is_teilzeit_eligible else 0.0,
        elterngeld_plus=final_plus if is_teilzeit_eligible else 0.0,
        geschwisterbonus=bonus_basis,
        has_geschwisterbonus=has_geschwisterbonus,
        mehrlingszuschlag_basis=mehrlingszuschlag_basis,
        mehrlingszuschlag_plus=mehrlingszuschlag_plus,
        mehrlinge_count=mehrlinge_count,
        zve=zve,
        is_eligible=True,
        teilzeit_netto=teilzeit_netto,
        teilzeit_stunden=teilzeit_stunden,
        is_teilzeit_eligible=is_teilzeit_eligible,
        mutterschaftsgeld_anrechnung=anrechnung_betrag,
        partnerschaftsbonus_moeglich=partnerschaftsbonus_moeglich,
        hinweise=hinweise,
    )
