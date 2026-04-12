# DNLI-I-0001 Medical Monitoring Report (MMR)

Safety-focused Medical Monitoring Report template and pipeline for clinical study **DNLI-I-0001** (DNL-126).

## Study Overview

| Item | Value |
|------|-------|
| **Study** | DNLI-I-0001 |
| **Drug** | DNL-126 (ETV:SGSH-BioM) |
| **Indication** | MPS IIIA (Sanfilippo Syndrome Type A) |
| **Phase** | Phase 1/2 |
| **Protocol** | Version 6 (26-Aug-2025) |
| **Subjects** | N=20 across 4 cohorts |
| **Data Cut** | 2026-02-25 (EDC) |

### Cohort Structure

| Cohort | N | Dose Schedule (Protocol V6) |
|--------|---|----------------------------|
| A1 | 4 | 3 mg/kg QW Wks 1-2, then 10 mg/kg Q2W |
| A2 | 4 | 3 mg/kg QW Wks 1-2, then escalate 3 to 6 to 10 mg/kg |
| A3 | 10 | 3 mg/kg QW x6 doses, 6 mg/kg QW x6 doses, 10 mg/kg QW |
| B1 | 2 | 3 mg/kg QW x6 doses, 6 mg/kg QW x6 doses, 10 mg/kg QW |

## Report Sections

1. **Study Status** - Enrollment, disposition, screen failures, current status
2. **Baseline Characteristics** - Demographics, disease baseline (SGSH mutation, ADA, organ volumes)
3. **Study Conduct** - Protocol deviations, dosing compliance, assessment availability
4. **Study Drug Exposure & Immunogenicity** - Exposure plots, compliance profiles, ADA summary
5. **Adverse Events** - TEAEs, IRRs (442 cumulative events), SAEs, AESIs
6. **Safety Laboratory** - Biochemistry, hematology, immune biomarkers, urine chemistry, eDISH
7. **ECG Summary** - QTcF, QRS, HR trend plots with outlier indicators
8. **Vital Signs** - SBP, DBP, pulse, SpO2, temperature (pre-dose, by cohort)

### Data Exclusions

Per Protocol V6 Section 9.1, the following **efficacy data** are excluded from this safety report:
- CSF Heparan Sulfate (primary efficacy endpoint)
- Serum NfL (secondary efficacy endpoint)
- Clinical Outcome Assessment results (KABC, VABS-III, BSID III/IV - exploratory efficacy)

**Urine HS** is included per medical monitor direction. COA **collection compliance** (whether assessed per SOA) is tracked, but actual results are not shown.

## Repository Structure

```
DNLI-I-0001-MMR/
+-- report/             # Generated safety-only HTML report
+-- qmd/                # R/Quarto template (safety-only)
+-- scripts/            # Python figure generation and PDF pipeline
|   +-- legacy/         # Earlier script iterations (reference)
+-- data/               # Clinical data inputs (not committed)
+-- output/             # Generated artifacts (not committed)
+-- docs/               # Supporting documentation
+-- config.yaml         # Study metadata and path configuration
+-- requirements.txt    # Python dependencies
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

## Quick Start

### Option A: R/Quarto (full report from raw data)
1. Place clinical data in `data/edc/` and vendor files in `data/`
2. Place `I1 Specs.xlsx` in `documents/`
3. `cd qmd && quarto render I-0001-Medical-Monitoring-Report-PDF.qmd`

### Option B: Python (figure generation + HTML/PDF assembly)
1. Update `config.yaml` with paths for the current data cut
2. `python scripts/gen_corrected_figs.py`
3. `python scripts/rebuild_mmr.py`
4. `python scripts/gen_mmr_pdf.py`

## New Data Cut

1. Update data cut dates in `config.yaml`
2. Place new data extracts in `data/`
3. Re-run pipeline (Option A or B)

## Safety Review

After generating the report, clinician and biostatistician review agents can be launched to perform safety signal detection focused on:
- AE/SAE emerging patterns and IRR severity trends
- Lab outlier identification and hepatotoxicity screening (eDISH)
- ECG/vital signs anomalies
- Dose-exposure and ADA-safety correlations
- Data completeness and statistical adequacy
