# -*- coding: utf-8 -*-
import pytest
from elterngeld_dach.calculator import (
    calculate_de_replacement_rate,
    calculate_germany_elterngeld,
)
from elterngeld_dach.rates import (
    DE_MIN_BASIS_ELTERNGELD,
    DE_MAX_BASIS_ELTERNGELD,
    DE_MIN_PLUS_ELTERNGELD,
    DE_MAX_PLUS_ELTERNGELD,
)


def test_standard_replacement_rate():
    # 1.000 bis 1.200 Euro Netto = 67%
    assert calculate_de_replacement_rate(1000.0) == 0.67
    assert calculate_de_replacement_rate(1100.0) == 0.67
    assert calculate_de_replacement_rate(1200.0) == 0.67


def test_low_income_replacement_rate():
    # Unter 1.000 Euro Netto: je 2 Euro unter 1.000 Euro +0,1%
    # 900 Euro -> 100 Euro unter 1000 -> 50 * 0,1% = +5% -> 72%
    assert calculate_de_replacement_rate(900.0) == 0.72
    # 500 Euro -> 500 Euro unter 1000 -> 250 * 0,1% = +25% -> 92%
    assert calculate_de_replacement_rate(500.0) == 0.92
    # 340 Euro -> 660 Euro unter 1000 -> 330 * 0,1% = +33% -> 100%
    assert calculate_de_replacement_rate(340.0) == 1.00
    assert calculate_de_replacement_rate(100.0) == 1.00


def test_high_income_replacement_rate():
    # Über 1.200 Euro Netto: je 20 Euro über 1.200 Euro -0,1% (bis 65%)
    # 1.400 Euro -> 200 Euro über 1200 -> 10 * 0,1% = -1% -> 66%
    assert calculate_de_replacement_rate(1400.0) == 0.66
    # 1.600 Euro -> 400 Euro über 1200 -> 20 * 0,1% = -2% -> 65%
    assert calculate_de_replacement_rate(1600.0) == 0.65
    assert calculate_de_replacement_rate(3000.0) == 0.65


def test_basis_elterngeld_caps():
    # Mindestbetrag 300 Euro bei geringem Einkommen
    res_min = calculate_germany_elterngeld(net_income_before=200.0)
    assert res_min["monthly_basis_elterngeld"] == DE_MIN_BASIS_ELTERNGELD

    # Höchstbetrag 1.800 Euro bei hohem Einkommen
    res_max = calculate_germany_elterngeld(net_income_before=4000.0)
    assert res_max["monthly_basis_elterngeld"] == DE_MAX_BASIS_ELTERNGELD


def test_sibling_bonus():
    # 10% Zuschlag, mind. 75 Euro für Basis
    res = calculate_germany_elterngeld(net_income_before=2000.0, has_qualifying_siblings=True)
    # Netto 2000 -> Rate 65% -> 1300 Euro -> 10% sind 130 Euro Bonus
    assert res["sibling_bonus_basis"] == 130.0
    assert res["monthly_basis_elterngeld"] == 1300.0 + 130.0

    # Mindestbonus 75 Euro bei niedrigem Basis-Elterngeld
    res_low = calculate_germany_elterngeld(net_income_before=600.0, has_qualifying_siblings=True)
    assert res_low["sibling_bonus_basis"] == 75.0


def test_multiple_birth_bonus():
    # Zwillinge: +300 Euro Basis, +150 Euro Plus
    res = calculate_germany_elterngeld(net_income_before=2000.0, multiple_birth_count=2)
    assert res["multiples_bonus_basis"] == 300.0
    assert res["multiples_bonus_plus"] == 150.0
    assert res["monthly_basis_elterngeld"] == 1300.0 + 300.0

    # Drillinge: +600 Euro Basis
    res_triplets = calculate_germany_elterngeld(net_income_before=2000.0, multiple_birth_count=3)
    assert res_triplets["multiples_bonus_basis"] == 600.0


def test_income_limit_2026():
    # Über 175.000 Euro zu versteuerndes Einkommen: Kein Anspruch
    res_over = calculate_germany_elterngeld(
        net_income_before=3000.0,
        taxable_yearly_income=180000.0,
    )
    assert res_over["eligible"] is False
    assert res_over["monthly_basis_elterngeld"] == 0.0

    # Bis 175.000 Euro: Anspruch besteht
    res_under = calculate_germany_elterngeld(
        net_income_before=3000.0,
        taxable_yearly_income=174000.0,
    )
    assert res_under["eligible"] is True


def test_part_time_during_parental_leave():
    # Teilzeit: Nettoverlust wird ausgeglichen
    res = calculate_germany_elterngeld(
        net_income_before=2500.0,
        part_time_net_during=1000.0,
        part_time_hours_per_week=25.0,
    )
    # Verlust: 1500 Euro * 65% = 975 Euro
    assert res["income_loss"] == 1500.0
    assert res["monthly_basis_elterngeld"] == 975.0
    assert res["partnership_bonus_eligible"] is True

    # Überschreitung 32 Wochenstunden
    res_invalid_hours = calculate_germany_elterngeld(
        net_income_before=2500.0,
        part_time_hours_per_week=35.0,
    )
    assert res_invalid_hours["eligible"] is False


def test_maternity_benefit_offset():
    # Mutterschaftsgeld-Anrechnung
    res = calculate_germany_elterngeld(
        net_income_before=2000.0,
        maternity_benefit_monthly=1000.0,
    )
    # Basis: 1300 Euro - 1000 Euro = 300 Euro
    assert res["payout_during_mutterschutz"] == 300.0
