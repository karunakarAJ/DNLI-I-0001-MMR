# DNLI-I-0001 Medical Monitoring Report (MMR)

Safety-focused Medical Monitoring Report template and pipeline for clinical study **DNLI-I-0001** (DNL-126), generated using a **multi-agent, multi-model AI pipeline** built on Claude Code with Claude (Anthropic) and GPT (OpenAI) review agents.

## Study Overview

| Item | Value |
|------|-------|
| **Study** | DNLI-I-0001 |
| **Drug** | DNL-126 (ETV:SGSH-BioM) |
| **Indication** | MPS IIIA (Sanfilippo Syndrome Type A) |
| **Phase** | Phase 1/2 |
| **Protocol** | Version 6 (26-Aug-2025) |
| **Subjects** | N=20 across 4 cohorts (4 sites) |
| **Data Cut** | 2026-02-25 (EDC) |
| **Report Date** | 2026-04-15 |

### Cohort Structure

| Cohort | N | Dose Schedule (Protocol V6) |
|--------|---|----------------------------|
| A1 | 4 | 3 mg/kg QW Wks 1-2, then 10 mg/kg Q2W |
| A2 | 4 | 3 mg/kg QW Wks 1-2, then escalate 3 → 6 → 10 mg/kg |
| A3 | 10 | 3 mg/kg QW ×6 doses, 6 mg/kg QW ×6 doses, 10 mg/kg QW |
| B1 | 2 | 3 mg/kg QW ×6 doses, 6 mg/kg QW ×6 doses, 10 mg/kg QW |

## Report Sections

1. **Study Status** — Enrollment (dual-panel Figure 1.1), disposition, screen failures, current status
2. **Baseline Characteristics** — Demographics, disease baseline (SGSH mutation, ADA, organ volumes)
3. **Study Conduct** — Protocol deviations, dosing compliance, assessment availability
4. **Study Drug Exposure & Immunogenicity** — Exposure swimlane (Fig 4.1 with IRR/interruption markers), compliance profiles (Fig 4.2 with IRR severity lines), ADA summary
5. **Adverse Events** — TEAEs, IRRs (442 cumulative events), SAE table with timeline figure (Fig 5.3), AESIs
6. **Safety Laboratory** — Biochemistry/hematology trend plots (Figs 6.1–6.4, cohort-panel layout), eDISH (Fig 6.4), immune biomarkers, urine chemistry
7. **ECG Summary** — QTcF, HR, QRS, PR trend plots (Figs 7.1–7.4, cohort-panel layout) with outlier indicators
8. **Vital Signs** — SBP, DBP, Pulse, SpO₂, Temperature trend plots (Figs 8.1–8.5, cohort-panel layout)

### Data Exclusions

Per Protocol V6 Section 9.1, the following **efficacy data** are excluded from this safety report:
- CSF Heparan Sulfate (primary efficacy endpoint)
- Serum NfL (secondary efficacy endpoint)
- Clinical Outcome Assessment results (KABC, VABS-III, BSID III/IV — exploratory efficacy)

**Urine HS** is included per medical monitor direction. COA **collection compliance** (whether assessed per SOA) is tracked, but actual results are not shown.

## Key Safety Findings

### Multi-Model Consensus Review ([full report](docs/consensus-safety-review.md))

Six independent AI agents (3 Claude + 3 GPT) reviewed the MMR and produced a unified consensus:

**Overall Benefit-Risk: Favorable** — No deaths, no discontinuations, no late-onset organ toxicity through up to 107 weeks of exposure in a uniformly fatal pediatric disease.

| Domain | Risk Level | Key Signal | Consensus |
|--------|-----------|------------|-----------|
| IRR | **MEDIUM-HIGH** | 442 events, 75% moderate-severe, 1 anaphylactic reaction (B1) | All 6 agents agree |
| AE/SAE Pattern | MEDIUM | 15 SAEs in 13/20 participants; 0017-9004 has 4 SAEs (highest burden) | All 6 agents agree |
| Immunogenicity/ADA | MEDIUM | 95% ADA+, 60% neutralizing; correlates with IRR severity | All 6 agents agree |
| Hepatotoxicity (eDISH) | LOW | 0/20 ALT >3×ULN, 0/20 TBILI >1.5×ULN | All 6 agents agree |
| ECG | LOW | QTcF >450ms in 3/20 — single observations, IRR-related | All 6 agents agree |

### Individual Agent Reviews

| Agent | Model | Focus | Report |
|-------|-------|-------|--------|
| Clinician | Claude Sonnet | AE/SAE patterns, IRR management, benefit-risk | [clinician_claude-review.md](docs/clinician_claude-review.md) |
| Clinician | GPT-4o | Pediatric neurology, ERT safety comparison | [clinician_gpt-review.md](docs/clinician_gpt-review.md) |
| Biostatistician | Claude Sonnet | Small sample limits, exposure-adjusted rates, CI calculations | [biostat_claude-review.md](docs/biostat_claude-review.md) |
| Patient Safety | GPT-4o | Individual risk tiers, pediatric concerns, protocol safeguards | [patient_safety_gpt-review.md](docs/patient_safety_gpt-review.md) |
| Visual Companion | Claude Sonnet | Figure quality, accessibility, clinical data standards | [visual_claude-review.md](docs/visual_claude-review.md) |
| Visual Companion | GPT-4o | Regulatory compliance, figure-table concordance | [visual_gpt-review.md](docs/visual_gpt-review.md) |

### High-Risk Patients (cross-agent consensus)

| Patient | Cohort | Risk Tier | Key Concern |
|---------|--------|-----------|-------------|
| 0017-9004 | B1 | **HIGH** | 4 SAEs, only drug-related SAE, anaphylactic reaction, hypoxia |
| 0016-9006 | A3 | **HIGH** | 2 unresolved SAEs (dysphagia + mobility), aspiration risk |
| 0017-9007 | A3 | **HIGH** | MRSA + dyskinesia (atypical for MPS IIIA) |
| 0016-9003 | A1 | **HIGH** | Persistent high ADA titers + cognitive disorder SAE |

## AI Pipeline Architecture

This report was generated using a **multi-agent, multi-model pipeline** combining Claude Code (orchestration), Claude API (Anthropic), and GPT API (OpenAI).

### Architecture & Data Pipeline

![MMR Pipeline Architecture](docs/mmr-pipeline-architecture.png)

> **[Open in Excalidraw](docs/mmr-pipeline-architecture.excalidraw)** for interactive editing

### Pipeline Phases

```
Phase 1-3: BUILD                    Phase 4-5: DATA                     Phase 6-7: REVIEW
┌─────────────────────┐            ┌─────────────────────┐            ┌──────────────────────────┐
│ Explore (×2)        │            │ Box MCP Download    │            │ Multi-Model Review       │
│ Plan + Protocol     │───────────▶│ 6 CSV files         │───────────▶│                          │
│ QMD Creator         │            │ Delta Analysis      │            │ ┌──────┐    ┌──────┐     │
│ Main Pipeline       │            │ MMR Generator v2    │            │ │Claude│    │ GPT  │     │
└─────────────────────┘            │ PDF Pipeline        │            │ │Sonnet│    │ 4o   │     │
                                   └─────────────────────┘            │ ├──────┤    ├──────┤     │
                                                                      │ │Clinic│    │Clinic│     │
                                                                      │ │Biost.│    │Pat.Sf│     │
                                                                      │ │Visual│    │Visual│     │
                                                                      │ └──┬───┘    └──┬───┘     │
                                                                      │    └────┬──────┘         │
                                                                      │    Consensus             │
                                                                      │    Synthesizer           │
                                                                      └──────────────────────────┘
```

### Agent Phases (Detailed)

| Phase | Agents | Task |
|-------|--------|------|
| 1. Exploration | 2 Explore agents (parallel) | Codebase structure, study data extraction |
| 2. Planning | Plan + Protocol Explorer | Repo design, efficacy/safety classification from Protocol V6 |
| 3. Implementation | QMD Creator + Main Pipeline | Safety-only QMD template (5,376 lines), HTML report (6.6 MB), scripts |
| 4. Data Integration | Box MCP Download + Delta Analysis | 6 CSV files (3 months), monthly delta comparison |
| 5. Report Generation | MMR Generator v2 + PDF Pipeline | Template-matched reports for JAN/FEB/MAR 2026 |
| 6. Safety Review | 4 Claude Code agents (parallel) | Clinician, biostatistician, patient safety, visual companion |
| 7. Multi-Model Review | 6 API agents (3 Claude + 3 GPT) + Consensus | Independent cross-model safety signal detection and synthesis |

### Multi-Model Review Architecture

```
                    ┌──────────────────────────────────────────┐
                    │  Report HTML → Extract text → Prompts    │
                    └────────┬───────────────────┬─────────────┘
                             │                   │
                    ┌────────▼────────┐ ┌────────▼────────┐
                    │  Claude Sonnet  │ │    GPT-4o       │
                    │  ┌────────────┐ │ │ ┌────────────┐  │
                    │  │ Clinician  │ │ │ │ Clinician  │  │
                    │  ├────────────┤ │ │ ├────────────┤  │
                    │  │ Biostat    │ │ │ │ Pat.Safety │  │
                    │  ├────────────┤ │ │ ├────────────┤  │
                    │  │ Visual     │ │ │ │ Visual     │  │
                    │  └────────────┘ │ │ └────────────┘  │
                    └────────┬────────┘ └────────┬────────┘
                             │                   │
                    ┌────────▼───────────────────▼─────────────┐
                    │       Consensus Synthesizer (Claude)      │
                    │  • Cross-agent agreement matrix           │
                    │  • Divergent finding resolution           │
                    │  • Unified risk assessment                │
                    │  • Blind spot analysis                    │
                    └──────────────────────────────────────────┘
```

### Token Usage

| Session | Tokens (Input) | Tokens (Output) | Cost (est.) | Work Done |
|---------|---------------|-----------------|-------------|-----------|
| Session 1: Initial Pipeline | ~2.5M | ~800K | ~$19.50 | Safety-only template, HTML report, clinician + biostatistician reviews, GitHub repo |
| Session 2: Data Integration | ~1.5M | ~500K | ~$12.00 | Box data download (6 CSVs), delta analysis, MMR generator v1, 3 HTML + 3 PDF reports |
| Session 3: Template Alignment | ~1.5M | ~500K | ~$12.00 | MMR generator v2 (template-matched), 3 HTML + 3 PDF final reports, token tracker |
| Session 4: Multi-Model Review | ~2.0M | ~700K | ~$16.00 | ECG/VS/SAE plots, multi-model agents, template-matched plot styling, compliance rewrite |
| Multi-Model API Calls | ~62K | ~12K | ~$0.34 | 6 agent reviews (Claude+GPT) + consensus synthesis |
| **Total** | **~7.6M** | **~2.5M** | **~$59.84** | **Full pipeline: raw data → validated safety MMR with multi-model review** |

*Note: Token estimates are approximate. Multi-model API costs based on Claude Sonnet ($3/$15 per MTok) and GPT-4o ($2.50/$10 per MTok).*

## Repository Structure

```
DNLI-I-0001-MMR/
├── report/                 # Generated safety reports (3 HTML + 3 PDF per data cut)
├── qmd/                    # R/Quarto template (safety-only, 5,376 lines)
├── scripts/
│   ├── generate_mmr.py     # Main MMR generator (template-matched plots + HTML)
│   ├── multi_model_review.py  # Multi-model safety review (Claude + GPT agents)
│   ├── html_to_pdf.py      # Playwright-based PDF converter
│   ├── gen_corrected_figs.py  # Reference figure generation (R paramplot style)
│   └── legacy/             # Earlier script iterations
├── data/                   # Clinical data inputs (not committed)
├── docs/
│   ├── consensus-safety-review.md        # Multi-model consensus report
│   ├── clinician_claude-review.md        # Claude clinician review
│   ├── clinician_gpt-review.md           # GPT clinician review
│   ├── biostat_claude-review.md          # Claude biostatistician review
│   ├── patient_safety_gpt-review.md      # GPT patient safety review
│   ├── visual_claude-review.md           # Claude visual review
│   ├── visual_gpt-review.md             # GPT visual review
│   ├── patient-safety-review.md          # Patient safety officer review
│   ├── clinician-safety-review-v2.md     # Clinician safety review v2
│   ├── biostatistician-safety-review-v2.md  # Biostatistician review v2
│   ├── multi-model-review-metadata.json  # Token usage & cost tracking
│   ├── pipeline-metadata.md
│   ├── token-consumption-tracker.md
│   └── mmr-pipeline-architecture.png
├── config.yaml             # Study metadata and path configuration
├── .env.example            # API key template (copy to .env)
└── requirements.txt        # Python dependencies
```

## Prerequisites

### R/Quarto Pipeline
- R >= 4.3
- Quarto >= 1.4
- Key R packages: haven, tidyverse, admiral, tern, rtables, ggplot2, gt, patchwork
- XeLaTeX (for PDF rendering)

### Python Pipeline
- Python >= 3.10
- Install: `pip install -r requirements.txt`
- For multi-model review: API keys for Anthropic (Claude) and OpenAI (GPT)

## Quick Start

### Option A: R/Quarto (full report from raw data)
1. Place clinical data in `data/edc/` and vendor files in `data/`
2. Place `I1 Specs.xlsx` in `documents/`
3. `cd qmd && quarto render I-0001-Medical-Monitoring-Report-PDF.qmd`

### Option B: Python (figure generation + HTML/PDF assembly)
1. Update `config.yaml` with paths for the current data cut
2. `python scripts/generate_mmr.py 2026MAR20`
3. `python scripts/html_to_pdf.py report/I-0001-Medical-Monitoring-Report-2026MAR20-SafetyOnly.html`

### Option C: Multi-Model Safety Review
1. Copy `.env.example` to `.env` and add your API keys
2. Generate the report (Option B)
3. Run the multi-model review:
```bash
source .env
python scripts/multi_model_review.py report/I-0001-Medical-Monitoring-Report-2026MAR20-SafetyOnly.html
```

This launches 6 parallel review agents (3 Claude Sonnet + 3 GPT-4o), then synthesizes a consensus report. Output: `docs/consensus-safety-review.md` + 6 individual reviews.

## New Data Cut

1. Update data cut dates in `config.yaml`
2. Place new data extracts in `data/`
3. Re-run pipeline (Option A or B)
4. Run multi-model review (Option C)

## Adapting for Other Denali Studies

This pipeline is designed to be **consistent and reproducible** across Denali ongoing studies. To adapt:

1. **Update constants** in `generate_mmr.py`: `COHORTS`, `SITES`, `TRTDUR`, `IRR_EVENTS`, `DRUG_INTERRUPTED`, `SAE_DATA`
2. **Update `config.yaml`** with new study metadata
3. **Update `MONTH_MAP`** with new data cut dates
4. **Provide CSV data** in `data/<month>/` directories
5. All plots, tables, and safety reviews regenerate automatically

The multi-model review agents are study-agnostic — they parse the generated HTML report and apply safety signal detection to whatever study data is present.

## Safety Review

After generating the report, safety review can be performed at two levels:

### Level 1: Claude Code Agents (built-in)
Launch specialized agents within Claude Code for immediate review:
- **Clinician Safety Reviewer** — AE/SAE patterns, IRR management, benefit-risk
- **Biostatistician** — Statistical rigor, exposure-adjusted rates, data completeness
- **Patient Safety Officer** — Individual risk tiers, pediatric concerns, protocol safeguards
- **Visual Companion** — Figure quality, accessibility, clinical data standards

### Level 2: Multi-Model API Review (independent)
Run `multi_model_review.py` for cross-model validation:
- 3 Claude Sonnet agents + 3 GPT-4o agents review independently
- Consensus synthesizer merges findings and resolves disagreements
- Produces unified risk assessment with confidence levels
- Cost: ~$0.34 per review cycle
