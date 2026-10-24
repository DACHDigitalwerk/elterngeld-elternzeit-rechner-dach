# -*- coding: utf-8 -*-
"""
Berechnungslogik für Elterngeld, Mutterschutz und Elternzeit 2026 im DACH-Raum.
"""

from typing import Dict, Any, Optional
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
    AT_WOCHENGELD_PCT,
    AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_STANDARD,
    AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_MEHRLING_KS,
    AT_EA_KBG_PCT,
    AT_EA_KBG_MAX_TAGESSATZ,
    AT_EA_KBG_ZUVERDIENSTGRENZE,
    AT_KBG_KONTO_MIN_TAGE,
    AT_KBG_KONTO_MAX_TAGE,
    AT_KBG_KONTO_MIN_TAGESSATZ,
    AT_KBG_KONTO_MAX_TAGESSATZ,
    AT_KBG_KONTO_GESAMTBETRAG_EINZEL,
    CH_MSE_PCT,
    CH_MSE_MAX_TAGGELD,
    CH_MSE_DAUER_TAGE,
    CH_VATERSCHAFT_DAUER_TAGE,
    CH_VATERSCHAFT_MAX_TAGGELD,
)


def calculate_de_replacement_rate(net_income: float) -> float:
    """
    Ermittelt die gesetzliche Ersatzrate nach § 2 Abs. 1 und 2 BEEG.
    - Bei Einkommen von 1.000 € bis 1.200 €: 67 %
    - Bei Einkommen < 1.000 € (Geringverdiener): je 2 € unter 1.000 € um 0,1 %-Punkte höher (bis 100 %)
    - Bei Einkommen > 1.200 €: je 20 € über 1.200 € um 0,1 %-Punkte niedriger (bis 65 %)
    """
    if net_income <= 0.0:
        return 0.67

    if net_income < 1000.0:
        # Geringverdiener-Formel
        steps = (1000.0 - net_income) / 2.0
        bonus_pct = steps * 0.001
        return round(min(1.00, 0.67 + bonus_pct), 4)
    elif net_income > 1200.0:
        # Degressive Absenkung auf 65 %
        steps = (net_income - 1200.0) / 20.0
        reduction_pct = steps * 0.001
        return round(max(0.65, 0.67 - reduction_pct), 4)
    else:
        return 0.67


def calculate_germany_elterngeld(
    net_income_before: float,
    part_time_net_during: float = 0.0,
    part_time_hours_per_week: float = 0.0,
    has_qualifying_siblings: bool = False,
    multiple_birth_count: int = 1,
    taxable_yearly_income: float = 0.0,
    maternity_benefit_monthly: float = 0.0,
) -> Dict[str, Any]:
    """
    Berechnet den monatlichen Anspruch auf Basiselterngeld und ElterngeldPlus gem. BEEG.
    """
    eligible = True
    ineligibility_reason = None

    if taxable_yearly_income > DE_EINKOMMENSGRENZE_2026:
        eligible = False
        ineligibility_reason = (
            f"Zu versteuerndes Einkommen ({taxable_yearly_income:,.2f} €) übersteigt die "
            f"gesetzliche Einkommensgrenze 2025/2026 von {DE_EINKOMMENSGRENZE_2026:,.2f} €."
        )

    if part_time_hours_per_week > DE_MAX_TEILZEIT_WOCHENSTUNDEN:
        eligible = False
        ineligibility_reason = (
            f"Geplante Arbeitszeit von {part_time_hours_per_week} Std./Woche übersteigt die "
            f"zulässige Höchstarbeitszeit von {DE_MAX_TEILZEIT_WOCHENSTUNDEN} Std./Woche nach § 1 Abs. 6 BEEG."
        )

    if not eligible:
        return {
            "eligible": False,
            "reason": ineligibility_reason,
            "net_income_before": net_income_before,
            "monthly_basis_elterngeld": 0.0,
            "monthly_plus_elterngeld": 0.0,
        }

    # Einkommensverlust berechnen
    income_loss = max(0.0, net_income_before - part_time_net_during)
    replacement_rate = calculate_de_replacement_rate(net_income_before)

    # Basiselterngeld Grundbetrag
    raw_basis = income_loss * replacement_rate
    clamped_basis = min(DE_MAX_BASIS_ELTERNGELD, max(DE_MIN_BASIS_ELTERNGELD, raw_basis))

    # Geschwisterbonus
    sibling_bonus_basis = 0.0
    sibling_bonus_plus = 0.0
    if has_qualifying_siblings:
        sibling_bonus_basis = max(
            DE_GESCHWISTERBONUS_MIN_BASIS,
            round(clamped_basis * DE_GESCHWISTERBONUS_PCT, 2),
        )
        sibling_bonus_plus = max(
            DE_GESCHWISTERBONUS_MIN_PLUS,
            round(sibling_bonus_basis / 2.0, 2),
        )

    # Mehrlingszuschlag
    additional_multiples = max(0, multiple_birth_count - 1)
    multiples_bonus_basis = additional_multiples * DE_MEHRLINGSZUSCHLAG_BASIS
    multiples_bonus_plus = additional_multiples * DE_MEHRLINGSZUSCHLAG_PLUS

    # Gesamter Anspruch Basiselterngeld
    total_basis = round(clamped_basis + sibling_bonus_basis + multiples_bonus_basis, 2)

    # ElterngeldPlus Deckelung
    # Grundsatz: ElterngeldPlus beträgt maximal die Hälfte des Basiselterngelds ohne Teilzeit
    # aber mindestens 150 € und maximal 900 € (+ Boni)
    raw_plus = round(clamped_basis / 2.0, 2)
    clamped_plus = min(DE_MAX_PLUS_ELTERNGELD, max(DE_MIN_PLUS_ELTERNGELD, raw_plus))
    total_plus = round(clamped_plus + sibling_bonus_plus + multiples_bonus_plus, 2)

    # Mutterschaftsgeld-Anrechnung (für die Lebensmonate während des Mutterschutzes)
    payout_during_mutterschutz = max(0.0, round(total_basis - maternity_benefit_monthly, 2))

    return {
        "eligible": True,
        "net_income_before": round(net_income_before, 2),
        "part_time_net_during": round(part_time_net_during, 2),
        "income_loss": round(income_loss, 2),
        "replacement_rate": replacement_rate,
        "clamped_basis_base": round(clamped_basis, 2),
        "sibling_bonus_basis": sibling_bonus_basis,
        "multiples_bonus_basis": multiples_bonus_basis,
        "monthly_basis_elterngeld": total_basis,
        "clamped_plus_base": round(clamped_plus, 2),
        "sibling_bonus_plus": sibling_bonus_plus,
        "multiples_bonus_plus": multiples_bonus_plus,
        "monthly_plus_elterngeld": total_plus,
        "maternity_benefit_monthly": round(maternity_benefit_monthly, 2),
        "payout_during_mutterschutz": payout_during_mutterschutz,
        "partnership_bonus_eligible": (24.0 <= part_time_hours_per_week <= 32.0),
    }


def calculate_austria_benefits(
    monthly_net_income: float,
    is_caesarean_or_multiples: bool = False,
    selected_kbg_model: str = "earnings_based",  # "earnings_based" oder "account"
    kbg_account_days: int = 365,
) -> Dict[str, Any]:
    """
    Berechnet Wochengeld gem. § 162 ASVG und Kinderbetreuungsgeld (KBG) gem. KBGG in Österreich.
    """
    # Wochengeld: 100% des Nettoeinkommens der letzten 3 Monate + anteilige Sonderzahlungen (ca. 17 %)
    daily_net = (monthly_net_income * 1.17) / 30.0
    protection_weeks = (
        AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_MEHRLING_KS
        if is_caesarean_or_multiples
        else AT_WOCHENGELD_SCHUTZFRIST_WOCHEN_STANDARD
    )
    total_wochengeld = round(daily_net * 7 * protection_weeks, 2)
    monthly_wochengeld_equiv = round(daily_net * 30.0, 2)

    # Kinderbetreuungsgeld
    if selected_kbg_model == "earnings_based":
        # 80 % des täglichen Nettoeinkommens, max. 73,88 €/Tag
        ea_daily = min(AT_EA_KBG_MAX_TAGESSATZ, round(daily_net * AT_EA_KBG_PCT, 2))
        monthly_kbg = round(ea_daily * 30.0, 2)
        total_kbg_single = round(ea_daily * 365, 2)
        total_kbg_both = round(ea_daily * 426, 2)
        additional_income_limit = AT_EA_KBG_ZUVERDIENSTGRENZE
        daily_rate = ea_daily
    else:
        # Pauschales KBG-Konto
        days = max(AT_KBG_KONTO_MIN_TAGE, min(AT_KBG_KONTO_MAX_TAGE, kbg_account_days))
        # Tagesbetrag sinkt mit der Dauer
        daily_rate = round(AT_KBG_KONTO_GESAMTBETRAG_EINZEL / days, 2)
        daily_rate = max(AT_KBG_KONTO_MIN_TAGESSATZ, min(AT_KBG_KONTO_MAX_TAGESSATZ, daily_rate))
        monthly_kbg = round(daily_rate * 30.0, 2)
        total_kbg_single = round(daily_rate * days, 2)
        total_kbg_both = round(total_kbg_single * 1.25, 2)
        additional_income_limit = max(18000.0, monthly_net_income * 12 * 0.60)

    return {
        "monthly_net_income": round(monthly_net_income, 2),
        "wochengeld_daily": round(daily_net, 2),
        "wochengeld_monthly_equiv": monthly_wochengeld_equiv,
        "wochengeld_protection_weeks": protection_weeks,
        "wochengeld_total": total_wochengeld,
        "kbg_model": selected_kbg_model,
        "kbg_daily_rate": daily_rate,
        "kbg_monthly": monthly_kbg,
        "kbg_total_single": total_kbg_single,
        "kbg_total_both": total_kbg_both,
        "kbg_additional_income_limit": round(additional_income_limit, 2),
    }


def calculate_switzerland_benefits(
    monthly_gross_salary: float,
) -> Dict[str, Any]:
    """
    Berechnet die Mutterschaftsentschädigung (MSE) und Vaterschaftsentschädigung nach EOG / VAEg.
    """
    daily_wage = monthly_gross_salary / 30.0
    raw_daily_benefit = daily_wage * CH_MSE_PCT
    daily_mse = min(CH_MSE_MAX_TAGGELD, round(raw_daily_benefit, 2))

    total_mse = round(daily_mse * CH_MSE_DAUER_TAGE, 2)
    monthly_mse_equiv = round(daily_mse * 30.0, 2)

    total_paternity = round(daily_mse * CH_VATERSCHAFT_DAUER_TAGE, 2)

    capped = raw_daily_benefit > CH_MSE_MAX_TAGGELD

    return {
        "monthly_gross_salary": round(monthly_gross_salary, 2),
        "daily_wage": round(daily_wage, 2),
        "replacement_rate": CH_MSE_PCT,
        "daily_mse": daily_mse,
        "is_capped": capped,
        "cap_limit_daily": CH_MSE_MAX_TAGGELD,
        "monthly_mse_equivalent": monthly_mse_equiv,
        "mse_duration_days": CH_MSE_DAUER_TAGE,
        "mse_total_payout": total_mse,
        "paternity_duration_days": CH_VATERSCHAFT_DAUER_TAGE,
        "paternity_total_payout": total_paternity,
    }
