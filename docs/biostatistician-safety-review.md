# DNLI-I-0001 Medical Monitoring Report -- Statistical Safety Signal Detection Review

**Study:** DNLI-I-0001 | **Drug:** DNL-126 (ETV:SGSH-BioM) | **Indication:** MPS IIIA (Sanfilippo Syndrome Type A)
**Data Cut:** 2026-02-25 | **N=20** across 4 cohorts | **Reviewer Role:** Safety Biostatistician

---

## Executive Summary

DNL-126 demonstrates an acceptable hepatic safety profile (0/20 participants meeting Hy's Law or approaching ALT/AST >3xULN thresholds) and no AE-related treatment discontinuations across a cumulative exposure of approximately 1,280 person-weeks. However, the universal incidence of infusion-related reactions (442 events across 20 participants; 100% affected) constitutes the dominant safety signal, with rash (108 events) and vomiting (84 events) as the highest-burden IRR subtypes. The single drug-related SAE (Grade 3 IRR in participant 0017-9004, Cohort B1) and the occurrence of one anaphylactic reaction event reinforce that IRR management remains the principal clinical risk. With N=20 and a smallest cohort of N=2, formal between-cohort statistical comparisons are not powered; only descriptive assessments and signal-level observations are appropriate.

---

## 1. Data Completeness Assessment

### 1.1 Study Disposition
- 20/20 enrolled participants received treatment (100% treatment initiation).
- 19/20 remain active on study drug; 1 participant is active off study drug.
- 16 consented for OLE; 4 for LTE. No early terminations. Zero discontinuations due to AEs.
- 3 screen failures occurred (exclusion criteria: 1 investigator judgment, 1 liver enzyme elevation [ALT/AST >3xULN or TBILI >1.5xULN], 1 compliance concern).

### 1.2 Safety Assessment Data Availability
The report does not provide granular visit-level completion rates for lab, ECG, or vital signs. However, several indirect indicators are available:

- **Protocol deviations for missed/late assessments** were reported for multiple participants across Cohorts A1-A3 during Dec 2025-Jan 2026, classified as "important, non-critical." This indicates some assessment windows were missed but the deviations were not considered data-integrity-threatening.
- **Lab data source:** MLM Medical Labs CSV transfer dated 2026-02-13 (12 days before data cut), meaning lab results from approximately the last 12 days may be absent.
- **ECG data source:** eg1.sas7bdat and frecgn.sas7bdat -- summary statistics are presented for all 4 cohorts, suggesting reasonable completeness.
- **Vital signs data source:** vs.sas7bdat (93 MB) -- summary data available across all cohorts.

### 1.3 Differential Missingness by Cohort
- Cohort A3 includes participant 0017-9007 who had an MRSA-related dose interruption (Jul-Sep 2025) and participant 0017-9008 (both in Core Study phase), potentially reducing their data density relative to other A3 participants.
- Cohort B1 (N=2) has the lowest compliance (>=91%), suggesting more dose interruptions and potentially more missed safety assessments.
- **Assessment:** Quantitative visit-level completeness percentages are NOT available in this report. This is a **data gap** -- I recommend requesting visit completion matrices from the EDC to confirm whether differential missingness introduces surveillance bias.

---

## 2. IRR Event Rate Analysis

### 2.1 Overall IRR Burden
- **Total IRR events:** 442 across 20 participants
- **Mean IRR events per participant:** 442 / 20 = **22.1 events/participant**
- 100% of participants experienced at least one IRR. 75% experienced moderate-to-severe IRR.

### 2.2 IRR Events by Cohort (Crude and Exposure-Adjusted)

| Cohort | N | Events | Duration (median wks) | Crude Rate (events/participant) | Exposure-Adjusted Rate (events/100 person-wks) |
|--------|---|--------|-----------------------|-------------------------------|-----------------------------------------------|
| A1 | 4 | 118 | 107 | 29.5 | 27.6 |
| A2 | 4 | 91 | 91 | 22.8 | 25.0 |
| A3 | 10 | 172 | 26 | 17.2 | 66.2 |
| B1 | 2 | 61 | 56 | 30.5 | 54.5 |
| **All** | **20** | **442** | **52** | **22.1** | **~38.0** |

*Note: Person-weeks estimated as N x median duration per cohort.*

### 2.3 Critical Observation: Exposure-Adjusted IRR Rates by Cohort
The exposure-adjusted IRR rate for **Cohort A3 (66.2 per 100 person-weeks) and B1 (54.5) far exceed those for A1 (27.6) and A2 (25.0)**. Two interpretations:

1. **Time-dependent decline:** A1 and A2 have been on study for 91-107 weeks. If IRR events are front-loaded (concentrated in the first 6-12 months of treatment), the longer denominator dilutes the rate. This would be consistent with immunological tolerance development.
2. **Cohort-specific factors:** A3 and B1 are still in the early-to-mid phase of exposure where IRR burden is expected to be highest.

**Conclusion:** The data pattern is consistent with a declining IRR event rate over treatment duration, which is a favorable signal suggesting immune tolerance or effective premedication adaptation. However, without patient-level time-to-event IRR data, I cannot formally confirm this with a Poisson regression or negative binomial model.

### 2.4 IRR Rate by Dose Level
- All A1, A2, and B1 participants (10 total) have reached 10 mg/kg. 7/10 A3 participants are at 10 mg/kg; 3 remain at lower dose levels.
- Since dose escalation occurs sequentially (3 -> 6 -> 10 mg/kg), IRR events during dose escalation periods cannot be separated from the time-on-study effect without individual dosing records.
- **Recommendation:** A formal dose-stratified exposure-adjusted IRR analysis using individual ex.sas7bdat records is needed to disentangle dose-level from time-on-study effects.

---

## 3. AE Incidence Rate Patterns

### 3.1 TEAE Summary
- 100% of participants experienced at least one TEAE (all cohorts).
- 100% experienced at least one drug-related TEAE (all cohorts).
- Grade >=3 TEAEs: 85% overall (17/20). By cohort: A1 100%, A2 75%, A3 80%, B1 100%.
- SAEs: 65% overall (13/20). By cohort: A1 100%, A2 25%, A3 60%, B1 100%.
- Drug-related SAE: 5% (1/20) -- single Grade 3 IRR in 0017-9004 (B1).
- AE leading to discontinuation: 0%.

### 3.2 Exposure-Adjusted SAE Incidence

| Cohort | N | SAE participants | Estimated person-wks | SAE incidence per 100 person-wks |
|--------|---|-----------------|---------------------|--------------------------------|
| A1 | 4 | 4 (100%) | 428 | ~0.93 |
| A2 | 4 | 1 (25%) | 364 | ~0.27 |
| A3 | 10 | 6 (60%) | 260 | ~2.31 |
| B1 | 2 | 2 (100%) | 112 | ~1.79 |

Cohort A1's 100% SAE rate reflects long cumulative exposure (107 weeks). The high crude SAE incidence in A3 (60% in only ~26 weeks) deserves attention -- however, examining the SAE listing reveals that several A3 SAEs occurred pre-dose (post-LP headache Day -11, port site infiltration Day -20, delirium Day -20), which inflates the treatment-emergent count.

### 3.3 SAE Temporal Clustering
Reviewing individual SAE onset days:

| Participant | Cohort | SAE | Onset (Study Day) |
|-------------|--------|-----|-------------------|
| 0016-9001 | A1 | SVT | Day 16 |
| 0016-9003 | A1 | Cognitive disorder | Day 423 |
| 0016-9006 | A3 | Post-LP headache | Day -11 |
| 0016-9006 | A3 | Mobility decreased | Day 93 |
| 0016-9006 | A3 | Dysphagia | Day 119 |
| 0017-9001 | A1 | Staph bacteremia | Day 638 |
| 0017-9002 | A1 | Inconsolable crying | Day 338 |
| 0017-9004 | B1 | Seizure-like activity | Day 42 |
| 0017-9004 | B1 | Pneumonia | Day 48 |
| 0017-9004 | B1 | Grade 3 IRR (RELATED) | Day 283 |
| 0017-9004 | B1 | Hypoxia | Day 388 |
| 0017-9007 | A3 | MRSA bacteremia | Day 2 |
| 0017-9007 | A3 | Dyskinesia | Day 163 |
| 2064-9003 | A3 | Port site infiltration | Day -20 |
| 2064-9005 | A3 | Delirium | Day -20 |

**Notable patterns:**
- Participant 0017-9004 (B1) accounts for 4 SAEs, the highest individual burden, including the only drug-related SAE. This participant warrants individual safety narrative review.
- Participant 0016-9006 (A3) has 3 SAEs (mobility decreased, dysphagia -- both unresolved), which may reflect disease progression in a 198-month (16.5-year) participant, the oldest in the study.
- No tight temporal clustering around specific treatment weeks across participants. SAE distribution appears dispersed over the treatment timeline.
- Early SAE events (Day 2, Day 16, Day 42, Day 48) may represent background disease burden rather than treatment effects -- the very early onset and "Not Related" causality assessments support this.

---

## 4. Lab Value Trends

### 4.1 Hepatic Safety Parameters
- **ALT/SGPT >3xULN:** 0/20 participants (0%)
- **AST/SGOT >3xULN:** 0/20 participants (0%)
- **Total Bilirubin >1.5xULN:** 0/20 participants (0%)
- **Creatinine >1.5xULN:** 0/20 participants (0%)
- **CK >5xULN:** Transient elevation noted in Cohort A3; assessed as not clinically significant, resolved.

### 4.2 eDISH Validation
- **Hy's Law quadrant (ALT >3xULN AND TBili >2xULN):** Confirmed 0/20 participants.
- All liver function parameters reported as "within acceptable limits across all cohorts."

### 4.3 Safety Margin -- Data Gap
The report states 0/20 participants exceeded the thresholds but does **not provide maximum observed xULN values** for ALT, AST, or TBILI. This is a **significant data gap** for eDISH validation. To properly quantify the safety margin, I need:
- Maximum observed ALT as a fraction of ULN (e.g., max ALT = 1.8xULN would give a safety margin of 40% below the 3xULN threshold)
- Maximum observed TBILI as fraction of ULN

**Recommendation:** Request the actual max ALT/AST/TBILI xULN values from the lab.sas7bdat dataset to compute: Safety Margin = 1 - (max observed / threshold). Without these values, the eDISH assessment is binary (pass/fail) rather than quantitative.

### 4.4 Haematology
- No Grade >=2 anaemia, no thrombocytopenia.
- Transient eosinophil elevations in A3/B1 peri-IRR (consistent with allergic/hypersensitivity component of IRR).
- Mild lymphocyte reductions in A1 -- monitored, no clinical significance assigned.

### 4.5 Assessment
The hepatic safety profile is clean. The eosinophil elevation in A3/B1 is pharmacologically expected given the IRR burden. The lymphocyte reduction in A1 warrants longitudinal trending -- with 107 weeks of exposure, any immune suppression signal would be important to monitor.

---

## 5. ADA-Safety Statistical Correlation

### 5.1 ADA Prevalence
- **ADA positive (any post-baseline):** 19/20 (95%)
- **Neutralizing ADA (NAb):** 12/20 (60%)
- **ADA negative throughout:** 1/20 (5%) -- single participant in A3
- **Baseline ADA positive:** 5/20 (25%)

### 5.2 ADA by Cohort

| Metric | A1 (N=4) | A2 (N=4) | A3 (N=10) | B1 (N=2) |
|--------|----------|----------|-----------|----------|
| ADA+ | 4 (100%) | 4 (100%) | 9 (90%) | 2 (100%) |
| NAb+ | 3 (75%) | 2 (50%) | 5 (50%) | 2 (100%) |

### 5.3 ADA-IRR Correlation
- With 19/20 ADA-positive and 20/20 IRR-affected, there is essentially no variability in the ADA-positive group to correlate with IRR. The single ADA-negative participant still experienced IRR.
- Meaningful ADA-IRR correlation analysis requires **titer magnitude** vs. **IRR event count** at the individual level. The report notes key high-titer participants: 0016-9004 (neutralizing, persistent), 2065-9002 (very high titer, Week 73), 0016-9003 (persistent, Wk 97 titer: 3,542,940).
- ADA positivity is associated with DEC-mandated dose adjustments in at least 7 participants (35%).
- **Quantitative assessment not possible** from aggregate data. A Spearman rank correlation of (peak ADA titer) vs. (IRR event count) or (peak ADA titer) vs. (time-to-first-moderate-severe-IRR) using individual bioagilytix data would be informative.

### 5.4 NAb+ vs. NAb- Safety Profile
- NAb+ (12/20, 60%): Includes all B1 participants (100% SAE rate, highest per-participant IRR burden of 30.5 events).
- NAb- (8/20, 40%): Descriptive comparison is confounded by cohort, exposure duration, and small sample size.
- **Statistical test appropriateness:** Fisher's exact test for SAE rate (NAb+ vs. NAb-) would have extremely low power with N=12 vs. N=8. Not recommended for formal hypothesis testing; descriptive tabulation is appropriate.

---

## 6. Dose Compliance Statistics

### 6.1 Compliance Distribution

| Cohort | N | Compliance | Dose Interruptions | DEC Dose Adjustments |
|--------|---|------------|-------------------|---------------------|
| A1 | 4 | >=96% | 3/4 (75%) | 2/4 (50%) |
| A2 | 4 | >=95% | 2/4 (50%) | 2/4 (50%) |
| A3 | 10 | >=94% | 5/10 (50%) | 3/10 (30%) |
| B1 | 2 | >=91% | 2/2 (100%) | 0/2 (0%) |
| **All** | **20** | -- | **12/20 (60%)** | **7/20 (35%)** |

### 6.2 Compliance-Exposure Relationship
- Compliance appears inversely related to exposure duration, with A1 (longest, >=96%) paradoxically having the highest compliance and B1 (>=91%) the lowest. This suggests:
  - A1/A2 participants have stabilized on treatment with effective IRR management.
  - B1's 100% dose interruption rate and lower compliance (91%) is driven by the complex SAE profile of participant 0017-9004 (4 SAEs including the only drug-related SAE).

### 6.3 Dose Interruption Clustering
- The report notes MRSA-related dose interruption for 0017-9007 (A3, Jul-Sep 2025) and IRR-related dose interruption for 0017-9004 (B1, post-Wk 25).
- Without individual dosing timelines, I cannot determine whether interruptions cluster at dose escalation points (3->6 mg/kg or 6->10 mg/kg transitions).
- **Recommendation:** Analyze dose interruption timing relative to escalation milestones using ex.sas7bdat data.

---

## 7. Small Sample Statistical Considerations

### 7.1 Power and Minimum Detectable Event Rates
For a single-arm study with N=20:
- **Minimum detectable AE rate with 80% power** (using exact binomial, alpha=0.05, one-sided test against H0: p=0): If the true AE rate is p, we need P(X >= 1 | N=20, p) >= 0.80. Solving: 1 - (1-p)^20 >= 0.80, giving p >= 1 - 0.20^(1/20) = **0.078 (7.8%)**. Events occurring at rates below ~8% have a meaningful probability (>20%) of being entirely missed.
- For Cohort B1 (N=2): Minimum detectable rate = 1 - 0.20^(1/2) = **55.3%**. This means B1 can only reliably detect very common events.
- For Cohort A1/A2 (N=4): Minimum detectable rate = 1 - 0.20^(1/4) = **33.1%**.

### 7.2 Confidence Intervals for Key Rates
- **Drug-related SAE rate:** 1/20 = 5%; 95% exact Clopper-Pearson CI: (0.13%, 24.9%). The true rate could plausibly be as high as 25%.
- **Grade >=3 TEAE rate:** 17/20 = 85%; 95% CI: (62.1%, 96.8%).
- **IRR rate:** 20/20 = 100%; 95% one-sided CI lower bound: (83.2%, 100%).

### 7.3 Between-Cohort Comparisons
- **Not statistically meaningful** for formal hypothesis testing. Example: SAE rate A2 (1/4 = 25%) vs. B1 (2/2 = 100%) -- Fisher's exact p-value would be 0.333, far from significant, despite a large observed difference.
- Cohort comparisons should be treated as **descriptive signal generation** only.
- The observed difference in exposure-adjusted IRR rates (A1: 27.6 vs. A3: 66.2 per 100 person-weeks) is likely a real time-on-study effect but cannot be formally tested with this design.

---

## 8. eDISH Statistical Validation

### 8.1 Threshold Assessment

| Parameter | Threshold | n Exceeding / N | Status |
|-----------|-----------|-----------------|--------|
| ALT/SGPT | >3xULN | 0/20 | CLEAR |
| AST/SGOT | >3xULN | 0/20 | CLEAR |
| Total Bilirubin | >1.5xULN | 0/20 | CLEAR |
| Total Bilirubin (Hy's Law criterion) | >2xULN | 0/20 | CLEAR |
| Creatinine | >1.5xULN | 0/20 | CLEAR |

### 8.2 Hy's Law Quadrant
**Confirmed: Zero datapoints in Hy's Law quadrant** (requires BOTH ALT >3xULN AND TBili >2xULN simultaneously). This is validated.

### 8.3 Safety Margin -- Data Gap
As noted in Section 4.3, the report provides only binary (above/below threshold) data. The actual maximum observed ALT, AST, and TBILI values as multiples of ULN are not reported. Without these:
- I cannot compute the distance from the nearest datapoint to the eDISH quadrant boundaries.
- I cannot assess whether any participant is trending toward thresholds.
- A participant at 2.9xULN for ALT would be "clear" but would represent a very different risk profile than one at 0.5xULN.

---

## Data Quality Assessment

### Strengths
1. Complete treatment initiation (20/20) and retention (0 discontinuations) -- eliminates informative censoring bias.
2. Consistent safety monitoring framework across all 4 sites.
3. 100% ADA monitoring coverage with Bioagilytix data through Week 97 for earliest cohorts.
4. SAE causality assessments documented for all events.

### Limitations
1. **No visit-level assessment completion rates** -- cannot quantify surveillance intensity differences by cohort.
2. **No individual patient lab values** -- only threshold-based (binary) lab assessments are reported; cannot assess trends or magnitudes.
3. **Lab data lag:** MLM safety lab transfer is 2026-02-13, 12 days before the 2026-02-25 data cut. Labs drawn in the last ~2 weeks of the reporting period are absent.
4. **Compliance values are floor estimates** (reported as ">=X%") rather than exact values.
5. **IRR event-level timing data** is not available in aggregate form -- individual patient profiles are needed to assess temporal decline patterns.
6. **Post-publication updates** (0017-9007 MRSA deviation, dyskinesia SAE, additional ADA Wk 97 data) indicate the data package was modified after the published MMR, creating version control considerations.

---

## Statistical Limitations and Caveats

1. **N=20 across 4 cohorts precludes formal between-cohort hypothesis testing.** All comparisons are descriptive. The minimum detectable AE rate is ~8% (overall) and ~33% (per cohort N=4).
2. **Confounding of time-on-study with cohort:** A1/A2 have 91-107 weeks of exposure vs. A3's 26 weeks. Higher cumulative AE/SAE rates in A1 are expected from longer follow-up alone.
3. **Single-arm design:** No concurrent control group; all safety assessments are against background disease rate expectations and published natural history data for MPS IIIA.
4. **Informative dose modification:** DEC-mandated dose adjustments in 35% of participants introduce a survivorship bias -- participants who tolerate treatment well continue at higher doses, while those with more severe IRR/ADA may have prolonged dose holds.
5. **Participant 0017-9004 (B1)** contributes 4/15 total SAEs (27%) and is the only drug-related SAE -- a single-participant disproportionate influence on the overall safety profile. In N=2 cohort, this represents half the safety data.

---

## Recommendations for Enhanced Monitoring or Analysis

1. **Request individual-level lab data** (ALT, AST, TBILI xULN values over time) to generate quantitative eDISH plots with actual datapoints and safety margin calculations.

2. **Perform exposure-adjusted IRR analysis stratified by treatment epoch** (Weeks 1-12, 13-26, 27-52, 52+) using individual dosing records to confirm the hypothesized declining IRR rate pattern.

3. **Conduct dose-level IRR analysis** (events during 3 mg/kg, 6 mg/kg, and 10 mg/kg treatment periods separately) to assess dose-response relationship.

4. **Request visit completion matrix** from EDC to quantify differential missingness by cohort and assessment type (lab, ECG, VS).

5. **ADA titer-IRR correlation analysis:** Using bioagilytix individual-level ADA titer data and IRR event timing, compute Spearman correlation between peak/time-matched ADA titer and IRR frequency.

6. **Participant 0017-9004 (B1) individual safety narrative:** This participant's trajectory (seizure-like activity Day 42, pneumonia Day 48, drug-related Grade 3 IRR Day 283, hypoxia Day 388) warrants a dedicated narrative analysis including DEC deliberation outcomes.

7. **Longitudinal lymphocyte monitoring** in Cohort A1, given the observation of mild reductions and the longest exposure duration (~2 years).

8. **Eosinophil trending** in A3/B1 to determine whether elevations are strictly peri-IRR transient or represent a persistent shift.

9. **Dose interruption timing analysis** relative to escalation milestones (3->6 and 6->10 mg/kg transitions) to inform dose escalation safety guidelines.

10. **Pre-specify a Data Safety Monitoring Board (DSMB) statistical analysis plan** for ongoing monitoring, given that the study is transitioning participants into OLE/LTE phases with continued dosing.
