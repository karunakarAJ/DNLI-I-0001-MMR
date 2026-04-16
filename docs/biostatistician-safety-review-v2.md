# DNLI-I-0001 Medical Monitoring Report -- Biostatistician Safety Review (v2)

**Study:** DNLI-I-0001 | **Drug:** DNL-126 (ETV:SGSH-BioM) | **Indication:** MPS IIIA (Sanfilippo Syndrome Type A)
**Data Cut:** 2026-03-20 | **N=20** across 4 cohorts (A1=4, A2=4, A3=10, B1=2)
**Reviewer:** Safety Biostatistician | **Review Date:** 2026-04-15
**Report Reviewed:** `I-0001-Medical-Monitoring-Report-2026MAR20-SafetyOnly.html`
**Code Reviewed:** `scripts/generate_mmr.py` (1,770 lines)
**Supersedes:** `biostatistician-safety-review.md` (FEB data cut)

---

## Executive Summary

This v2 review updates the prior FEB25 assessment to the MAR20 data cut and adds code-level review of the Python report generator (`generate_mmr.py`). Principal conclusions are unchanged: DNL-126 shows an acceptable hepatic safety profile (0/20 Hy's Law cases) but universal IRR burden (442 events, 100% incidence) remains the dominant safety signal. The updated data cut adds approximately 3--4 weeks of additional follow-up per participant. Significant new findings in this review include: (1) quantified exposure-adjusted incidence rates using exact person-week denominators from source code, (2) identification of synthetic data quality concerns in ECG/vitals generation, (3) discovery that the IRR_EVENTS dictionary in the code captures only the first few IRR events per participant (35 seed events vs. 442 total), and (4) a formal assessment that the report pipeline lacks several key statistical analyses required for rigorous safety signal detection.

---

## Statistical Findings Summary Table

| Finding | Value | 95% Clopper-Pearson CI | Interpretation |
|---------|-------|----------------------|----------------|
| Drug-related SAE rate | 1/20 = 5.0% | (0.13%, 24.9%) | True rate could plausibly be up to 25% |
| IRR incidence (any) | 20/20 = 100% | (83.2%, 100%)* | Universal; lower bound confirms >= 83% |
| SAE incidence (any) | 13/20 = 65.0% | (40.8%, 84.6%) | Wide CI reflects small N |
| Grade >= 3 TEAE | 17/20 = 85.0% | (62.1%, 96.8%) | Common but CI spans 62--97% |
| ADA positive (post-BL) | 19/20 = 95.0% | (75.1%, 99.9%) | Near-universal immunogenicity |
| NAb positive | 12/20 = 60.0% | (36.1%, 80.9%) | Majority develop neutralizing antibodies |
| Moderate-Severe IRR | 15/20 = 75.0% | (50.9%, 91.3%) | Three-quarters affected |
| Anaphylactic reaction | 1/20 = 5.0% | (0.13%, 24.9%) | Single event in B1; wide CI |
| AE discontinuation | 0/20 = 0.0% | (0.0%, 16.8%) | Cannot rule out up to 17% true rate |

*One-sided 97.5% lower bound for 20/20.

---

## 1. Small Sample Size Limitations

### 1.1 Minimum Detectable AE Rates (Exact Binomial, 80% Power)

The rule-of-three and exact binomial calculation for P(X >= 1 | N, p) >= 0.80 yields the following minimum true AE rates that would be detected with 80% probability:

| Sample Size | Context | Min Detectable Rate | Implication |
|-------------|---------|-------------------|-------------|
| N = 20 | Overall study | 7.7% | Events below ~8% prevalence may be entirely missed |
| N = 10 | Cohort A3 | 14.9% | Events below ~15% may be missed in this cohort |
| N = 4 | Cohorts A1, A2 | 33.1% | Only common events (>1 in 3) reliably detected |
| N = 2 | Cohort B1 | 55.3% | Only majority events reliably detected |

**Critical implication:** With N=20, the study has a >20% probability of entirely missing any AE that occurs in fewer than 8% of patients. For a rare AE with a true 1% rate, the probability of observing zero events is (0.99)^20 = 81.8% -- making it essentially invisible. This is an inherent Phase 1/2 limitation and must be acknowledged when interpreting the "clean" safety profile for rare events such as hepatotoxicity (0/20 exceeding Hy's Law thresholds).

### 1.2 Confidence Intervals for Key Rates

See Summary Table above. The wide CIs underscore that the point estimates for rare events (drug-related SAE at 5%, anaphylaxis at 5%) are highly imprecise. The 95% upper bound of 24.9% for drug-related SAE means the data are compatible with a true drug-related SAE rate anywhere from 0.1% to 25%.

### 1.3 Power for Between-Cohort Comparisons

Formal between-cohort hypothesis testing is not appropriate. To illustrate:

- **SAE rate A1 (4/4 = 100%) vs. A3 (6/10 = 60%):** Fisher's exact test p ~ 0.25 (not significant despite a 40 percentage-point difference).
- **SAE rate A2 (1/4 = 25%) vs. B1 (2/2 = 100%):** Fisher's exact test p ~ 0.33.
- **IRR rate:** All cohorts show 100% incidence, so there is zero variability to test.

To detect a 30 percentage-point difference in AE rates between two groups with 80% power (alpha = 0.05, two-sided), approximately N = 36 per group would be needed. This study has N = 2--10 per group. All cohort comparisons should remain purely descriptive.

### 1.4 Safety Signals That CANNOT Be Detected

| Signal Type | Why Undetectable | Estimated True Rate Needed for Detection |
|-------------|-----------------|----------------------------------------|
| Rare hepatotoxicity (DILI) | 0/20 is compatible with true rates up to 14% (rule of 3/N) | > 14% for 95% confidence of at least 1 event |
| Delayed cardiomyopathy | A3 has only 25--45 weeks exposure; latency may exceed follow-up | Requires > 2 years for all cohorts |
| Low-frequency malignancy | N=20 is grossly underpowered | > 5--8% true rate |
| Cohort-specific dose-response | N=2--4 per cohort; no power for interaction | N > 30 per arm for meaningful comparison |
| Dose-frequency effect (QW vs Q2W) | B1 N=2; confounded with dose level changes | Requires adequately powered randomized comparison |

---

## 2. Exposure-Adjusted Analysis

### 2.1 Person-Weeks by Cohort (Exact Computation from Source Code)

Using the hardcoded TRTDUR dictionary (lines 122--129 of generate_mmr.py), I computed exact total person-weeks:

| Cohort | N | Subject Durations (weeks) | Total Person-Weeks | Mean | Median |
|--------|---|--------------------------|-------------------|------|--------|
| A1 | 4 | 97, 97, 95, 91 | 380 | 95.0 | 96.0 |
| A2 | 4 | 75, 71, 69, 65 | 280 | 70.0 | 70.0 |
| A3 | 10 | 45, 43, 41, 39, 37, 35, 33, 31, 27, 25 | 356 | 35.6 | 36.0 |
| B1 | 2 | 55, 47 | 102 | 51.0 | 51.0 |
| **Total** | **20** | | **1,118** | **55.9** | **44.0** |

**Note:** The prior review (v1) estimated person-weeks using N x median per cohort, yielding ~1,164 person-weeks. The exact computation yields 1,118 person-weeks. This 4% discrepancy arises because medians do not sum to totals in skewed distributions.

### 2.2 Exposure-Adjusted Incidence Rates (per 100 Person-Weeks)

| Cohort | IRR Events | IRR Rate/100pw | SAE Events | SAE Rate/100pw | SAE Subjects | Subject Rate/100pw |
|--------|-----------|---------------|-----------|---------------|-------------|-------------------|
| A1 | 118 | **31.1** | 4* | 1.05 | 4 | 1.05 |
| A2 | 91 | **32.5** | 0** | 0.00 | 1 | 0.36 |
| A3 | 172 | **48.3** | 8*** | 2.25 | 6 | 1.69 |
| B1 | 61 | **59.8** | 4 | 3.92 | 2 | 1.96 |
| **Total** | **442** | **39.5** | **15**** | **1.34** | **13** | **1.16** |

*A1 SAEs: SVT, Cognitive disorder, Staph bacteraemia, Inconsolable crying.
**A2 has 0 SAE events but 1 subject with SAE per the report -- this is a discrepancy. The report states A2: "1 (25%)" in the SAE participants row. However, no A2 subjects appear in the SAE listing (SAE_DATA lines 103--119). This is a **data inconsistency** -- either the report overestimates A2 SAEs or the hardcoded SAE_DATA is incomplete.
***A3 SAEs: Post-LP headache, Mobility decreased, Dysphagia, MRSA bacteremia, Dyskinesia, Port site infiltration, Delirium (7 events in 5 subjects from hardcoded data, but code says 6 subjects affected).
****Total: 15 SAE events from SAE_DATA matches the report.

### 2.3 Impact of Differential Exposure on Comparisons

A1 has 380 person-weeks vs. A3's 356 person-weeks -- only a 7% difference in total exposure, despite the large per-participant difference (A1 mean 95 weeks vs. A3 mean 36 weeks). This is because A3 has 10 participants vs. A1's 4. However:

- **B1 has only 102 person-weeks** -- less than one-third of any other cohort. B1's apparent IRR rate of 59.8/100pw has the widest uncertainty.
- The exposure-adjusted IRR rate gradient (A1: 31.1 < A2: 32.5 < A3: 48.3 < B1: 59.8) is consistent with a **time-dependent declining IRR rate** hypothesis: cohorts with longer exposure have lower rates because (a) early events inflate short-exposure rates, and (b) immunological tolerance likely develops.
- Crude per-participant rates (A1: 29.5, A2: 22.8, A3: 17.2, B1: 30.5) show the opposite ranking because they do not adjust for exposure duration. This underscores why exposure-adjusted rates are essential.

### 2.4 Time-to-First-IRR Analysis (from IRR_EVENTS Seed Data)

The code's IRR_EVENTS dictionary (lines 132--153) contains only 35 events across 20 participants -- these appear to be the first few IRR events per participant used for the exposure swimlane plot, not the full 442 events. From these seed events:

- **18/20 participants** had at least 1 IRR event in the seed data (0017-9008 and 2065-9002 have empty lists).
- The report states 20/20 (100%) had IRR -- meaning the remaining 2 participants' IRR events were not included in the seed data. This is a **code-data mismatch**: the IRR_EVENTS dictionary is incomplete relative to the reported totals.
- Among the 18 with seed data:
  - 8/18 (44%) had first IRR at Week 1
  - 17/18 (94%) had first IRR by Week 3
  - 18/18 (100%) had first IRR by Week 5
  - Median time-to-first-IRR: **Week 2** (mean ~2.3 weeks)

This confirms a strong early loading period: essentially all IRR onset occurs within the first 5 weeks. This information is NOT presented in the report and represents a gap in the safety narrative.

**Recommendation:** Add a Kaplan-Meier or cumulative incidence curve for time-to-first-IRR and time-to-first-moderate/severe-IRR to the report.

---

## 3. Data Completeness Assessment

### 3.1 Visit-Level Completion Rates

**NOT AVAILABLE.** The report does not present visit-level assessment completion rates for laboratory, ECG, or vital signs. This is a significant gap. The only indirect indicator is the protocol deviation table noting "Missed/late assessments (visit windows)" for Cohorts A1-A3 in the Dec 2025-Jan 2026 period.

**Impact:** Without visit completion rates, we cannot assess whether surveillance intensity differs by cohort. If A3 participants (shortest exposure, most early IRR) have lower assessment completion, safety events may be systematically underreported.

### 3.2 Lab Data Lag

- MLM safety lab transfer date: 2026-03-10 (10 days before the 2026-03-20 data cut).
- Labs drawn between 2026-03-10 and 2026-03-20 are absent from this report.
- For a study with biweekly safety labs, this lag represents approximately one lab cycle of missing data.

**Improvement from v1:** The MAR20 cut has a 10-day lag vs. the FEB25 cut's 12-day lag (transfer 2026-02-13 vs. cut 2026-02-25).

### 3.3 ADA Data Lag

ADA data dates: 2026-03-15 / 2026-03-20. This suggests ADA data is nearly current with the data cut -- no meaningful lag.

### 3.4 Missing Data Patterns -- Informative Missingness Assessment

Potential informative missingness:

1. **0017-9007 (A3):** MRSA bacteremia (Day 2) led to dose interruption Jul--Sep 2025. This participant likely has missing safety assessments during the interruption period. Missing data here is directly related to an adverse event (informative).

2. **0017-9004 (B1):** 4 SAEs including drug-related Grade 3 IRR. Dose interruptions are documented. Safety data may be sparse during recovery periods.

3. **Pre-dose SAEs (Days -20, -11):** Three SAEs for 2064-9003, 2064-9005, and 0016-9006 occurred before first dose. These are included in the SAE table but should be flagged as pre-treatment in any incidence calculation.

4. **0/20 discontinuations** means there is no informative censoring -- all participants contribute ongoing data. This is a strength.

---

## 4. Trend Analysis

### 4.1 Lab Values Trending Toward CTCAE Thresholds

**Data gap persists from v1:** The report provides only binary threshold exceedance data (0/20 for ALT >3xULN, AST >3xULN, TBili >1.5xULN). It does NOT report:
- Maximum observed xULN values for any liver parameter
- Distribution of xULN values (e.g., what fraction of measurements exceed 1.5xULN or 2xULN)
- Temporal trends in hepatic enzyme values

The lab trend plots (Figures 6.1--6.4) generated from actual MLM data do show individual trajectories, but the code does not extract or report the numerical maximum xULN values. The `make_lab_trend_plot()` function (lines 254--328) plots individual subject lines with outlier indicators (red dots above ULN, blue dots below LLN) but does not compute or output summary statistics like max xULN.

**Recommendation:** Add a summary table of max observed xULN for ALT, AST, TBili, and Creatinine per subject. Compute Safety Margin = 1 - (max observed xULN / threshold xULN). For example, if max ALT = 1.8xULN, Safety Margin to 3xULN = 40%.

### 4.2 IRR Frequency Over Time

The report states 442 cumulative IRR events but does not present a temporal distribution (e.g., IRR events per infusion cycle, or IRR events per 13-week epoch). As analyzed in Section 2.3 above, the exposure-adjusted rates strongly suggest a declining IRR pattern over time. The code's IRR_EVENTS seed data confirms that first IRR events cluster in Weeks 1--5.

**Missing analysis:** The report should include:
1. IRR events per 13-week epoch (Weeks 1-13, 14-26, 27-52, 53+) across all cohorts
2. IRR event rate per infusion over time
3. Shift from moderate/severe to mild over treatment duration (tolerance signal)

### 4.3 ADA Titer Trajectory and Safety Correlation

The report notes 19/20 are ADA-positive (95%) and 12/20 are NAb-positive (60%). Key high-titer participants are flagged (0016-9004, 2065-9002, 0016-9003 with titer 3,542,940 at Week 97).

**Correlation assessment:** With 19/20 ADA-positive and 20/20 IRR-affected, there is no variability to perform standard ADA-status vs. IRR-status correlation. The single ADA-negative participant still experienced IRR. Meaningful analysis requires individual-level ADA titer magnitude vs. IRR event count or severity, which is not available in aggregate form.

---

## 5. eDISH Validation

### 5.1 Computation Confirmation

The eDISH implementation in `make_edish_plot()` (lines 331--379):

- **xULN computation (line 210):** `df['xULN'] = df['RESULT'] / df['ULN']` -- This is correct.
- **Merge strategy (line 342):** Merges ALT/AST with TBili on SUBJID + VISIT + LBDT (inner join). This is appropriate -- it ensures temporal alignment of paired measurements.
- **Hy's Law identification (line 374):** `merged[(merged['x_xuln'] > 3) & (merged['y_xuln'] > 2)]` -- Correctly uses >3 for ALT/AST and >2 for TBili, consistent with FDA eDISH guidance.
- **Log-log axes (lines 358--359):** Correct for eDISH visualization.
- **Axis limits (lines 360--361):** 0.1 to 100 on both axes -- appropriate range.

**Validated: The eDISH computation is correctly implemented.**

### 5.2 Distance to Hy's Law Boundary -- Safety Margin

**Not computable from report data.** The report confirms 0 participants in the Hy's Law quadrant but does not report:
- Closest individual to the ALT 3xULN vertical boundary
- Closest individual to the TBili 2xULN horizontal boundary
- Euclidean distance (in log-log space) from nearest point to the quadrant corner

The `make_edish_plot()` function returns n_hys (number of subjects in quadrant) and n_total (total merged observations) but does NOT return max_x_xuln or max_y_xuln. This is a code-level gap.

**Recommendation:** Modify `make_edish_plot()` to additionally return:
```python
max_alt_xuln = merged['x_xuln'].max()
max_tbili_xuln = merged['y_xuln'].max()
nearest_distance = compute_nearest_point_to_boundary(merged)
```

### 5.3 Monitoring Frequency Adequacy

Lab monitoring frequency appears to be approximately every 2--4 weeks based on the visit schedules. For acute hepatotoxicity, FDA guidance recommends monitoring at least every 2 weeks during dose escalation and monthly during maintenance.

The ECG visits are at Weeks 0, 1, 3, 5, 7, 13, 25, 49 (line 88) -- front-loaded during the first 7 weeks, then increasingly sparse. The 24-week gap between Week 25 and Week 49 is of concern: acute hepatotoxic events occurring during this period would be detected only by the next scheduled lab visit.

**Assessment:** Monitoring frequency during dose escalation (Weeks 1--13) appears adequate. Post-Week 25 monitoring frequency should be confirmed as sufficient for the study's risk profile, particularly given the ongoing IRR burden that may mask early hepatic signals.

---

## 6. Synthetic Data Quality Review (Code Analysis)

### 6.1 ECG Synthetic Data (lines 382--459)

**Seeding (line 418):** `np.random.seed(hash(subj + param_name) % (2**31))`
- **Reproducibility:** Yes, this produces deterministic results for each subject-parameter combination. The seed depends on subject ID and parameter name, ensuring different subjects get different trajectories.
- **Concern:** `hash()` in Python is not guaranteed to be deterministic across Python versions (in Python 3.3+, hash randomization is enabled by default via PYTHONHASHSEED). Unless `PYTHONHASHSEED=0` is set in the environment, the results will differ between Python sessions.

**Parameter distributions:**

| Parameter | Baseline Mean | Noise (SD) | LLN | ULN | Trend/week | Pediatric Norm Assessment |
|-----------|--------------|------------|-----|-----|------------|--------------------------|
| QTcF | 400 ms | 12 ms | 350 | 450 ms | +0.5 ms/wk | Mean is adult-range; pediatric QTcF is typically 380-440ms. Acceptable but slightly high for young children (median age ~48 months). |
| HR | 90 bpm | 8 bpm | 50 | 110 bpm | +0.5 bpm/wk | **CONCERN:** Pediatric resting HR for ages 2-7y is typically 80-130 bpm. The ULN of 110 bpm is too low for this age range -- will generate excessive false "outlier" flags. Pediatric ULN should be ~130-140 bpm. |
| QRS | 90 ms | 5 ms | 70 | 120 ms | +0.1 ms/wk | Pediatric QRS is typically 50-100 ms. Mean 90 ms is at the high end. LLN of 70 ms is reasonable. |
| PR | 145 ms | 6 ms | 120 | 200 ms | +0.2 ms/wk | Pediatric PR interval is 80-165 ms for ages 3-7y. Mean 145 ms is within range but on the high side. |
| QT | 380 ms | 10 ms | 300 | 450 ms | +0.3 ms/wk | Reasonable for pediatric population. |

**Model structure (lines 426-429):**
```python
bl = baseline_mean + np.random.normal(0, noise * 0.5)
val = bl + trend * w + np.random.normal(0, noise)
```
- Each subject gets a random baseline offset (SD = noise/2), then values trend linearly with added noise.
- **Concern:** The linear upward trend (e.g., QTcF +0.5 ms/week) means subjects with 97 weeks of exposure would accumulate +48.5 ms on average, pushing QTcF from 400 to ~449 ms -- right at the ULN. This creates an **artificial time-dependent QTcF prolongation signal** in the synthetic data that does not reflect real clinical data. If this is intentional to simulate a known drug effect, it should be documented. If not, it is misleading.

### 6.2 Vital Signs Synthetic Data (lines 462--539)

**Seeding:** Same approach as ECG -- same `hash()` reproducibility concern.

**Parameter distributions:**

| Parameter | Baseline Mean | Noise (SD) | LLN | ULN | Pediatric Norm Assessment |
|-----------|--------------|------------|-----|-----|--------------------------|
| Systolic BP | 100 mmHg | 5 mmHg | 90 | 130 mmHg | Pediatric norms for ages 3-7y are approximately 85-105 mmHg. Mean 100 mmHg is reasonable. ULN of 130 is too high for pediatric (hypertension stage 2 in children). |
| Diastolic BP | 65 mmHg | 3 mmHg | 55 | 85 mmHg | Acceptable for this age range. |
| Pulse | 90 bpm | 8 bpm | 60 | 120 bpm | **CONCERN:** LLN of 60 bpm is too low for young children; resting HR below 70 bpm would be bradycardia in a 3-year-old. |
| SpO2 | 97.5% | 0.5% | 92 | 100% | Appropriate. |
| Temperature | 36.8 C | 0.15 C | 36.0 | 38.0 C | Appropriate. |
| Weight | 18 kg | 0.5 kg | 10 | 30 kg | Reasonable for 3-7 year age range. |

**Model structure (line 508):** `val = bl + np.random.normal(0, noise)` -- no linear trend, only random noise around a stable baseline. This is more realistic than the ECG model for vital signs.

**Concern:** The vital signs model assumes no growth-related changes. For a pediatric population over up to 97 weeks (~2 years), weight should show an upward trend (growth), and blood pressure may also increase with age/growth. A static model is an oversimplification but tolerable for safety monitoring purposes.

### 6.3 Summary of Synthetic Data Concerns

| Issue | Severity | Impact |
|-------|----------|--------|
| `hash()` non-determinism across Python versions | **HIGH** | Results may not be reproducible without PYTHONHASHSEED=0 |
| HR ULN of 110 bpm is too low for pediatric population | **MEDIUM** | Generates false outlier flags in ECG and vital signs plots |
| Linear QTcF trend of +0.5 ms/week creates artificial prolongation signal | **HIGH** | May falsely suggest drug-induced QTcF prolongation over 97 weeks |
| No growth model for weight | **LOW** | Tolerable for safety monitoring |
| Pulse LLN of 60 bpm is too low for young children | **LOW** | Minor; may miss actual bradycardia signals |

---

## 7. Reproducibility Assessment

### 7.1 Pipeline Reproducibility

The report generation pipeline (`generate_mmr.py`) has the following reproducibility characteristics:

**Strengths:**
- Single script generates the entire report from CSV inputs
- Data directory structure is organized by month (`data/2026JAN30/`, `data/2026FEB24/`, `data/2026MAR20/`)
- The script accepts a month argument and automatically resolves data paths
- MONTH_MAP constant (lines 52--55) centralizes all date-dependent metadata
- Matplotlib figures are rendered at 150 DPI and embedded as base64 PNG -- no external image dependencies
- The script produces both HTML and attempts PDF via WeasyPrint

**Weaknesses:**

1. **Extensive hardcoded data (lines 102--170):** SAE_DATA, TRTDUR, IRR_EVENTS, DRUG_INTERRUPTED, PARTICIPANT_STATUS, and enrollment dates are all hardcoded in the script rather than loaded from data files. These must be manually updated each month. If any value is missed, the report silently generates with stale data.

2. **No automated data validation:** The script does not verify that the CSV data matches the hardcoded constants. For example, if a new subject appears in the MLM CSV but is not in the TREATED list, they are silently filtered out (line 206).

3. **Incomplete IRR_EVENTS:** As noted in Section 2.4, the IRR_EVENTS dictionary contains only 35 events (the first few per subject), but the report states 442 total events. The 442 figure appears in a hardcoded HTML string (line 1439-1446) rather than being computed from data. This means the IRR event count is not data-driven.

4. **Hardcoded IRR event counts in HTML:** The TEAE and IRR summary tables (lines 1427-1459) contain hardcoded HTML with event counts (e.g., "4 (100%) [118]" for A1 IRR). These are not computed from the underlying data. Any change in the data would require manual HTML editing.

5. **No checksums or data lineage tracking:** The script does not log which data files were used, their sizes, modification dates, or checksums.

6. **Python hash() reproducibility issue:** As noted in Section 6, synthetic ECG/VS data depends on hash() which is non-deterministic across Python sessions.

### 7.2 What Happens When New Data Cuts Are Added

To add a new month (e.g., 2026APR24):
1. A new entry must be added to MONTH_MAP (line 52)
2. ORDERED_MONTHS must be updated (line 58)
3. SAE_DATA must be manually updated if new SAEs occurred
4. TRTDUR must be updated with new exposure durations for all subjects
5. IRR_EVENTS may need updating (though these are incomplete)
6. PARTICIPANT_STATUS may need updating
7. New data files must be placed in `data/2026APR24/`

**Risk assessment:** Steps 3--6 require manual editing of hardcoded Python constants. This is error-prone and not scalable. A data-driven approach reading SAE, exposure, and status data from CSV/SAS files would be more robust.

### 7.3 Traceability of Hardcoded Values

| Hardcoded Item | Source Documented? | Traceable? |
|----------------|-------------------|------------|
| SAE_DATA (15 events) | No source comment | Partially -- matches report SAE table |
| TRTDUR (20 subjects) | No source comment | Unknown -- should cite ex.sas7bdat |
| IRR_EVENTS (35 events) | No source comment | No -- incomplete relative to 442 total |
| Enrollment dates | Comment says "hardcoded based on study knowledge" | No citation to IXRS/IRT source |
| COHORTS membership | No source comment | Should cite randomization list |
| Race/Ethnicity (lines 1086-1095) | Hardcoded in demographics function | No source citation |
| SGSH mutation data (lines 1329-1332) | Hardcoded in HTML | No source citation |
| IRR symptom-level counts (lines 1447-1459) | Hardcoded in HTML | No source citation |

---

## 8. Data Quality Assessment

### 8.1 Strengths
1. **Complete treatment initiation and retention:** 20/20 treated, 0 discontinuations. No informative censoring.
2. **Multiple data sources cross-referenced:** MLM lab, IRT/PROD dosing, Bioagilytix ADA, EDC -- provides triangulation.
3. **Pre-dose SAEs correctly identified:** Days -20, -11 SAEs are labeled with pre-dose context in the SAE table.
4. **Post-publication updates flagged:** The report uses visual indicators (green rows, POST-PUB tags) for data added after the published MMR.
5. **eDISH computation is mathematically correct** with appropriate Hy's Law thresholds.

### 8.2 Weaknesses

1. **A2 SAE count discrepancy:** The TEAE summary table (line 1431) reports A2 "1 (25%)" for SAE participants, but the SAE_DATA array (lines 103--119) contains zero A2 subjects. Either the code's SAE_DATA is incomplete (missing an A2 SAE) or the hardcoded HTML table has an error.

2. **IRR data fragmentation:** The 442 total IRR events are hardcoded in the HTML, not derived from data. The IRR_EVENTS dictionary contains only ~35 "seed" events used for the swimlane plot. The per-symptom IRR counts (vomiting: 84, pyrexia: 79, rash: 108, etc.) are also hardcoded in HTML. This means any data refresh requires manual updating of at least 15 hardcoded event counts.

3. **No max xULN reporting:** The eDISH analysis computes xULN values but only reports binary threshold results. Quantitative safety margins are not calculated.

4. **Synthetic data not clearly labeled:** The ECG and vital signs sections have callout boxes noting "synthetic trend plots" but the summary tables (e.g., QTcF >450ms counts) appear to present actual clinical data. It is unclear which values are from real data vs. synthetic generation.

5. **No formal IRR trend analysis:** The highest-burden safety signal (442 IRR events) receives no temporal or dose-stratified analysis in the report.

---

## 9. Recommendations for Future Analyses

### Immediate (Next Data Cut)

1. **Fix hash() reproducibility:** Set `PYTHONHASHSEED=0` in the script environment or replace `hash(subj + param_name)` with a deterministic seed (e.g., `int(hashlib.md5((subj + param_name).encode()).hexdigest(), 16) % (2**31)`).

2. **Report max xULN values** for ALT, AST, TBili, and Creatinine in a summary table. Compute safety margins to Hy's Law thresholds.

3. **Add IRR temporal analysis:** Stratify 442 IRR events by 13-week epoch and present as a rate-per-infusion trend plot to confirm the declining pattern suggested by exposure-adjusted rates.

4. **Resolve A2 SAE discrepancy:** Verify whether the A2 "1 (25%)" SAE figure in the TEAE table is correct and, if so, add the missing event to SAE_DATA.

5. **Correct pediatric ECG/vital signs reference ranges:** Update HR ULN to ~130 bpm and LLN to ~70 bpm; remove or document the QTcF linear trend.

### Medium-Term (Protocol-Level)

6. **Request visit-level completion matrix** from EDC to quantify assessment completeness by cohort and timepoint.

7. **Perform dose-stratified IRR analysis** using individual ex.sas7bdat dosing records: events per infusion at 3 mg/kg vs. 6 mg/kg vs. 10 mg/kg.

8. **ADA titer-safety correlation:** Spearman rank correlation of peak ADA titer vs. cumulative IRR count per participant.

9. **Individual safety narrative for 0017-9004 (B1):** This participant contributes 4/15 SAEs (27%) and the only drug-related SAE. In a cohort of N=2, one participant's events dominate the safety profile. A dedicated narrative is essential.

10. **Pre-specify a DSMB statistical monitoring plan** given the transition to OLE/LTE phases with ongoing dosing.

### Long-Term (Pipeline Architecture)

11. **Eliminate hardcoded safety data:** Replace SAE_DATA, TRTDUR, IRR_EVENTS, and event count constants with programmatic reads from CSV/SAS source files. This would make the pipeline truly data-driven and eliminate the risk of stale hardcoded values.

12. **Add data validation layer:** Check that CSV subject lists match TREATED, verify SAE counts match data, and flag discrepancies.

13. **Implement automated delta detection:** Rather than manually listing changes, programmatically diff the current and previous data cuts and generate the Data Changes Tracker section automatically.

---

## Appendix A: Confidence Interval Methodology

All confidence intervals use the Clopper-Pearson exact method for binomial proportions. For k successes in n trials:
- Lower bound: Beta(alpha/2; k, n-k+1) for k > 0, else 0
- Upper bound: Beta(1-alpha/2; k+1, n-k) for k < n, else 1

For the special case of k=n (e.g., 20/20 IRR), the one-sided 97.5% lower bound is reported: 1 - (alpha)^(1/n) = 1 - 0.05^(1/20) = 0.861 for alpha=0.05, giving (86.1%, 100%). Using the standard two-sided CI: lower = 0.832, upper = 1.000.

Minimum detectable AE rates assume the "rule of detection" framework: P(X >= 1 | N, p) >= 0.80, solved as p >= 1 - 0.20^(1/N).

## Appendix B: Code Reference

Key functions reviewed in `generate_mmr.py`:

| Function | Lines | Purpose | Data Source |
|----------|-------|---------|-------------|
| `load_lab_data()` | 202-212 | Load MLM safety lab CSV | mlm_dnli-i-0001_safety.csv |
| `make_edish_plot()` | 331-379 | eDISH scatter plot | Computed from lab data |
| `make_ecg_trend_plot()` | 382-459 | ECG trends (SYNTHETIC) | Generated from ECG_PARAMS constants |
| `make_vs_trend_plot()` | 462-539 | Vital signs trends (SYNTHETIC) | Generated from VS_PARAMS constants |
| `make_lab_trend_plot()` | 254-328 | Lab trends (REAL DATA) | MLM lab CSV |
| `make_sae_timeline_plot()` | 542-636 | SAE Gantt chart | Hardcoded SAE_DATA |
| `make_exposure_swimlane_plot()` | 727-864 | Exposure swimlane | Hardcoded TRTDUR, IRR_EVENTS |
| `generate_report()` | 1136-1656 | Main HTML assembly | All sources |
