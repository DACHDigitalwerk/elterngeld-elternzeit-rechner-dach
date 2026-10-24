# -*- coding: utf-8 -*-
"""
Kommandozeilen-Interface (CLI) für dach-elterngeld.
"""

import argparse
import json
import sys
from .calculator import (
    calculate_germany_elterngeld,
    calculate_austria_benefits,
    calculate_switzerland_benefits,
    calculate_de_replacement_rate,
)


def main():
    parser = argparse.ArgumentParser(
        prog="dach-elterngeld",
        description="DACH Elterngeld-, Mutterschutz- & Elternzeit-Rechner 2026 (BEEG, MSchG, KBGG, EOG)",
    )
    subparsers = parser.add_subparsers(dest="country", help="Land auswählen (de, at, ch)")

    # Subcommand: DE
    de_parser = subparsers.add_parser("de", help="Deutschland (BEEG & MuSchG)")
    de_parser.add_argument("--netto", type=float, required=True, help="Monatliches Nettoeinkommen vor Geburt in EUR")
    de_parser.add_argument("--teilzeit-netto", type=float, default=0.0, help="Geplantes Nettoeinkommen in Teilzeit waehrend Elternzeit")
    de_parser.add_argument("--teilzeit-stunden", type=float, default=0.0, help="Geplante Wochenarbeitsstunden (max. 32 Std.)")
    de_parser.add_argument("--geschwisterbonus", action="store_true", help="Geschwisterbonus aktivieren (Kind unter 3 bzw. 2 Kinder unter 6)")
    de_parser.add_argument("--mehrlinge", type=int, default=1, help="Anzahl der neugeborenen Kinder (Standard: 1)")
    de_parser.add_argument("--zv-einkommen", type=float, default=0.0, help="Zu versteuerndes Jahreseinkommen (Grenze: 175.000 EUR)")
    de_parser.add_argument("--mutterschaftsgeld", type=float, default=0.0, help="Monatliches Mutterschaftsgeld zur Anrechnung")
    de_parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")

    # Subcommand: AT
    at_parser = subparsers.add_parser("at", help="Oesterreich (MSchG & KBGG)")
    at_parser.add_argument("--netto", type=float, required=True, help="Monatliches Nettoeinkommen in EUR")
    at_parser.add_argument("--kaiserschnitt-mehrling", action="store_true", help="Kaiserschnitt, Fruehgeburt oder Mehrlinge (12 Wochen Schutzfrist nach Geburt)")
    at_parser.add_argument("--modell", choices=["ea", "konto"], default="ea", help="KBG-Modell: ea (einkommensabhaengig) oder konto (pauschal)")
    at_parser.add_argument("--tage", type=int, default=365, help="Bezugstage fuer pauschales KBG-Konto (365 bis 1063)")
    at_parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")

    # Subcommand: CH
    ch_parser = subparsers.add_parser("ch", help="Schweiz (EOG & VAEg)")
    ch_parser.add_argument("--brutto", type=float, required=True, help="Monatlicher Bruttolohn vor Niederkunft in CHF")
    ch_parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")

    args = parser.parse_args()

    if not args.country:
        parser.print_help()
        sys.exit(0)

    if args.country == "de":
        res = calculate_germany_elterngeld(
            net_income_before=args.netto,
            part_time_net_during=args.teilzeit_netto,
            part_time_hours_per_week=args.teilzeit_stunden,
            has_qualifying_siblings=args.geschwisterbonus,
            multiple_birth_count=args.mehrlinge,
            taxable_yearly_income=args.zv_einkommen,
            maternity_benefit_monthly=args.mutterschaftsgeld,
        )
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 65)
            print("🇩🇪 DEUTSCHLAND: ELTERNGELD-BERECHNUNG 2026 (BEEG)")
            print("=" * 65)
            if not res["eligible"]:
                print(f"❌ KEIN ANSPRUCH: {res['reason']}")
                sys.exit(1)
            print(f"Nettoeinkommen vor Geburt : {res['net_income_before']:,.2f} EUR")
            print(f"Ersatzrate gem. BEEG       : {res['replacement_rate'] * 100:.1f} Prozent")
            print(f"Basiselterngeld / Monat   : {res['monthly_basis_elterngeld']:,.2f} EUR (max. 12-14 Monate)")
            print(f"ElterngeldPlus / Monat     : {res['monthly_plus_elterngeld']:,.2f} EUR (max. 24-28 Monate)")
            if res["sibling_bonus_basis"] > 0:
                print(f"inkl. Geschwisterbonus     : +{res['sibling_bonus_basis']:,.2f} EUR / Monat")
            if res["multiples_bonus_basis"] > 0:
                print(f"inkl. Mehrlingszuschlag    : +{res['multiples_bonus_basis']:,.2f} EUR / Monat")
            if res["maternity_benefit_monthly"] > 0:
                print(f"Auszahlung im Mutterschutz : {res['payout_during_mutterschutz']:,.2f} EUR")
            if res["partnership_bonus_eligible"]:
                print("✅ Partnerschaftsbonus-Monate moeglich (Teilzeit 24-32 Std./Woche erfuellt)")
            print("=" * 65)

    elif args.country == "at":
        model_name = "earnings_based" if args.modell == "ea" else "account"
        res = calculate_austria_benefits(
            monthly_net_income=args.netto,
            is_caesarean_or_multiples=args.kaiserschnitt_mehrling,
            selected_kbg_model=model_name,
            kbg_account_days=args.tage,
        )
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 65)
            print("🇦🇹 OESTERREICH: WOCHENGELD & KINDERBETREUUNGSGELD 2026")
            print("=" * 65)
            print(f"Monatliches Netto         : {res['monthly_net_income']:,.2f} EUR")
            print(f"Wochengeld Tagessatz      : {res['wochengeld_daily']:,.2f} EUR / Tag ({res['wochengeld_protection_weeks']} Wochen Schutzfrist)")
            print(f"Wochengeld Gesamt         : {res['wochengeld_total']:,.2f} EUR")
            print(f"KBG-Modell                : {res['kbg_model']}")
            print(f"KBG Tagessatz             : {res['kbg_daily_rate']:,.2f} EUR / Tag")
            print(f"KBG Monatsbetrag          : {res['kbg_monthly']:,.2f} EUR / Monat")
            print(f"KBG Gesamtsumme (1 Elter) : {res['kbg_total_single']:,.2f} EUR")
            print(f"Zuverdienstgrenze         : {res['kbg_additional_income_limit']:,.2f} EUR / Jahr")
            print("=" * 65)

    elif args.country == "ch":
        res = calculate_switzerland_benefits(
            monthly_gross_salary=args.brutto,
        )
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("=" * 65)
            print("🇨🇭 SCHWEIZ: MUTTERSCHAFTS- & VATERSCHAFTSENTSCHAEDIGUNG 2026")
            print("=" * 65)
            print(f"Monatlicher Bruttolohn    : {res['monthly_gross_salary']:,.2f} CHF")
            print(f"Taggeld (80 Prozent)      : {res['daily_mse']:,.2f} CHF / Kalendertag")
            if res["is_capped"]:
                print(f"Deckelung aktiv           : Max. {res['cap_limit_daily']:,.2f} CHF / Tag erreicht")
            print(f"Mutterschaftsentschaed.   : {res['mse_total_payout']:,.2f} CHF ({res['mse_duration_days']} Tage / 14 Wochen)")
            print(f"Vaterschaftsurlaub Entsch.: {res['paternity_total_payout']:,.2f} CHF ({res['paternity_duration_days']} Tage / 2 Wochen)")
            print("=" * 65)


if __name__ == "__main__":
    main()
