# -*- coding: utf-8 -*-
import pytest
from elterngeld_dach.calculator import calculate_switzerland_benefits
from elterngeld_dach.rates import CH_MSE_MAX_TAGGELD, CH_MSE_DAUER_TAGE


def test_switzerland_mse_standard():
    # 6.000 CHF Monatslohn -> 200 CHF Tagessatz -> 80% = 160 CHF Taggeld
    res = calculate_switzerland_benefits(monthly_gross_salary=6000.0)
    assert res["daily_wage"] == 200.0
    assert res["daily_mse"] == 160.0
    assert res["is_capped"] is False
    assert res["mse_total_payout"] == 160.0 * CH_MSE_DAUER_TAGE
    assert res["paternity_total_payout"] == 160.0 * 14


def test_switzerland_mse_capping():
    # 10.000 CHF Monatslohn -> Tagessatz 333,33 CHF -> 80% = 266,67 CHF
    # Deckelung greift bei 220 CHF/Tag
    res = calculate_switzerland_benefits(monthly_gross_salary=10000.0)
    assert res["daily_mse"] == CH_MSE_MAX_TAGGELD
    assert res["is_capped"] is True
    assert res["mse_total_payout"] == CH_MSE_MAX_TAGGELD * CH_MSE_DAUER_TAGE
    assert res["paternity_total_payout"] == CH_MSE_MAX_TAGGELD * 14
