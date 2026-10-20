# CircuTwin-HD — feasibility and validation plan

Snapshot: 20 October 2026. Supporting analysis for section 3 of the report; it does not change the
two-page write-up.

CircuTwin-HD is a **proposal**, not a demonstrated system. This plan shows how the idea would be tested
cheaply first, what data it needs, what could make it fail, and when to stop. The guiding rule is the one
an R&D team would apply to its own budget: **spend little until the riskiest assumption is tested.**

## 1. The riskiest assumptions

| # | Assumption | Why it matters | How it is tested |
|---|---|---|---|
| A1 | Inverter load history (temperature, current, switching events) can be logged or reconstructed from existing bus telematics | Without it, the twin has nothing to learn from | Gate 1: data audit with an operator |
| A2 | A physics-of-failure damage model calibrated on power-cycling tests predicts remaining life with useful accuracy | Core technical claim | Gate 2: proof of concept on public ageing data, then lab tests |
| A3 | Quantified uncertainty changes the decision (repair vs. remanufacture vs. recycle) compared with simple age/mileage rules | This is the novelty; if it never changes a decision, the twin adds cost without value | Gate 3: decision comparison on returned units |
| A4 | Partners will share data under acceptable terms (OEM, operator) | Feasibility of any real project | Parallel track: letters of intent before proposal writing |

## 2. Data needed, where it comes from, and the fallback

| Data | Likely source | Availability today | Fallback if unavailable |
|---|---|---|---|
| Junction/case temperature or a proxy, phase current, DC-link voltage | Bus telematics or inverter controller logs (operator/OEM) | Uncertain: often not exported | Estimate junction temperature from current and coolant temperature with a thermal model (standard practice in power-electronics reliability) |
| Duty cycles of real routes | Operator schedules, GPS speed profiles | Usually available | Standard duty cycles (e.g. SORT bus cycles) |
| Power-module ageing data (cycles to failure, degradation indicators) | Public data and literature for proof of concept; partner lab for calibration | **Public:** NASA PCoE IGBT accelerated-ageing dataset (thermal overstress, six devices) | Accelerated power-cycling on a few modules at a university partner |
| Teardown findings of returned inverters | Remanufacturer | Requires a partner | Expert assessment of returned units as the reference |
| Environmental and cost data (LCA/LCC) | Commercial LCA databases, remanufacturer quotes | Available under licence | Published LCA studies for power electronics |

## 3. Stage gates

| Stage | What is done | Cost/effort (indicative) | Pass criterion | Stop if |
|---|---|---|---|---|
| **0 — Desk PoC** (weeks) | Damage model + uncertainty on public IGBT ageing data; synthetic bus duty cycles | Small: 1 engineer, no partners | Model reproduces measured degradation trends; uncertainty bands cover held-out data | Model cannot track degradation better than a cycle-count rule |
| **1 — Data audit** (1–2 months) | With one operator: which signals exist, at what rate, at what cost | Small: workshops, NDA | At least temperature-proxy and current are obtainable, or can be reconstructed | No usable signals and no logging possible |
| **2 — Lab calibration** (part of a funded project) | Power-cycling of representative modules; calibrate the model | Medium: lab time with university partner | Prediction error and calibration within targets agreed with partners | Error too large for any decision to change |
| **3 — Decision test** (funded project) | Blind comparison on returned inverters: twin vs. age/mileage rule vs. teardown | Medium–high: fleet + remanufacturer | Twin's recommendations match teardown more often than the rule baseline | No measurable improvement over the rule baseline |

Gates 0 and 1 cost little and can be done **before** writing a Horizon proposal. They turn the idea into
evidence a consortium would trust: this is how BLUE could enter the D5-03 call with a credible starting point
instead of a concept only.

## 4. Success measures

| Measure | Definition | Why |
|---|---|---|
| Prediction error | Error of remaining-life estimate on held-out modules | Technical validity (A2) |
| Calibration | Share of outcomes inside the stated uncertainty band | Proves the uncertainty is honest, not decorative |
| Decision agreement | Share of recommendations matching teardown, versus the rule baseline | The core claim (A3) |
| Avoided impact | Material and CO2e avoided per component under stated LCA assumptions | Link to circularity goals and the call's expected outcomes |
| Traceability | Share of required data points available per component, and cost of collecting them | Area B requirement; business case |

Targets are deliberately not fixed here: they should be agreed with partners after Gate 0, when realistic
error levels are known.

## 5. Main risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OEM will not share inverter controller data | Medium–high | High | Reconstruct loads from operator telematics and thermal models; involve the OEM as a partner with clear data rights |
| Too few returned inverters for a statistical decision test | Medium | Medium | Combine field returns with lab-aged modules; extend to battery thermal-management systems (second application) |
| Overlap with running projects (RUST2LIFE, CREDIT) | Medium | Medium | Position as complementary: CircuTwin-HD supplies remaining-life evidence to remanufacturing triage; invite a partner from those consortia |
| Remaining-life model works but does not change decisions | Low–medium | High | Detected cheaply at Gate 0/3; result would still be publishable and would redirect effort |
| Conflict of interest or confidential data in a public exercise | — | — | This repository uses public sources only |

## 6. What this plan deliberately does not do

It does not build the twin. The brief asks for a radar and an R&D project idea; building a prototype
would take weeks and real data. What this plan shows instead is how the idea would be **de-risked step by
step**, with explicit stop criteria — the part of R&D work that decides whether money is well spent.

## Sources

- NASA Prognostics Center of Excellence, [IGBT Accelerated Aging dataset](https://data.nasa.gov/dataset/insulated-gate-bipolar-transistor-igbt-accelerated-aging) (public; thermal overstress ageing of six devices).
- Kim, Lee, Han, [PHM framework for discrete IGBTs in EV applications](https://papers.phmsociety.org/index.php/phme/article/view/4920), PHME 2026 (physics-of-failure damage metric validated by power cycling).
- CORDIS, [HORIZON-CL5-2027-03-D5-03 scope](https://cordis.europa.eu/programme/id/HORIZON_HORIZON-CL5-2027-03-D5-03) (Area B requirements).
- CORDIS, [RUST2LIFE](https://cordis.europa.eu/project/id/101295335) and [CREDIT](https://cordis.europa.eu/projects/101138182) (related projects).
