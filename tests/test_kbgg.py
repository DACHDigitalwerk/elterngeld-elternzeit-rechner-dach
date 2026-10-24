# -*- coding: utf-8 -*-
"""
Tests für Österreich: Wochengeld & KBG (MSchG / KBGG 2026).
"""

import pytest
from elterngeld_dach.kbgg import calculate_kbgg
from elterngeld_dach.rates import AT_EA_KBG_MAX_TAGESSATZ


def test_wochengeld_standard():
    # 2.500 € Netto mit 17 % Sonderzahlung -> 2.925 € / 30 = 97.50 € Tagessatz
    # 16 Wochen Schutzfrist (8 vor, 8 nach) = 112 Tage
    res = calculate_kbgg(netto_monat=2500.0, ist_kaiserschnitt_oder_mehrling=False)
    assert res.wochengeld_wochen == 16
    assert res.wochengeld_tagessatz == 97.50
    assert res.wochengeld_gesamt == round(97.50 * 112, 2)


def test_wochengeld_kaiserschnitt():
    # 20 Wochen Schutzfrist (8 vor, 12 nach) = 140 Tage
    res = calculate_kbgg(netto_monat=2500.0, ist_kaiserschnitt_oder_mehrling=True)
    assert res.wochengeld_wochen == 20
    assert res.wochengeld_gesamt == round(97.50 * 140, 2)


def test_ea_kbg_deckelung():
    # Hohes Gehalt 4.000 €:
    # 4.000 * 12 / 365 * 0.80 = 105.20 € -> gedeckelt auf 73,88 €
    res = calculate_kbgg(netto_monat=4000.0)
    assert res.ea_kbg_tagessatz == AT_EA_KBG_MAX_TAGESSATZ
    assert res.ea_kbg_tagessatz == 73.88
    assert res.ea_kbg_monat_30 == round(73.88 * 30, 2)


def test_ea_kbg_normal():
    # 1.500 € Netto:
    # 1.500 * 12 / 365 * 0.80 = 39.45 € Tagessatz
    res = calculate_kbgg(netto_monat=1500.0)
    assert res.ea_kbg_tagessatz == 39.45


def test_kbg_konto_pauschale():
    # Kürzeste Variante 365 Tage -> 39,12 €/Tag
    res_short = calculate_kbgg(netto_monat=2000.0, pauschale_tage=365)
    assert res_short.pauschale_tagessatz == 39.12
    assert res_short.pauschale_tage == 365

    # Längste Variante 1063 Tage -> min 16,93 €/Tag
    res_long = calculate_kbgg(netto_monat=2000.0, pauschale_tage=1063)
    assert res_long.pauschale_tagessatz <= 16.93 or res_long.pauschale_tagessatz == 16.93
    assert res_long.pauschale_tage == 1063
