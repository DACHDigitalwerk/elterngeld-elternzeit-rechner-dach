# -*- coding: utf-8 -*-
"""
Datenmodelle und Ergebnisstrukturen für den DACH Elterngeld-,
Mutterschutz- und Elternzeit-Planer 2026.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class BeegResult:
    """Ergebnis der deutschen Elterngeld-Berechnung (§§ 1–4 BEEG)."""
    netto_voreinkommen: float
    ersatzrate: float
    ersatzrate_prozent: float
    is_geringverdiener: bool
    is_degressiv: bool
    basis_elterngeld_brutto: float
    basis_elterngeld: float
    elterngeld_plus: float
    geschwisterbonus: float
    has_geschwisterbonus: bool
    mehrlingszuschlag_basis: float
    mehrlingszuschlag_plus: float
    mehrlinge_count: int
    zve: float
    is_eligible: bool
    ineligibility_reason: Optional[str] = None
    teilzeit_netto: float = 0.0
    teilzeit_stunden: float = 0.0
    is_teilzeit_eligible: bool = True
    mutterschaftsgeld_anrechnung: float = 0.0
    partnerschaftsbonus_moeglich: bool = False
    hinweise: List[str] = field(default_factory=list)


@dataclass
class AtKbgResult:
    """Ergebnis der österreichischen Wochengeld- und KBG-Berechnung."""
    netto_monat: float
    wochengeld_tagessatz: float
    wochengeld_monat: float
    wochengeld_wochen: int
    wochengeld_gesamt: float
    ea_kbg_tagessatz: float
    ea_kbg_monat_30: float
    ea_kbg_max_tage: int
    ea_kbg_gesamt_max: float
    pauschale_tage: int
    pauschale_tagessatz: float
    pauschale_monat_30: float
    pauschale_gesamt: float
    ea_zuverdienstgrenze: float
    pauschale_zuverdienstgrenze: float
    hinweise: List[str] = field(default_factory=list)


@dataclass
class ChEogResult:
    """Ergebnis der Schweizer Mutterschafts- & Vaterschaftsentschädigung (EOG/VAEg)."""
    monatslohn: float
    massgebender_lohn: float
    mse_tagessatz: float
    mse_wochen: int
    mse_tage: int
    mse_gesamt: float
    vaterschaft_tagessatz: float
    vaterschaft_tage: int
    vaterschaft_gesamt: float
    betreuung_tagessatz: float
    betreuung_max_tage: int
    hinweise: List[str] = field(default_factory=list)


@dataclass
class MonthPlanItem:
    """Ein einzelner Monat im 24-Monats-Plan."""
    lebensmonat: int
    elternteil1_modus: str  # 'basis', 'plus', 'partnerbonus', 'arbeit', 'none'
    elternteil1_betrag: float
    elternteil1_stunden: float
    elternteil2_modus: str  # 'basis', 'plus', 'partnerbonus', 'arbeit', 'none'
    elternteil2_betrag: float
    elternteil2_stunden: float
    monatssumme: float
    warnings: List[str] = field(default_factory=list)


@dataclass
class PlanSummary:
    """Gesamtzusammenfassung eines 24-Monats-Elternzeitplans."""
    total_months: int
    total_auszahlung: float
    et1_summe: float
    et2_summe: float
    et1_basis_monate: int
    et1_plus_monate: int
    et1_bonus_monate: int
    et2_basis_monate: int
    et2_plus_monate: int
    et2_bonus_monate: int
    gleichzeitige_basis_monate_jahr1: int
    is_valid_beeg: bool
    violations: List[str] = field(default_factory=list)
    items: List[MonthPlanItem] = field(default_factory=list)
