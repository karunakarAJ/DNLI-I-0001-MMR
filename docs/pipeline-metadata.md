# MMR Pipeline Metadata

## Report Generation Date
2026-04-12

## Data Cut
EDC Snapshot: 2026-02-25

---

## Agent Pipeline Summary

### Phase 1: Exploration (Parallel)

| Agent | Type | Task | Status |
|-------|------|------|--------|
| Explore Agent 1 | `Explore` | Explore MMR folder structure — identify all files, templates, data | Completed |
| Explore Agent 2 | `Explore` | Extract DNLI-I-0001 study data, report format, guidelines | Completed |

### Phase 2: Planning

| Agent | Type | Task | Status |
|-------|------|------|--------|
| Plan Agent | `Plan` | Design repo structure, file inclusion/exclusion, README, .gitignore | Completed |
| Protocol Explorer | `Explore` | Extract safety/efficacy classification from Protocol V6 (Box file ID: 2073510585232) | Completed |

### Phase 3: Implementation

| Agent | Type | Task | Tokens | Tool Uses | Duration | Status |
|-------|------|------|--------|-----------|----------|--------|
| QMD Template Creator | `general-purpose` | Strip efficacy from QMD, create safety-only template | 123,997 | 63 | 5m 25s | Completed |
| Main Pipeline | Direct (no agent) | HTML report creation, scripts copy, supporting files, git push | — | — | — | Completed |

### Phase 4: Review (Parallel)

| Agent | Type | Task | Tokens | Tool Uses | Duration | Status |
|-------|------|------|--------|-----------|----------|--------|
| Clinician Safety Reviewer | `general-purpose` | Clinical safety signal detection across all 8 sections | 53,415 | 40 | 4m 3s | Completed |
| Biostatistician Safety Reviewer | `general-purpose` | Statistical safety analysis, data completeness, eDISH validation | 58,465 | 42 | 6m 12s | Completed |

### Total Pipeline Agents: 7

---

## Token Usage Summary

| Component | Input Tokens | Output Tokens | Total Tokens |
|-----------|-------------|---------------|--------------|
| QMD Template Creator | — | — | 123,997 |
| Clinician Reviewer | — | — | 53,415 |
| Biostatistician Reviewer | — | — | 58,465 |
| **Subtotal (agents)** | — | — | **235,877+** |

*Note: Exploration and Plan agent token counts not captured in task notifications. Main conversation tokens are separate.*

---

## Files Generated

| File | Size | Description |
|------|------|-------------|
| `report/I-0001-Medical-Monitoring-Report-2026FEB25-SafetyOnly.html` | 6.6 MB | Safety-only HTML report (CSF HS & COA results removed) |
| `qmd/I-0001-Medical-Monitoring-Report-PDF.qmd` | 5,376 lines | Safety-only R/Quarto template |
| `docs/clinician-safety-review.md` | — | Clinician signal detection review |
| `docs/biostatistician-safety-review.md` | — | Biostatistician statistical review |
| `docs/pipeline-metadata.md` | — | This file |
| `scripts/gen_corrected_figs.py` | 29 KB | Primary figure generator (76 figures) |
| `scripts/rebuild_mmr.py` | 12 KB | HTML figure injection |
| `scripts/gen_mmr_pdf.py` | 17 KB | HTML to PDF conversion |
| `config.yaml` | — | Study metadata and configuration |
| `README.md` | — | Project documentation |

---

## Data Exclusions Applied

| Excluded Data | Protocol Classification | Verification |
|---------------|------------------------|-------------|
| CSF Heparan Sulfate | Primary efficacy (Sec 9.1.1) | grep "CSF Heparan" = 0 matches |
| CSF HS normalization | Secondary efficacy (Sec 9.1.2.4) | grep "CSF Dermatan" = 0 matches |
| Serum NfL | Secondary efficacy (Sec 9.1.2.3) | — |
| KABC scores | Exploratory efficacy (Sec 8.11) | grep "KABC" = 0 in data sections |
| VABS-III scores | Exploratory efficacy (Sec 8.11) | grep "Vineland-3" = 0 matches |
| BSID III/IV scores | Exploratory efficacy (Sec 8.11) | grep "Bayley3" = 0 matches |

| Kept Data | Reason | Verification |
|-----------|--------|-------------|
| Urine HS | Medical monitor direction | grep "Urine" = 2 matches |
| SGSH Genotype | Eligibility/safety (Sec 8.2) | grep "SGSH" = 4 matches |
| ADA | Immunogenicity (Sec 9.4.6) | grep "ADA" = 740 matches |
| eDISH | Safety hepatotoxicity screen | grep "eDISH" = 2 matches |
| IRR data | Safety (Sec 9.4.5) | grep "IRR" = 41 matches |

---

## Review Comments Summary

### Clinician Safety Reviewer — Key Findings

**Overall Benefit-Risk: Favorable**

| Domain | Risk Level | Key Signal |
|--------|-----------|------------|
| IRR | **MEDIUM-HIGH** | 442 events, 75% moderate-severe, 1 anaphylactic reaction (B1 cohort) |
| AE/SAE Pattern | MEDIUM | 15 SAEs in 13/20 participants; 0017-9004 has 4 SAEs (highest burden) |
| Immunogenicity/ADA | MEDIUM | 95% ADA+, 60% neutralizing; correlates with IRR severity |
| Vital Signs | LOW-MEDIUM | SpO2 <92% in 2 participants; pyrexia in 80% (expected for ERT) |
| Dose-Response | LOW-MEDIUM | No dose-dependent worsening; IRR attenuates over time |
| Hepatotoxicity | LOW | eDISH clean — 0/20 ALT >3xULN, 0/20 TBILI >1.5xULN |
| ECG | LOW | QTcF >450ms in 3/20 — single observations, IRR-related |

**Priority Action Items:**
1. Re-adjudicate 0017-9004 hypoxia SAE causality (currently "Not Related" despite prior drug-related IRR SAE + anaphylaxis)
2. Update anaphylaxis protocols at all sites; consider augmented pre-medication for youngest participants
3. Request formal ADA titer vs IRR frequency/severity correlation analysis
4. Request individual ALT/AST/TBILI trending plots (sub-threshold monitoring)
5. Review 0016-9006 unresolved SAEs (mobility decreased Day 93, dysphagia Day 119) — disease progression vs drug effect
6. Discuss 0017-9007 dyskinesia SAE at next DSMB — atypical for MPS IIIA
7. Convene DEC for pre-medication protocol escalation review

### Biostatistician Safety Reviewer — Key Findings

**Overall: Acceptable hepatic safety; IRR dominant signal; formal between-cohort testing not powered (N=20)**

| Domain | Key Finding |
|--------|------------|
| Data Completeness | Visit-level completion rates NOT available — data gap; lab data lag of 12 days |
| IRR Exposure-Adjusted Rates | A3: 66.2/100 person-wks, B1: 54.5 vs A1: 27.6, A2: 25.0 — consistent with time-dependent decline |
| SAE Temporal Analysis | No clustering; 3 pre-dose SAEs inflate A3 count; 0017-9004 drives 27% of all SAEs |
| eDISH Validation | Confirmed clean (0/20 Hy's Law); **max xULN values not reported** — safety margin unknown |
| ADA-IRR Correlation | 95% ADA+, 100% IRR — near-zero variability; titer-level analysis needed |
| Small Sample Power | Min detectable AE rate: 7.8% (N=20), 33% (N=4), 55% (N=2); drug-related SAE 95% CI: 0.1–24.9% |
| Dose Compliance | A1 >=96% (highest), B1 >=91% (lowest); 60% with >=1 dose interruption |

**Priority Recommendations:**
1. Request individual-level lab xULN values for quantitative eDISH safety margin
2. Exposure-adjusted IRR analysis by treatment epoch (Wk 1-12, 13-26, 27-52, 52+)
3. Dose-level IRR analysis (3/6/10 mg/kg periods) using ex.sas7bdat
4. Visit completion matrix from EDC for differential missingness assessment
5. ADA titer vs IRR Spearman correlation using individual Bioagilytix data
6. 0017-9004 dedicated safety narrative (4 SAEs, only drug-related SAE)
7. Longitudinal lymphocyte trending in A1 (107 weeks exposure)
8. Pre-specify DSMB statistical analysis plan for OLE/LTE phases

---

## GitHub Repository
- **URL:** https://github.com/karunakarAJ/DNLI-I-0001-MMR
- **Visibility:** Public
- **Branch:** main
