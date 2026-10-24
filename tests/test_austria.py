# -*- coding: utf-8 -*-
import pytest
from elterngeld_dach.calculator import calculate_austria_benefits
from elterngeld_dach.rates import AT_EA_KBG_MAX_TAGESSATZ


def test_austria_wochengeld_standard():
    res = calculate_austria_benefits(
        monthly_net_income=2500.0,
        is_caesarean_or_multiples=False,
    )
    # Schutzfrist 16 Wochen
    assert res["wochengeld_protection_weeks"] == 16
    assert res["wochengeld_daily"] > 0
    assert res["wochengeld_total"] > 0


def test_austria_wochengeld_caesarean():
    res = calculate_austria_benefits(
        monthly_net_income=2500.0,
        is_caesarean_or_multiples=True,
    )
    # Schutzfrist 20 Wochen
    assert res["wochengeld_protection_weeks"] == 20


def test_austria_earnings_based_kbg():
    res = calculate_austria_benefits(
        monthly_net_income=2000.0,
        selected_kbg_model="earnings_based",
    )
    # 2000 * 1.17 / 30 = 78 Euro / Tag * 80% = 62.40 Euro
    assert res["kbg_daily_rate"] <= AT_EA_KBG_MAX_TAGESSATZ
    assert res["kbg_additional_income_limit"] == 8600.0


def test_austria_earnings_based_kbg_capping():
    # Hohes Einkommen führt zur Deckelung bei 73,88 Euro/Tag
    res = calculate_austria_benefits(
        monthly_net_income=5000.0,
        selected_kbg_model="earnings_based",
    )
    assert res["kbg_daily_rate"] == AT_EA_KBG_MAX_TAGESSATZ


def test_austria_account_kbg():
    res = calculate_austria_benefits(
        monthly_net_income=2000.0,
        selected_kbg_model="account",
        kbg_account_days=365,
    )
    assert res["kbg_daily_rate"] >= 16.93
    assert res["kbg_daily_rate"] <= 39.12
    assert res["kbg_total_single"] > 0
