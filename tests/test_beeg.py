# -*- coding: utf-8 -*-
"""
Tests für das deutsche Elterngeld (BEEG 2026).
"""

import pytest
from elterngeld_dach.beeg import calculate_beeg, calculate_ersatzrate
from elterngeld_dach.rates import DE_EINKOMMENSGRENZE_2026


def test_ersatzrate_standard():
    # Zwischen 1000 und 1200 Euro: Exakt 67 %
    assert calculate_ersatzrate(1000.0) == 0.67
    assert calculate_ersatzrate(1100.0) == 0.67
    assert calculate_ersatzrate(1200.0) == 0.67


def test_ersatzrate_geringverdiener():
    # Je 2 € unter 1.000 €: +0,1 %-Punkte
    # 800 €: 200 € drunter / 2 = 100 Schritte * 0.001 = +0.10 -> 0.77 (77%)
    assert calculate_ersatzrate(800.0) == 0.77
    # 500 €: 500 € drunter / 2 = 250 Schritte * 0.001 = +0.25 -> 0.92 (92%)
    assert calculate_ersatzrate(500.0) == 0.92
    # 340 €: 660 € drunter / 2 = 330 Schritte * 0.001 = +0.33 -> 1.00 (100%)
    assert calculate_ersatzrate(340.0) == 1.00
    # 200 €: max 1.00
    assert calculate_ersatzrate(200.0) == 1.00


def test_ersatzrate_degressiv():
    # Je 20 € über 1.200 €: -0,1 %-Punkte bis 65 %
    # 1220 €: 1 Schritt * 0.001 -> 0.669
    assert calculate_ersatzrate(1220.0) == 0.669
    # 1240 €: 2 Schritte -> 0.668
    assert calculate_ersatzrate(1240.0) == 0.668
    # 1600 €: 400 / 20 = 20 Schritte * 0.001 = 0.02 -> 0.65
    assert calculate_ersatzrate(1600.0) == 0.65
    # 2500 €: gedeckelt auf min 0.65
    assert calculate_ersatzrate(2500.0) == 0.65


def test_basiselterngeld_sockel_und_kappung():
    # Mindestbetrag 300 €
    res_min = calculate_beeg(netto_voreinkommen=0.0)
    assert res_min.basis_elterngeld == 300.0
    assert res_min.elterngeld_plus == 150.0

    # Höchstbetrag 1.800 € (bei hohem Netto)
    res_max = calculate_beeg(netto_voreinkommen=4000.0)
    assert res_max.basis_elterngeld == 1800.0
    assert res_max.elterngeld_plus == 900.0


def test_einkommensgrenze_zve_175k():
    # Über 175.000 €: Kein Anspruch
    res_over = calculate_beeg(netto_voreinkommen=5000.0, zve=175001.0)
    assert not res_over.is_eligible
    assert res_over.basis_elterngeld == 0.0
    assert res_over.elterngeld_plus == 0.0
    assert "175" in res_over.ineligibility_reason

    # Bei 175.000 €: Berechtigt
    res_ok = calculate_beeg(netto_voreinkommen=3000.0, zve=175000.0)
    assert res_ok.is_eligible
    assert res_ok.basis_elterngeld > 0.0


def test_geschwisterbonus():
    # Netto 2.000 € -> 65 % = 1.300 € Basis
    # Geschwisterbonus: +10 % = 130 €
    res = calculate_beeg(netto_voreinkommen=2000.0, has_geschwisterbonus=True)
    assert res.geschwisterbonus == 130.0
    assert res.basis_elterngeld == 1430.0

    # Mindestbonus 75 € bei Sockelbetrag
    res_sockel = calculate_beeg(netto_voreinkommen=300.0, has_geschwisterbonus=True)
    assert res_sockel.geschwisterbonus == 75.0
    assert res_sockel.basis_elterngeld == 375.0


def test_mehrlingszuschlag():
    # Zwillinge: +300 € Basis, +150 € Plus
    res_twins = calculate_beeg(netto_voreinkommen=2000.0, mehrlinge_count=2)
    assert res_twins.mehrlingszuschlag_basis == 300.0
    assert res_twins.mehrlingszuschlag_plus == 150.0
    assert res_twins.basis_elterngeld == 1300.0 + 300.0

    # Drillinge: +600 € Basis, +300 € Plus
    res_triplets = calculate_beeg(netto_voreinkommen=2000.0, mehrlinge_count=3)
    assert res_triplets.mehrlingszuschlag_basis == 600.0
    assert res_triplets.mehrlingszuschlag_plus == 300.0


def test_teilzeit_ueber_32_stunden():
    # > 32h schließt Elterngeld für den Monat aus
    res_tz_over = calculate_beeg(netto_voreinkommen=2500.0, teilzeit_stunden=35.0, teilzeit_netto=1500.0)
    assert not res_tz_over.is_teilzeit_eligible
    assert res_tz_over.basis_elterngeld == 0.0


def test_teilzeit_im_rahmen():
    # 20 Stunden mit 1.000 € Netto bei Voreinkommen 2.500 €
    # Einkommensverlust: 1.500 €
    # 1.500 € * 65 % = 975 € Basis mit TZ
    res_tz = calculate_beeg(netto_voreinkommen=2500.0, teilzeit_stunden=20.0, teilzeit_netto=1000.0)
    assert res_tz.is_teilzeit_eligible
    assert res_tz.basis_elterngeld == 975.0
    # Deckelungsbetrag für Plus: 1.625 / 2 = 812.50 €
    assert res_tz.elterngeld_plus == 812.50
