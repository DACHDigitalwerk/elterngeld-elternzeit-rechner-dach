# -*- coding: utf-8 -*-
"""
DACH Elterngeld & Elternzeit 2026: Quickstart Beispiel.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from elterngeld_dach.beeg import calculate_beeg
from elterngeld_dach.kbgg import calculate_kbgg
from elterngeld_dach.eog import calculate_eog
from elterngeld_dach.planner import evaluate_plan


def main():
    print("=== DEUTSCHLAND (BEEG 2026) ===")
    res_de = calculate_beeg(netto_voreinkommen=2800.0, has_geschwisterbonus=True)
    print(f"Basiselterngeld: {res_de.basis_elterngeld:.2f} € / Monat (Ersatzrate: {res_de.ersatzrate_prozent:.1f} %)")
    print(f"ElterngeldPlus:  {res_de.elterngeld_plus:.2f} € / Monat")

    print("\n=== ÖSTERREICH (MSchG / KBGG 2026) ===")
    res_at = calculate_kbgg(netto_monat=2500.0)
    print(f"Wochengeld:      {res_at.wochengeld_tagessatz:.2f} € / Tag ({res_at.wochengeld_gesamt:.2f} € Gesamt)")
    print(f"ea KBG (80%):    {res_at.ea_kbg_tagessatz:.2f} € / Tag (~ {res_at.ea_kbg_monat_30:.2f} € / Monat)")

    print("\n=== SCHWEIZ (EOG / VAEg 2026) ===")
    res_ch = calculate_eog(monatslohn=7500.0)
    print(f"MSE Taggeld:     {res_ch.mse_tagessatz:.2f} CHF / Tag ({res_ch.mse_gesamt:.2f} CHF für 14 Wochen)")
    print(f"Vaterschaft:     {res_ch.vaterschaft_tagessatz:.2f} CHF / Tag ({res_ch.vaterschaft_gesamt:.2f} CHF für 2 Wochen)")

    print("\n=== 24-MONATS-PLANUNG ===")
    plan = evaluate_plan(
        et1_netto=2800.0,
        et2_netto=2400.0,
        et1_months=['basis']*12 + ['arbeit']*12,
        et2_months=['arbeit']*12 + ['basis']*2 + ['arbeit']*10,
    )
    print(f"Plan BEEG-Gültig: {plan.is_valid_beeg}")
    print(f"Gesamtauszahlung: {plan.total_auszahlung:,.2f} € über 24 Monate")


if __name__ == "__main__":
    main()
