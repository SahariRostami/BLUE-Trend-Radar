# BLUE Engineering Trend Radar — Smart, Sustainable & Circular Commercial Mobility

A mini technology radar for BLUE Engineering's R&D team, covering **automotive**, narrowed to
**zero-emission commercial vehicles** (buses, coaches, vans, trucks), with a 2031–2036 horizon.

| Deliverable | File |
|---|---|
| Write-up (2 pages) | [`report/report.pdf`](report/report.pdf) · source [`report/report.tex`](report/report.tex) (its table, `radar_table.tex`, is generated from the data) |
| Data file | [`data/trends.json`](data/trends.json) (master) · [`data/trends.csv`](data/trends.csv) (spreadsheet export) |
| Dashboard | [`docs/index.html`](docs/index.html) |
| Screening and audit | [`research/longlist_screen.csv`](research/longlist_screen.csv) · [`research/SOURCE_AUDIT.md`](research/SOURCE_AUDIT.md) |
| Maintenance tool | [`tools/radar.py`](tools/radar.py) · monthly check [`.github/workflows/radar-check.yml`](.github/workflows/radar-check.yml) |

## Open the dashboard

**Option 1 – no installation:** download the repository and double-click `docs/index.html`.
It is a single self-contained file (data embedded, no server, no internet needed).

**Option 2 – online (after you enable Pages):** the dashboard can be published with GitHub Pages:
`https://<github-user>.github.io/BLUE-Trend-Radar/`
(Settings → Pages → Deploy from branch → `main` / `docs`).

What it shows:
- **Radar**: four sectors (Electrification, Digital twins & validation, AI & automation, Circularity) and three
  rings that mean *what BLUE should do* — Engage now, Build capability, Monitor. Shape = class
  (circle Core, diamond Adjacent, triangle Transformative); hollow = TRL still provisional.
- **Detail panel** (click any trend): two *separate* indicators — industry maturity (EU TRL, with evidence) and
  the BLUE R&D opportunity (the unsolved next step, starting maturity marked as an assumption) — plus the
  2031–2036 outlook, driver, barrier, signpost to watch, ring rationale and typed sources.
- **Watchlist timeline**: dated events that trigger a review, with a "today" marker.
- **Recommended project**: CircuTwin-HD, with a novelty check against running EU projects and the funding route.

## The data file

`data/trends.json` is the single source of truth. Per trend it stores:

| Field | Meaning |
|---|---|
| `state_of_art.trl`, `evidence`, `evidence_status` | Industry TRL of the best evidenced application; `provisional` if no cited demonstration |
| `rd_frontier.application`, `starting_maturity` | Where BLUE could do R&D; starting maturity is a planning assumption, not a TRL claim |
| `classification` | Core / Adjacent / Transformative **for BLUE** |
| `ring`, `ring_why` | Recommended action and why |
| `expected_evolution_2031_2036`, `driver`, `barrier`, `signpost` | Forward-looking view |
| `sources[]` | `type` (regulation, EU official, project report, company release, vendor, academic, news), `checked_at`, `access_status` |
| `watch[]`, top-level `watchlist[]` | Dated review triggers (`precision`: day / month / year) |

## Keeping the radar alive

```bash
python tools/radar.py validate   # schema + flags overdue reviews and passed watchlist dates
python tools/radar.py all        # validate, export CSV, rebuild docs/index.html and report/radar_table.tex
cd report && pdflatex report.tex # recompile the write-up (run twice)
```

Only the Python standard library is needed. The process:

1. **Owner**: one R&D team member (the trend-radar intern), quarterly sign-off by the Head of R&D.
2. **Cadence**: quarterly review, plus an event-driven review whenever a watchlist date passes.
3. **Change rule**: a TRL or ring changes only with a new dated source and a one-line rationale; git history is the audit trail.
4. **Retire rule**: no new evidence for two reviews → move to Monitor, or remove if merged/irrelevant.
5. **Signals**: CORDIS results (not objectives), EU Funding & Tenders, EUR-Lex and UNECE WP.29, OEM releases, Catena-X, patents (Espacenet), local signals (Torino City Lab, Regione Piemonte).
6. **Automation**: the GitHub workflow runs on every change and on the 1st of each month. It fails if the data
   are invalid or the generated dashboard, CSV or LaTeX table is out of sync with them (the compiled PDF is not
   checked: recompile it after data changes). On the monthly run it opens one "Radar review due" issue, or adds
   a comment to it if it is still open, listing overdue reviews and passed watchlist dates. GitHub may notify users subscribed to repository issues; enable **Watch → Custom → Issues** or assign a maintainer. This is not a guaranteed external-mail service. Acknowledged milestones must have `watchlist[].reviewed_at` recorded to stop repeat alerts.

## Assumptions

- Public sources only; no client or employer data. TRLs are analyst judgements on the EU scale.
- Commercial vehicles are the part of automotive where BLUE can act within one proposal cycle.
- Funding details for HORIZON-CL5-2027-03-D5-03 (planned opening 15 Dec 2026, deadline 14 Apr 2027) must be
  re-checked on the EU Funding & Tenders portal when the call opens; the Work Programme identifies this as an **Innovation Action (IA)**, with ~EUR 24M topic budget and EUR 5–7M indicative contribution per consortium project.

## Use of AI

AI assistants were used for search, drafting and cross-checking. Source-level claims are dated and typed; entries should be rechecked before a formal proposal. Claims not fully supported are labelled in place (for example the UN R152 virtual-testing amendment). Independent reviews were part of the process:
one caught that an earlier draft had wrongly dismissed RUST2LIFE as non-existent (it is CORDIS grant 101295335
and is now the closest related project), and another added MINDED as validation evidence for digital twins.

---
Sahar Rostami · October 2026

## Final PDF check

`report/report.pdf` is a separately compiled artifact. The CI checks the source-generated `radar_table.tex`, **not the compiled PDF**. Recompile with `pdflatex` twice and confirm it is at most two pages before committing.
