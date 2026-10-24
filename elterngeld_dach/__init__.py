# -*- coding: utf-8 -*-
"""
DACH Elterngeld-, Mutterschutz- & Elternzeit-Rechner 2026.
Berechnungsmodelle für Deutschland (BEEG), Österreich (MSchG/KBGG) und die Schweiz (EOG/VAEg).
"""

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"

from .calculator import (
    calculate_germany_elterngeld,
    calculate_austria_benefits,
    calculate_switzerland_benefits,
    calculate_de_replacement_rate,
)
from .rates import (
    DE_MIN_BASIS_ELTERNGELD,
    DE_MAX_BASIS_ELTERNGELD,
    DE_MIN_PLUS_ELTERNGELD,
    DE_MAX_PLUS_ELTERNGELD,
    DE_EINKOMMENSGRENZE_2026,
    AT_EA_KBG_MAX_TAGESSATZ,
    CH_MSE_MAX_TAGGELD,
)

__all__ = [
    "calculate_germany_elterngeld",
    "calculate_austria_benefits",
    "calculate_switzerland_benefits",
    "calculate_de_replacement_rate",
    "DE_MIN_BASIS_ELTERNGELD",
    "DE_MAX_BASIS_ELTERNGELD",
    "DE_MIN_PLUS_ELTERNGELD",
    "DE_MAX_PLUS_ELTERNGELD",
    "DE_EINKOMMENSGRENZE_2026",
    "AT_EA_KBG_MAX_TAGESSATZ",
    "CH_MSE_MAX_TAGGELD",
]
