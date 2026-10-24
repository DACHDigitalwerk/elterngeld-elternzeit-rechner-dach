# -*- coding: utf-8 -*-
"""
Tests für die CLI dach-elterngeld.
"""

import subprocess
import json
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run_cli(args):
    env = dict(os.environ)
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{REPO_ROOT}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else REPO_ROOT

    cmd = [sys.executable, "-m", "elterngeld_dach.cli"] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=REPO_ROOT, env=env)


def test_cli_de_json():
    res = run_cli(["de", "--netto", "2500", "--json"])
    data = json.loads(res.stdout)
    assert data["country"] == "DE"
    assert data["netto"] == 2500.0
    assert data["is_eligible"] is True
    assert data["basis_elterngeld"] == 1625.0  # 2500 * 0.65


def test_cli_de_over_limit():
    res = run_cli(["de", "--netto", "4000", "--zve", "180000", "--json"])
    data = json.loads(res.stdout)
    assert data["is_eligible"] is False
    assert data["basis_elterngeld"] == 0.0


def test_cli_at_json():
    res = run_cli(["at", "--netto", "2000", "--json"])
    data = json.loads(res.stdout)
    assert data["country"] == "AT"
    assert data["wochengeld_tagessatz"] > 0
    assert data["ea_kbg_tagessatz"] > 0


def test_cli_ch_json():
    res = run_cli(["ch", "--lohn", "8250", "--json"])
    data = json.loads(res.stdout)
    assert data["country"] == "CH"
    assert data["mse_tagessatz"] == 220.0
    assert data["mse_gesamt_14w"] == 220.0 * 98
