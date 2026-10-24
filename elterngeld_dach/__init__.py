# -*- coding: utf-8 -*-
"""
DACH Elterngeld-, Mutterschutz- & Elternzeit-Planer 2026 (BEEG, MSchG & Schweizer EO / VAEg).
"""

__version__ = "1.0.0"

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
    AT_EA_KBG_PCT,
    AT_EA_KBG_MAX_TAGESSATZ,
    CH_MSE_PCT,
    CH_MSE_MAX_TAGGELD,
    CH_MSE_MAX_MONATSLOHN,
)
from .models import BeegResult, AtKbgResult, ChEogResult, MonthPlanItem, PlanSummary
from .beeg import calculate_beeg, calculate_ersatzrate
from .kbgg import calculate_kbgg
from .eog import calculate_eog
from .planner import evaluate_plan

__all__ = [
    "calculate_beeg",
    "calculate_ersatzrate",
    "calculate_kbgg",
    "calculate_eog",
    "evaluate_plan",
    "BeegResult",
    "AtKbgResult",
    "ChEogResult",
    "MonthPlanItem",
    "PlanSummary",
]
