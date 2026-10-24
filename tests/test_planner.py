# -*- coding: utf-8 -*-
"""
Tests für den 24-Monats-Elternzeit-Planer.
"""

import pytest
from elterngeld_dach.planner import evaluate_plan


def test_standard_plan_12_plus_2():
    # ET1: M1-M12 Basiselterngeld (12 Monate)
    # ET2: M13-M14 Basiselterngeld (2 Monate)
    et1_months = ['basis'] * 12 + ['arbeit'] * 12
    et2_months = ['arbeit'] * 12 + ['basis'] * 2 + ['arbeit'] * 10

    plan = evaluate_plan(
        et1_netto=2500.0,
        et2_netto=2000.0,
        et1_months=et1_months,
        et2_months=et2_months,
    )

    assert plan.is_valid_beeg
    assert len(plan.violations) == 0
    assert plan.et1_basis_monate == 12
    assert plan.et2_basis_monate == 2
    assert plan.gleichzeitige_basis_monate_jahr1 == 0
    assert plan.total_auszahlung > 0


def test_plan_gleichzeitigkeit_verstoss_jahr1():
    # Beide nehmen Monat 2 und Monat 3 gleichzeitig Basiselterngeld (2 Monate > 1 erlaubter Monat)
    et1_months = ['basis'] * 10 + ['arbeit'] * 14
    et2_months = ['arbeit', 'basis', 'basis'] + ['arbeit'] * 21

    plan = evaluate_plan(
        et1_netto=2000.0,
        et2_netto=2000.0,
        et1_months=et1_months,
        et2_months=et2_months,
    )

    assert not plan.is_valid_beeg
    assert any("Gleichzeitiger Basiselterngeld-Bezug" in v for v in plan.violations)


def test_plan_kontingent_ueberschritten():
    # 16 Basismonate geplant (> 14 Monate)
    et1_months = ['basis'] * 12 + ['arbeit'] * 12
    et2_months = ['arbeit'] * 12 + ['basis'] * 4 + ['arbeit'] * 8

    plan = evaluate_plan(
        et1_netto=2000.0,
        et2_netto=2000.0,
        et1_months=et1_months,
        et2_months=et2_months,
    )

    assert not plan.is_valid_beeg
    assert any("Gesamtanspruchskontingent" in v for v in plan.violations)


def test_plan_mit_plus_und_partnerbonus():
    # ET1: 6 Monate Basis (M1-M6), dann 4 Monate Plus (M7-M10), dann 4 Monate Bonus (M11-M14)
    # ET2: 4 Monate Plus (M7-M10), dann 4 Monate Bonus (M11-M14)
    et1_months = ['basis'] * 6 + ['plus'] * 4 + ['partnerbonus'] * 4 + ['arbeit'] * 10
    et2_months = ['arbeit'] * 6 + ['plus'] * 4 + ['partnerbonus'] * 4 + ['arbeit'] * 10
    et1_hours = [0.0]*6 + [20.0]*4 + [28.0]*4 + [40.0]*10
    et2_hours = [40.0]*6 + [20.0]*4 + [28.0]*4 + [40.0]*10

    plan = evaluate_plan(
        et1_netto=2200.0,
        et2_netto=2200.0,
        et1_months=et1_months,
        et2_months=et2_months,
        et1_hours=et1_hours,
        et2_hours=et2_hours,
    )

    assert plan.is_valid_beeg
    assert plan.et1_bonus_monate == 4
    assert plan.et2_bonus_monate == 4
