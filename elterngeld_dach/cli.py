# -*- coding: utf-8 -*-
"""
CLI-Schnittstelle für dach-elterngeld:
DACH Elterngeld-, Mutterschutz- & Elternzeit-Planer 2026.
"""

import argparse
import json
import sys
from .beeg import calculate_beeg, calculate_ersatzrate
from .kbgg import calculate_kbgg
from .eog import calculate_eog
from .planner import evaluate_plan


def format_currency(val: float, curr: str = "€") -> str:
    return f"{val:,.2f} {curr}".replace(",", "X").replace(".", ",").replace("X", ".")


def cmd_de(args):
    res = calculate_beeg(
        netto_voreinkommen=args.netto,
        zve=args.zve,
        has_geschwisterbonus=args.geschwisterbonus,
        mehrlinge_count=args.mehrlinge,
        teilzeit_netto=args.teilzeit_netto,
        teilzeit_stunden=args.teilzeit_stunden,
        mutterschaftsgeld_tagessatz=args.muschgeld,
        ist_mutter=args.mutter,
    )

    if args.json:
        data = {
            "country": "DE",
            "netto": res.netto_voreinkommen,
            "ersatzrate_pct": res.ersatzrate_prozent,
            "is_eligible": res.is_eligible,
            "basis_elterngeld": res.basis_elterngeld,
            "elterngeld_plus": res.elterngeld_plus,
            "geschwisterbonus": res.geschwisterbonus,
            "mehrlingszuschlag_basis": res.mehrlingszuschlag_basis,
            "hinweise": res.hinweise,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=" * 65)
    print("🇩🇪 DEUTSCHLAND: ELTERNGELD & ELTERNZEIT 2026 (BEEG)")
    print("=" * 65)
    print(f"Netto-Voreinkommen (12 Monatsmittel): {format_currency(res.netto_voreinkommen)}")
    print(f"Zu versteuerndes Einkommen (zvE):    {format_currency(res.zve)}")
    print(f"Gesetzliche Ersatzrate:              {res.ersatzrate_prozent:.1f} %")
    print(f"Geringverdiener-Bonus aktiv:         {'Ja (< 1.000 €)' if res.is_geringverdiener else 'Nein'}")
    print(f"Degressive Absenkung aktiv:          {'Ja (> 1.200 €)' if res.is_degressiv else 'Nein'}")
    print("-" * 65)
    if not res.is_eligible:
        print(f"❌ KEIN ANSPRUCH: {res.ineligibility_reason}")
    else:
        print(f"Basiselterngeld pro Monat:           {format_currency(res.basis_elterngeld)}")
        print(f"ElterngeldPlus pro Monat:            {format_currency(res.elterngeld_plus)}")
        if res.has_geschwisterbonus:
            print(f"Inklusive Geschwisterbonus:          +{format_currency(res.geschwisterbonus)} / Monat")
        if res.mehrlinge_count > 1:
            print(f"Inklusive Mehrlingszuschlag:         +{format_currency(res.mehrlingszuschlag_basis)} / Monat")
        if res.teilzeit_netto > 0:
            print(f"Teilzeit-Zuverdienst berücksichtigt: {format_currency(res.teilzeit_netto)} ({res.teilzeit_stunden} h/Woche)")
        if res.mutterschaftsgeld_anrechnung > 0:
            print(f"Mutterschaftsgeld-Anrechnung (M1–2): {format_currency(res.mutterschaftsgeld_anrechnung)} / Monat")

    if res.hinweise:
        print("-" * 65)
        print("Hinweise:")
        for h in res.hinweise:
            print(f"• {h}")
    print("=" * 65)


def cmd_at(args):
    res = calculate_kbgg(
        netto_monat=args.netto,
        ist_kaiserschnitt_oder_mehrling=args.kaiserschnitt,
        pauschale_tage=args.tage,
        beide_eltern=args.beide,
        inkl_sonderzahlungen=not args.ohne_sz,
    )

    if args.json:
        data = {
            "country": "AT",
            "netto_monat": res.netto_monat,
            "wochengeld_tagessatz": res.wochengeld_tagessatz,
            "wochengeld_monat": res.wochengeld_monat,
            "wochengeld_gesamt": res.wochengeld_gesamt,
            "ea_kbg_tagessatz": res.ea_kbg_tagessatz,
            "ea_kbg_monat": res.ea_kbg_monat_30,
            "ea_kbg_gesamt_max": res.ea_kbg_gesamt_max,
            "pauschale_tagessatz": res.pauschale_tagessatz,
            "pauschale_monat": res.pauschale_monat_30,
            "pauschale_gesamt": res.pauschale_gesamt,
            "hinweise": res.hinweise,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=" * 65)
    print("🇦🇹 ÖSTERREICH: WOCHENGELD & KINDERBETREUUNGSGELD 2026")
    print("=" * 65)
    print(f"Nettoeinkommen / Monat:              {format_currency(res.netto_monat)}")
    print("-" * 65)
    print("1. WOCHENGELD (§ 162 ASVG):")
    print(f"   Tagessatz:                        {format_currency(res.wochengeld_tagessatz)}")
    print(f"   Schutzfrist-Dauer:                {res.wochengeld_wochen} Wochen")
    print(f"   Gesamtanspruch Wochengeld:        {format_currency(res.wochengeld_gesamt)}")
    print("-" * 65)
    print("2. EINKOMMENSABHÄNGIGES KBG (80 %):")
    print(f"   Tagessatz (max. 73,88 €):         {format_currency(res.ea_kbg_tagessatz)}")
    print(f"   Monatsbetrag (30 Tage):           {format_currency(res.ea_kbg_monat_30)}")
    print(f"   Gesamt bei {res.ea_kbg_max_tage} Tagen Bezug:      {format_currency(res.ea_kbg_gesamt_max)}")
    print(f"   Zuverdienstgrenze:                {format_currency(res.ea_zuverdienstgrenze)} / Jahr")
    print("-" * 65)
    print("3. PAUSCHALES KBG-KONTO (FLEXIBEL):")
    print(f"   Gewählte Bezugstage:              {res.pauschale_tage} Tage")
    print(f"   Tagessatz:                        {format_currency(res.pauschale_tagessatz)}")
    print(f"   Monatsbetrag (30 Tage):           {format_currency(res.pauschale_monat_30)}")
    print(f"   Gesamtsumme Konto:                {format_currency(res.pauschale_gesamt)}")
    print(f"   Zuverdienstgrenze:                {format_currency(res.pauschale_zuverdienstgrenze)} / Jahr")
    print("=" * 65)


def cmd_ch(args):
    res = calculate_eog(monatslohn=args.lohn)

    if args.json:
        data = {
            "country": "CH",
            "monatslohn": res.monatslohn,
            "massgebender_lohn": res.massgebender_lohn,
            "mse_tagessatz": res.mse_tagessatz,
            "mse_gesamt_14w": res.mse_gesamt,
            "vaterschaft_tagessatz": res.vaterschaft_tagessatz,
            "vaterschaft_gesamt_2w": res.vaterschaft_gesamt,
            "hinweise": res.hinweise,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=" * 65)
    print("🇨🇭 SCHWEIZ: MUTTERSCHAFTS- & VATERSCHAFTSENTSCHÄDIGUNG 2026")
    print("=" * 65)
    print(f"Monatslohn:                          {format_currency(res.monatslohn, 'CHF')}")
    print(f"Maximal anrechenbarer Lohn:          {format_currency(res.massgebender_lohn, 'CHF')}")
    print("-" * 65)
    print("1. MUTTERSCHAFTSENTSCHÄDIGUNG (MSE):")
    print(f"   Taggeld (80 %, max. 220 CHF):     {format_currency(res.mse_tagessatz, 'CHF')} / Tag")
    print(f"   Dauer:                            {res.mse_wochen} Wochen ({res.mse_tage} Tage)")
    print(f"   Gesamtentschädigung:              {format_currency(res.mse_gesamt, 'CHF')}")
    print("-" * 65)
    print("2. URLAUB FÜR DEN ANDEREN ELTERNTEIL (VATERSCHAFTSURLAUB):")
    print(f"   Taggeld:                          {format_currency(res.vaterschaft_tagessatz, 'CHF')} / Tag")
    print(f"   Dauer:                            2 Wochen (14 Taggelder / 10 Arbeitstage)")
    print(f"   Gesamtentschädigung:              {format_currency(res.vaterschaft_gesamt, 'CHF')}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        prog="dach-elterngeld",
        description="DACH Elterngeld-, Mutterschutz- & Elternzeit-Planer 2026 (BEEG, MSchG & Schweizer EO/VAEg)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand DE
    p_de = subparsers.add_parser("de", help="Deutschland: Elterngeld nach BEEG berechnen")
    p_de.add_argument("--netto", type=float, required=True, help="Durchschnittliches Nettoeinkommen vor Geburt (€)")
    p_de.add_argument("--zve", type=float, default=0.0, help="Zu versteuerndes Einkommen im Vorjahr (€)")
    p_de.add_argument("--geschwisterbonus", action="store_true", help="Geschwisterbonus beanspruchen (+10 %%, min 75 €)")
    p_de.add_argument("--mehrlinge", type=int, default=1, help="Anzahl Kinder bei Mehrlingsgeburt (z.B. 2 für Zwillinge)")
    p_de.add_argument("--teilzeit-netto", type=float, default=0.0, help="Monatliches Netto-Einkommen in Teilzeit (€)")
    p_de.add_argument("--teilzeit-stunden", type=float, default=0.0, help="Geplante Wochenarbeitszeit (max. 32 h)")
    p_de.add_argument("--muschgeld", type=float, default=0.0, help="Mutterschaftsgeld-Tagessatz der Krankenkasse + AG-Zuschuss")
    p_de.add_argument("--mutter", action="store_true", help="Berechnung für die Mutter (mit Schutzfrist)")
    p_de.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    p_de.set_defaults(func=cmd_de)

    # Subcommand AT
    p_at = subparsers.add_parser("at", help="Österreich: Wochengeld & KBG berechnen")
    p_at.add_argument("--netto", type=float, required=True, help="Monatliches Nettoeinkommen vor Mutterschutz (€)")
    p_at.add_argument("--kaiserschnitt", action="store_true", help="Kaiserschnitt, Frühgeburt oder Mehrlinge (12 Wochen Schutz)")
    p_at.add_argument("--tage", type=int, default=365, help="Tage für KBG-Konto (365 bis 1063)")
    p_at.add_argument("--beide", action="store_true", help="Aufteilung auf beide Elternteile (bis 426 bzw. 1063 Tage)")
    p_at.add_argument("--ohne-sz", action="store_true", help="Ohne Sonderzahlungs-Zuschlag")
    p_at.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    p_at.set_defaults(func=cmd_at)

    # Subcommand CH
    p_ch = subparsers.add_parser("ch", help="Schweiz: MSE & Vaterschaftsentschädigung berechnen")
    p_ch.add_argument("--lohn", type=float, required=True, help="Monatslohn vor der Geburt (CHF)")
    p_ch.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    p_ch.set_defaults(func=cmd_ch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
