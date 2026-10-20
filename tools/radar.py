#!/usr/bin/env python3
"""Maintenance tool for the BLUE Trend Radar.

Usage:
    python tools/radar.py validate   # check schema, values and review deadlines
    python tools/radar.py csv        # export data/trends.csv for spreadsheets
    python tools/radar.py build      # inject data/trends.json into docs/index.html
    python tools/radar.py table      # write report/radar_table.tex (the table in the PDF)
    python tools/radar.py all        # validate + csv + build + table

Only the Python standard library is used.
"""
import csv
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "trends.json"
CSV_OUT = ROOT / "data" / "trends.csv"
TEMPLATE = ROOT / "tools" / "dashboard_template.html"
SITE = ROOT / "docs" / "index.html"
TABLE = ROOT / "report" / "radar_table.tex"

RINGS = {"Engage now", "Build capability", "Monitor"}
CLASSES = {"Core", "Adjacent", "Transformative"}
REQUIRED = ["id", "name", "short_name", "sector", "classification", "ring", "description",
            "state_of_art", "rd_frontier", "evidence_status", "expected_evolution_2031_2036",
            "driver", "barrier", "signpost", "ring_why", "sources", "last_reviewed",
            "report_label", "report_evidence"]
MAX_AGE_DAYS = 100  # one quarter plus a short grace period


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def parse_date(text):
    """Accept YYYY, YYYY-MM or YYYY-MM-DD; return the last day the date could mean."""
    parts = [int(p) for p in str(text).split("-")]
    if len(parts) == 1:
        return dt.date(parts[0], 12, 31)
    if len(parts) == 2:
        nxt = dt.date(parts[0] + (parts[1] == 12), parts[1] % 12 + 1, 1)
        return nxt - dt.timedelta(days=1)
    return dt.date(*parts)


def validate(data, today=None):
    today = today or dt.date.today()
    errors, warnings = [], []
    ids = set()
    for t in data["trends"]:
        tid = t.get("id", "?")
        if tid in ids:
            errors.append(f"{tid}: duplicate id")
        ids.add(tid)
        for key in REQUIRED:
            if key not in t:
                errors.append(f"{tid}: missing '{key}'")
        trl = t.get("state_of_art", {}).get("trl")
        if not isinstance(trl, int) or not 1 <= trl <= 9:
            errors.append(f"{tid}: state_of_art.trl must be an integer 1-9")
        if t.get("ring") not in RINGS:
            errors.append(f"{tid}: ring '{t.get('ring')}' not in {sorted(RINGS)}")
        if t.get("classification") not in CLASSES:
            errors.append(f"{tid}: classification '{t.get('classification')}' not in {sorted(CLASSES)}")
        if t.get("evidence_status") not in {"supported", "provisional"}:
            errors.append(f"{tid}: evidence_status must be 'supported' or 'provisional'")
        opened = [s for s in t.get("sources", []) if s.get("access_status") == "opened"]
        if not opened:
            errors.append(f"{tid}: needs at least one source with access_status 'opened'")
        age = (today - parse_date(t.get("last_reviewed", "1900-01-01"))).days
        if age > MAX_AGE_DAYS:
            warnings.append(f"{tid}: last reviewed {age} days ago - quarterly review overdue")
    for w in data.get("watchlist", []):
        due = parse_date(w["date"])
        reviewed = w.get("reviewed_at")
        # Mark a completed review in watchlist.reviewed_at after checking the event.
        # This prevents the same historical milestone triggering forever.
        acknowledged = bool(reviewed) and parse_date(reviewed) >= due
        if due < today and not acknowledged:
            warnings.append(f"watchlist: '{w['event']}' ({w['date']}) has passed - review {w['trend']}")
    return errors, warnings


def export_csv(data):
    cols = ["id", "short_name", "sector", "classification", "ring", "industry_trl", "evidence_status",
            "rd_frontier", "rd_starting_maturity", "expected_evolution_2031_2036", "driver", "barrier",
            "signpost", "n_sources", "last_reviewed"]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for t in data["trends"]:
            wr.writerow({
                "id": t["id"], "short_name": t["short_name"], "sector": t["sector"],
                "classification": t["classification"], "ring": t["ring"],
                "industry_trl": t["state_of_art"]["trl"], "evidence_status": t["evidence_status"],
                "rd_frontier": t["rd_frontier"]["application"],
                "rd_starting_maturity": t["rd_frontier"].get("starting_maturity"),
                "expected_evolution_2031_2036": t["expected_evolution_2031_2036"],
                "driver": t["driver"], "barrier": t["barrier"], "signpost": t["signpost"],
                "n_sources": len(t["sources"]), "last_reviewed": t["last_reviewed"],
            })
    print(f"wrote {CSV_OUT.relative_to(ROOT)}")


def build(data):
    html = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    if "/*__RADAR_DATA__*/null" not in html:
        sys.exit("template placeholder not found")
    SITE.parent.mkdir(exist_ok=True)
    SITE.write_text(html.replace("/*__RADAR_DATA__*/null", payload), encoding="utf-8")
    print(f"wrote {SITE.relative_to(ROOT)}")


def latex_table(data):
    """Write the radar table used by report/report.tex, so the PDF always matches the data."""
    short_class = {"Core": "Core", "Adjacent": "Adj.", "Transformative": "Transf."}
    short_ring = {"Engage now": "Engage", "Build capability": "Build", "Monitor": "Monitor"}
    lines = [
        "% Generated by tools/radar.py from data/trends.json - do not edit by hand.",
        r"\begin{tabularx}{\textwidth}{@{}lcll>{\raggedright\arraybackslash}X@{}}",
        r"\toprule",
        r"Trend & TRL & Class & Ring & Key evidence \\",
        r"\midrule",
    ]
    for i, t in enumerate(data["trends"], 1):
        star = "*" if t["evidence_status"] == "provisional" else ""
        label = t["report_label"].replace("&", r"\&")
        lines.append(f"{i} {label} & {t['state_of_art']['trl']}{star} & {short_class[t['classification']]} & "
                     f"{short_ring[t['ring']]} & {t['report_evidence']} \\\\")
    lines += [r"\bottomrule", r"\end{tabularx}", ""]
    TABLE.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {TABLE.relative_to(ROOT)}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    data = load()
    if cmd in ("validate", "all"):
        errors, warnings = validate(data)
        for w in warnings:
            print("WARN ", w)
        for e in errors:
            print("ERROR", e)
        print(f"{len(data['trends'])} trends checked: {len(errors)} errors, {len(warnings)} warnings")
        if errors:
            sys.exit(1)
    if cmd in ("csv", "all"):
        export_csv(data)
    if cmd in ("build", "all"):
        build(data)
    if cmd in ("table", "all"):
        latex_table(data)


if __name__ == "__main__":
    main()
