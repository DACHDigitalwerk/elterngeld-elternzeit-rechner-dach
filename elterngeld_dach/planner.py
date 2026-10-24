# -*- coding: utf-8 -*-
"""
Planungs- und Validierungsmodul für den 24-Monats-Elternzeitplaner (BEEG 2026).
"""

from typing import List, Dict, Any, Optional
from .models import MonthPlanItem, PlanSummary
from .beeg import calculate_beeg


def evaluate_plan(
    et1_netto: float,
    et2_netto: float,
    et1_months: List[str],  # 24 strings: 'basis', 'plus', 'partnerbonus', 'arbeit'
    et2_months: List[str],  # 24 strings: 'basis', 'plus', 'partnerbonus', 'arbeit'
    et1_hours: Optional[List[float]] = None,
    et2_hours: Optional[List[float]] = None,
    et1_zve: float = 0.0,
    et2_zve: float = 0.0,
    has_geschwisterbonus: bool = False,
    mehrlinge_count: int = 1,
) -> PlanSummary:
    """
    Simuliert und validiert einen vollständigen 24-Monats-Bezugsplan für beide Elternteile.
    """
    if et1_hours is None:
        et1_hours = [0.0] * 24
    if et2_hours is None:
        et2_hours = [0.0] * 24

    # Standard-Ergebnisse für Vollbezug ohne Teilzeit
    res1_full = calculate_beeg(et1_netto, zve=et1_zve, has_geschwisterbonus=has_geschwisterbonus, mehrlinge_count=mehrlinge_count)
    res2_full = calculate_beeg(et2_netto, zve=et2_zve, has_geschwisterbonus=has_geschwisterbonus, mehrlinge_count=mehrlinge_count)

    items: List[MonthPlanItem] = []
    violations: List[str] = []

    et1_basis_count = 0
    et1_plus_count = 0
    et1_bonus_count = 0

    et2_basis_count = 0
    et2_plus_count = 0
    et2_bonus_count = 0

    gleichzeitige_basis_monate_jahr1 = 0
    total_auszahlung = 0.0
    et1_summe = 0.0
    et2_summe = 0.0

    for m in range(24):
        month_num = m + 1
        mode1 = et1_months[m] if m < len(et1_months) else 'arbeit'
        mode2 = et2_months[m] if m < len(et2_months) else 'arbeit'
        h1 = et1_hours[m] if m < len(et1_hours) else 0.0
        h2 = et2_hours[m] if m < len(et2_hours) else 0.0

        amt1 = 0.0
        amt2 = 0.0
        warnings: List[str] = []

        # Elternteil 1
        if mode1 == 'basis':
            et1_basis_count += 1
            amt1 = res1_full.basis_elterngeld
            if h1 > 32.0:
                warnings.append(f"ET1: {h1} h/Woche überschreitet 32h-Limit im Basiselterngeld (M{month_num})")
        elif mode1 == 'plus':
            et1_plus_count += 1
            amt1 = res1_full.elterngeld_plus
            if h1 > 32.0:
                warnings.append(f"ET1: {h1} h/Woche überschreitet 32h-Limit im ElterngeldPlus (M{month_num})")
        elif mode1 == 'partnerbonus':
            et1_bonus_count += 1
            amt1 = res1_full.elterngeld_plus
            if h1 < 24.0 or h1 > 32.0:
                warnings.append(f"ET1: Partnerschaftsbonus erfordert 24–32 h/Woche (aktuell {h1} h in M{month_num})")

        # Elternteil 2
        if mode2 == 'basis':
            et2_basis_count += 1
            amt2 = res2_full.basis_elterngeld
            if h2 > 32.0:
                warnings.append(f"ET2: {h2} h/Woche überschreitet 32h-Limit im Basiselterngeld (M{month_num})")
        elif mode2 == 'plus':
            et2_plus_count += 1
            amt2 = res2_full.elterngeld_plus
            if h2 > 32.0:
                warnings.append(f"ET2: {h2} h/Woche überschreitet 32h-Limit im ElterngeldPlus (M{month_num})")
        elif mode2 == 'partnerbonus':
            et2_bonus_count += 1
            amt2 = res2_full.elterngeld_plus
            if h2 < 24.0 or h2 > 32.0:
                warnings.append(f"ET2: Partnerschaftsbonus erfordert 24–32 h/Woche (aktuell {h2} h in M{month_num})")

        # Gleichzeitiger Basiselterngeldbezug im ersten Lebensjahr (§ 4 Abs. 6 BEEG)
        if month_num <= 12 and mode1 == 'basis' and mode2 == 'basis':
            gleichzeitige_basis_monate_jahr1 += 1
            if gleichzeitige_basis_monate_jahr1 > 1:
                warnings.append(
                    f"Verstoß BEEG 2026: Gleichzeitiger Basiselterngeld-Bezug ist im 1. Lebensjahr "
                    f"nur für maximal 1 Monat zulässig (M{month_num} ist der {gleichzeitige_basis_monate_jahr1}. gleichzeitige Monat)!"
                )

        month_sum = amt1 + amt2
        total_auszahlung += month_sum
        et1_summe += amt1
        et2_summe += amt2

        items.append(MonthPlanItem(
            lebensmonat=month_num,
            elternteil1_modus=mode1,
            elternteil1_betrag=round(amt1, 2),
            elternteil1_stunden=h1,
            elternteil2_modus=mode2,
            elternteil2_betrag=round(amt2, 2),
            elternteil2_stunden=h2,
            monatssumme=round(month_sum, 2),
            warnings=warnings,
        ))

    # Gesetzliche Gesamtkontingente prüfen:
    # 1 Basismonat = 1 Monatsäquivalent
    # 1 Plusmonat = 0.5 Monatsäquivalent
    et1_equiv = et1_basis_count + (et1_plus_count * 0.5)
    et2_equiv = et2_basis_count + (et2_plus_count * 0.5)
    total_equiv = et1_equiv + et2_equiv

    # Maximal 14 Basismonats-Äquivalente für Paare (wenn beide mind. 2 Monate nehmen)
    if total_equiv > 14.0:
        violations.append(
            f"Das Gesamtanspruchskontingent von maximal 14 Basismonaten ist überschritten "
            f"(aktuell: {total_equiv:.1f} Monatsäquivalente geplant)."
        )

    # Mindestens 2 Partnermonate pro Elternteil bei Inanspruchnahme von 14 Monaten
    if total_equiv > 12.0 and (et1_equiv < 2.0 or et2_equiv < 2.0):
        violations.append(
            "Für den vollen 14-Monats-Anspruch muss jeder Elternteil mindestens 2 Partnermonate beziehen."
        )

    # Gleichzeitigkeit
    if gleichzeitige_basis_monate_jahr1 > 1:
        violations.append(
            f"Gleichzeitiger Basiselterngeld-Bezug im 1. Lebensjahr für {gleichzeitige_basis_monate_jahr1} Monate "
            f"geplant (maximal 1 Monat gesetzlich erlaubt)."
        )

    # Partnerschaftsbonus (muss 2 bis 4 aufeinanderfolgende Monate für BEIDE Eltern gleichzeitig sein)
    if (et1_bonus_count > 0 or et2_bonus_count > 0):
        if et1_bonus_count != et2_bonus_count or et1_bonus_count < 2 or et1_bonus_count > 4:
            violations.append(
                f"Der Partnerschaftsbonus muss für beide Elternteile synchron für 2 bis 4 Monate beantragt werden "
                f"(ET1: {et1_bonus_count} M, ET2: {et2_bonus_count} M)."
            )

    is_valid_beeg = len(violations) == 0

    return PlanSummary(
        total_months=24,
        total_auszahlung=round(total_auszahlung, 2),
        et1_summe=round(et1_summe, 2),
        et2_summe=round(et2_summe, 2),
        et1_basis_monate=et1_basis_count,
        et1_plus_monate=et1_plus_count,
        et1_bonus_monate=et1_bonus_count,
        et2_basis_monate=et2_basis_count,
        et2_plus_monate=et2_plus_count,
        et2_bonus_monate=et2_bonus_count,
        gleichzeitige_basis_monate_jahr1=gleichzeitige_basis_monate_jahr1,
        is_valid_beeg=is_valid_beeg,
        violations=violations,
        items=items,
    )
