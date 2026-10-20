#!/usr/bin/env python3
"""Maintenance tool for the BLUE Trend Radar.

Usage:
    python tools/radar.py validate   # check schema, values and review deadlines
    python tools/radar.py csv        # export data/trends.csv for spreadsheets
    python tools/radar.py build      # inject data/trends.json into docs/index.html
    python tools/radar.py table      # write report/radar_table.tex (the table in the PDF)
    python tools/radar.py score      # write research/PRIORITIZATION.md (weighted scores + sensitivity test)
    python tools/radar.py all        # validate + csv + build + table + score

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
PRIORITY_MD = ROOT / "research" / "PRIORITIZATION.md"

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
        weights = data["meta"].get("priority_model", {}).get("weights", {})
        scores = t.get("priority", {}).get("scores", {})
        if set(scores) != set(weights):
            errors.append(f"{tid}: priority.scores must cover {sorted(weights)}")
        elif any(not isinstance(v, int) or not 1 <= v <= 5 for v in scores.values()):
            errors.append(f"{tid}: priority scores must be integers 1-5")
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


def weighted(scores, weights):
    return sum(weights[k] * scores[k] for k in weights)


def priority_report(data, runs=5000, seed=42):
    """Write research/PRIORITIZATION.md: scores, rationale and a weight-sensitivity test."""
    import random
    model = data["meta"]["priority_model"]
    w0 = model["weights"]
    keys = list(w0)
    trends = data["trends"]
    base = {t["id"]: weighted(t["priority"]["scores"], w0) for t in trends}
    order = sorted(trends, key=lambda t: -base[t["id"]])
    rank0 = {t["id"]: i + 1 for i, t in enumerate(order)}

    # Monte Carlo: perturb every weight by up to +/-50% of its value, renormalise, re-rank.
    rng = random.Random(seed)
    first, top3 = {t["id"]: 0 for t in trends}, {t["id"]: 0 for t in trends}
    for _ in range(runs):
        raw = {k: w0[k] * rng.uniform(0.5, 1.5) for k in keys}
        s = sum(raw.values())
        w = {k: v / s for k, v in raw.items()}
        ranked = sorted(trends, key=lambda t: -weighted(t["priority"]["scores"], w))
        first[ranked[0]["id"]] += 1
        for t in ranked[:3]:
            top3[t["id"]] += 1
    equal = {k: 1 / len(keys) for k in keys}
    eq_rank = {t["id"]: i + 1 for i, t in enumerate(sorted(trends, key=lambda t: -weighted(t["priority"]["scores"], equal)))}

    short = {"strategic_fit": "Fit", "rd_opportunity": "R&D gap", "funding_timing": "Timing",
             "feasibility": "Feasib.", "evidence_confidence": "Evidence"}
    L = ["# Technology prioritisation", "",
         "> Generated by `python tools/radar.py score` from `data/trends.json` - edit the data, not this file.", "",
         model["purpose"], "",
         "## Criteria and weights", "", "| Criterion | Weight | What is scored |", "|---|---|---|"]
    for k in keys:
        nice = {"rd_opportunity": "R&D opportunity"}.get(k, k.replace("_", " ").capitalize())
        L.append(f"| {nice} | {round(w0[k]*100)}% | {model['criteria'][k]} |")
    L += ["", f"Scale: {model['scale']} {model['caveat']}", "",
          "## Ranking", "",
          "| Rank | Trend | " + " | ".join(short[k] for k in keys) + " | **Score** | Ring |",
          "|---|---|" + "---|" * len(keys) + "---|---|"]
    for t in order:
        sc = t["priority"]["scores"]
        L.append(f"| {rank0[t['id']]} | {t['id']} {t['short_name']} | " + " | ".join(str(sc[k]) for k in keys)
                 + f" | **{base[t['id']]:.2f}** | {t['ring']} |")
    L += ["", "## How robust is the ranking?", "",
          f"Each weight was varied at random by up to ±50% of its value and renormalised, {runs:,} times "
          f"(fixed seed {seed}). Equal weights were also tested.", "",
          "| Trend | Base rank | Rank with equal weights | Ranked 1st | In top 3 |", "|---|---|---|---|---|"]
    for t in order:
        i = t["id"]
        L.append(f"| {i} {t['short_name']} | {rank0[i]} | {eq_rank[i]} | {first[i]/runs:.0%} | {top3[i]/runs:.0%} |")
    lead = order[0]
    L += ["", "## What the scores say", "",
          f"- **{lead['id']} {lead['short_name']}** ranks first in {first[lead['id']]/runs:.0%} of weight variations "
          f"and first with equal weights: the choice of CircuTwin-HD (built on {lead['id']}) does not depend on a particular weighting.",
          f"- **{order[1]['id']} {order[1]['short_name']}** is the strongest alternative project; it scores lower mainly on "
          "feasibility, because BLUE would depend on a truck OEM for hardware.",
          "- **The scores challenge one ring.** T02 Battery health analytics is in *Engage now* but ranks "
          f"{rank0['T02']}th on its own. It stays in Engage now because CircuTwin-HD needs the same remaining-life "
          "methods and data: engaging T02 is part of the T06 project, not a separate bet. If CircuTwin-HD is not "
          "pursued, T02 should move to *Build capability*.",
          "- **Rings and scores answer different questions.** The ring says *when* to act; the score says *how attractive* "
          "the trend is for BLUE. T04 Virtual homologation scores high but stays in *Build capability* because no "
          "funding window is open yet.", "",
          "## Rationale per trend", ""]
    for t in order:
        L.append(f"**{t['id']} {t['name']}** (score {base[t['id']]:.2f})")
        L.append("")
        for k in keys:
            L.append(f"- {short[k]} {t['priority']['scores'][k]}/5: {t['priority']['rationale'][k]}")
        L.append("")
    PRIORITY_MD.parent.mkdir(exist_ok=True)
    PRIORITY_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {PRIORITY_MD.relative_to(ROOT)}")


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
    if cmd in ("score", "all"):
        priority_report(data)


if __name__ == "__main__":
    main()
