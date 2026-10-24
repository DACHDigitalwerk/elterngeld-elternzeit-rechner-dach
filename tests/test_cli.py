# -*- coding: utf-8 -*-
import json
import subprocess
import sys


def test_cli_help():
    cmd = [sys.executable, "-m", "elterngeld_dach.cli", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "dach-elterngeld" in res.stdout
    assert "BEEG" in res.stdout


def test_cli_germany():
    cmd = [
        sys.executable,
        "-m",
        "elterngeld_dach.cli",
        "de",
        "--netto", "2500",
        "--geschwisterbonus",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "DEUTSCHLAND: ELTERNGELD-BERECHNUNG" in res.stdout
    assert "Basiselterngeld" in res.stdout
    assert "Geschwisterbonus" in res.stdout


def test_cli_germany_json():
    cmd = [
        sys.executable,
        "-m",
        "elterngeld_dach.cli",
        "de",
        "--netto", "2000",
        "--json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["eligible"] is True
    assert data["monthly_basis_elterngeld"] == 1300.0


def test_cli_germany_ineligible():
    cmd = [
        sys.executable,
        "-m",
        "elterngeld_dach.cli",
        "de",
        "--netto", "4000",
        "--zv-einkommen", "190000",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode != 0
    assert "Einkommensgrenze" in res.stdout


def test_cli_austria():
    cmd = [
        sys.executable,
        "-m",
        "elterngeld_dach.cli",
        "at",
        "--netto", "2200",
        "--modell", "ea",
        "--json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["kbg_model"] == "earnings_based"
    assert data["wochengeld_daily"] > 0


def test_cli_switzerland():
    cmd = [
        sys.executable,
        "-m",
        "elterngeld_dach.cli",
        "ch",
        "--brutto", "7500",
        "--json",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["daily_wage"] == 250.0
    assert data["daily_mse"] == 200.0
    assert data["mse_total_payout"] == 200.0 * 98
