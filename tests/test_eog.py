# -*- coding: utf-8 -*-
"""
Tests für die Schweiz: EOG Mutterschafts- & Vaterschaftsentschädigung 2026.
"""

import pytest
from elterngeld_dach.eog import calculate_eog
from elterngeld_dach.rates import CH_MSE_MAX_TAGGELD, CH_MSE_MAX_MONATSLOHN


def test_eog_deckelung():
    # Hoher Lohn 10.000 CHF (> 8.250 CHF Grenze)
    res = calculate_eog(monatslohn=10000.0)
    assert res.mse_tagessatz == CH_MSE_MAX_TAGGELD
    assert res.mse_tagessatz == 220.0
    assert res.mse_tage == 98
    assert res.mse_gesamt == 220.0 * 98
    assert res.vaterschaft_tagessatz == 220.0
    assert res.vaterschaft_gesamt == 220.0 * 14


def test_eog_unter_deckel():
    # 6.000 CHF Monatslohn:
    # 6.000 / 30 = 200 CHF/Tag * 0.80 = 160.0 CHF/Tag
    res = calculate_eog(monatslohn=6000.0)
    assert res.mse_tagessatz == 160.0
    assert res.mse_gesamt == 160.0 * 98
    assert res.vaterschaft_gesamt == 160.0 * 14


def test_eog_exakte_grenze():
    # Bei exakt 8.250 CHF: 8.250 * 0.80 / 30 = 220.0 CHF
    res = calculate_eog(monatslohn=8250.0)
    assert res.mse_tagessatz == 220.0
