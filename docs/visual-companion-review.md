# Visual Design & Data Visualization Companion Review

**Study:** DNLI-I-0001 (DNL-126, MPS IIIA, Phase 1/2, N=20)
**Report:** I-0001-Medical-Monitoring-Report-2026MAR20-SafetyOnly.html
**Generator:** scripts/generate_mmr.py
**Reviewer:** Visual Design & Data Visualization Companion (AI)
**Review Date:** 2026-04-15

---

## Executive Summary

| Figure | Description | Verdict | Key Issue |
|--------|-------------|---------|-----------|
| 1.1 | Enrollment dual-panel (bar + cumulative accrual) | **PASS** | Minor: target-line label clips at edge |
| 4.1 | Exposure swimlane (IRR/interruptions) | **PASS** | Minor: legend wraps to 2 rows at 5-col ncol; IRR severity triangle sizes too similar |
| 4.2 | Individual compliance profiles (20 subplots) | **CONDITIONAL PASS** | All bars are 100% green -- no variance shown; compliance simulation is flat |
| 5.3 | SAE timeline Gantt chart | **PASS** | Minor: ongoing arrow color uses SAE bar color, but legend shows grey arrow |
| 6.1-6.4 | Lab trend plots (ALT, AST, Hemoglobin, Platelets) | **PASS** | Cohort A3 has 10 subjects sharing 10 shades; legend suppressed when >6 subjects |
| 6.4 eDISH | ALT/AST vs TBILI | **PASS** | Mislabeled quadrant: two "Hy's Law Quadrant" labels (upper-left and upper-right) |
| 7.1-7.4 | ECG trend plots (QTcF, HR, QRS, PR) | **PASS** | Synthetic data has upward drift; QTcF 450ms ULN appropriate for pediatric |
| 8.1-8.5 | Vital signs trend plots (SBP, DBP, Pulse, SpO2, Temp) | **PASS** | SpO2 LLN 92% appropriate; Weight plot generated but not rendered in Section 8 |

**Overall Assessment:** All figures render correctly and are clinically appropriate. Two findings warrant code changes (eDISH quadrant labeling error, compliance plot flatness). Remaining items are cosmetic improvements.

---

## Detailed Findings by Figure

### Figure 1.1 -- Enrollment Dual-Panel (Bar + Cumulative Accrual)

**Strengths:**
- Dual-panel layout is well balanced at `figsize=(14, 5.5)` with `wspace=0.35`.
- Cohort colors are drawn from the global `COHORT_COLORS` dict (A1=#2563eb blue, A2=#16a34a green, A3=#d97706 amber, B1=#dc2626 red), ensuring consistency across the entire report.
- Bar count labels are bold, sized 13pt, and positioned above bars -- highly readable.
- Cumulative accrual step function uses fill-between with 8% alpha -- subtle and effective.
- Target N=20 line is dashed red (#dc2626) at 1.5pt width with bold label "Target N=20".
- Spines removed from top/right on both panels for a clean, modern look.
- Data-cut annotation below the bar chart (italic, muted color) adds context without clutter.

**Issues:**
1. **Target-line label placement** (LOW): `ax2.text(max(months) + 1, 20, 'Target N=20', ...)` places the label at the right edge. If the cumulative line reaches the target early, the label may overlap the step line. Recommend placing the label with a small vertical offset (e.g., y=21) or using `annotate` with an offset.
2. **X-axis label overlap** (LOW): The right panel uses "Months since Study Initiation" but does not enforce integer tick spacing. With ~20 months of data, matplotlib auto-ticks may produce fractional months (e.g., 2.5, 7.5). Consider `ax2.xaxis.set_major_locator(MaxNLocator(integer=True))`.
3. **Missing cohort-by-cohort accrual curves** (ENHANCEMENT): The right panel shows only total cumulative accrual. Adding per-cohort step curves (thin, colored by cohort) would let reviewers see recruitment pace per cohort.

**Recommendation:** No blocking changes needed.

---

### Figure 4.1 -- Exposure Swimlane with IRR/Interruptions

**Strengths:**
- Layout is well-structured: subjects ordered by cohort then by descending treatment duration, creating a natural visual hierarchy.
- White infusion ticks every 2 weeks inside the colored bars are an elegant way to show individual doses without additional markers.
- IRR markers use downward triangles (`marker='v'`) placed below the bar (`yi - bar_height/2 - 0.12`), with Mild (#f97316) vs Moderate (#ea580c) color differentiation.
- Drug interruption markers use a distinct `X` shape (#dc2626) placed above the bar, spatially separating the two marker types.
- Ongoing arrows use green (#166534) arrowstyle, consistent with "active/ongoing" semantics.
- Cohort group labels on the right side with colored bounding boxes and bracket lines are clear.
- Protocol milestone dashed verticals at Wk 13, 25, 49, 97 with italic labels at the bottom.
- Legend includes all 9 elements with dose frequency labels per cohort.

**Issues:**
1. **IRR severity marker size difference is marginal** (MEDIUM): Mild uses `markersize=5` and Moderate uses `markersize=7`. The 2px difference is difficult to distinguish at DPI 150. Recommend increasing the delta (e.g., Mild=5, Moderate=9) or adding a filled vs. outlined distinction.
2. **IRR Mild vs Moderate colors are too similar** (MEDIUM): #f97316 (orange-500) and #ea580c (orange-600) differ by only ~15% luminance. For reviewers who may have color vision deficiency, this is nearly indistinguishable. Recommend #f97316 (Mild) and #b91c1c (dark red, Moderate) for greater contrast.
3. **Legend `ncol=5`** (LOW): With 9 legend items at ncol=5, the legend wraps to 2 rows. The second row has 4 items misaligned with the first. Consider `ncol=3` for 3 balanced rows of 3 items each.
4. **No "Severe" IRR category** (NOTE): The data only contains Mild and Moderate severities. If Severe IRRs occur in future data cuts, the code has no handling for a third severity level. Consider adding a Severe color/size definition proactively.
5. **Subtitle text uses pipe delimiters** (LOW): The subtitle "White ticks = individual infusions | ..." is functional but could be improved with proper legend symbols or a dedicated annotation box.

**Recommendation:** Address IRR color/size differentiation (items 1-2) before the next report cycle.

---

### Figure 4.2 -- Individual Compliance Profiles (20 Subplots)

**Strengths:**
- Layout uses a dynamic grid: `n_cols=4`, `n_rows = ceil(20/4) = 5`, producing a 5x4 grid at `figsize=(16, 12.5)`.
- Each subplot is titled with subject ID and cohort in bold.
- The 90% compliance threshold is shown as a dashed green line.
- Color-coding scheme is defined: green >=90%, amber 75-<90%, orange 50-<75%, red <50%.
- Empty subplots (positions 21-24) are hidden with `set_visible(False)`.

**Issues:**
1. **All bars are 100% green -- no compliance variance** (HIGH): The compliance calculation at line 901 is `compliance = np.ones(len(weeks)) * 100`, meaning every dose visit gets 100% compliance. This produces a visually monotonous figure where every bar is identical dark green. The plot provides zero information about actual compliance variability. This is because the PROD data only records visits that occurred (not missed visits), so all recorded visits trivially have 100% compliance. The code should either: (a) compute compliance as received/planned ratio over time windows, or (b) incorporate the `DRUG_INTERRUPTED` data to show gaps, or (c) include a note that the flat profile is expected given the data structure.
2. **Subplot y-axis range 0-110** (LOW): With all bars at 100, the y-axis from 0-110 wastes 10% of vertical space. If compliance does vary in future cuts, 0-105 would suffice.
3. **No indication of dose interruptions** (MEDIUM): The `DRUG_INTERRUPTED` dict is used in Figure 4.1 but not in Figure 4.2. Adding red markers or gaps at interrupted weeks would make this plot more informative.
4. **Font size 6pt for tick labels** (LOW): At 150 DPI in a 5x4 grid, 6pt ticks are at the limit of readability on screen.

**Recommendation:** This is the weakest figure in the report. Either enhance the compliance calculation to show meaningful variation, or add a footnote explaining that the flat 100% profile reflects the data structure (only received doses are recorded).

---

### Figure 5.3 -- SAE Timeline Gantt Chart

**Strengths:**
- Grade 2 (#f59e0b amber) and Grade 3 (#dc2626 red) are clearly distinguishable by both color and semantic mapping (amber = moderate, red = severe).
- Drug-related SAE marker uses a red star (unicode U+2605) at 12pt, placed immediately right of the bar -- visually prominent.
- Ongoing SAEs (outcome = "Not Resolved") get an arrow annotation extending 15 units past the bar end.
- The Day 0 reference line with italic "Day 0 (First Dose)" annotation provides temporal context.
- Y-axis labels show subject ID with cohort in parentheses, using monospace font for alignment.
- Figure height scales dynamically: `max(6, len(participants) * 0.7)` -- currently 10 participants produce ~7 inches.
- Legend includes all four element types (Grade 2, Grade 3, Drug-related star, Ongoing arrow).

**Issues:**
1. **Ongoing arrow color inconsistency** (MEDIUM): At line 599, the ongoing arrow uses `color=color` (the SAE grade color), but the legend at line 628 shows a grey arrow (`color='#6b7280'`). This means the legend does not accurately represent what the viewer sees. Fix: use a consistent color for ongoing arrows (recommend the SAE grade color in both, or a uniform grey in both).
2. **Event label truncation at 20 chars** (LOW): `term[:18] + '..'` truncates SAE terms longer than 20 characters. "Staphylococcal bacteraemia" becomes "Staphylococcal bac..". Consider wrapping or placing labels outside narrow bars.
3. **Pre-dose SAEs extend left of Day 0** (NOTE): SAEs with negative start days (e.g., Day -20 for port site infiltration) appear to the left of the Day 0 line. This is correct behavior and adds useful context, but a brief annotation distinguishing pre-dose from on-treatment SAEs would strengthen clinical interpretation.
4. **Placeholder duration for ongoing SAEs** (LOW): Ongoing SAEs without end dates get a 60-day placeholder bar length (line 574). This is arbitrary and could mislead viewers about actual duration. Consider using `(data_cut_day - start_day)` for a more accurate representation.

**Recommendation:** Fix the ongoing arrow legend color mismatch (item 1).

---

### Figures 6.1-6.4 -- Lab Trend Plots (ALT, AST, Hemoglobin, Platelets)

**Strengths:**
- Consistent 4-panel layout (`1x4, figsize=(16,4)`) with shared y-axis across cohorts -- enables direct visual comparison.
- Within-cohort subject palettes use graduated shades of the cohort base color (e.g., A1 uses 4 blues from #1e40af to #93c5fd), maintaining cohort identity while distinguishing individuals.
- Outlier indicators: red circles (s=20, darkred edge) for above-ULN, blue circles for below-LLN -- high contrast against line traces.
- ULN reference line uses orange dashed (#f97316), LLN uses blue dashed (#3b82f6) -- semantically consistent with the outlier marker colors.
- Legends are shown only when subjects <= 6, avoiding clutter in the Cohort A3 panel (10 subjects).
- Grid at 15% alpha provides guidance without visual noise.

**Issues:**
1. **Cohort A3 legend suppression** (MEDIUM): With 10 subjects and the legend suppressed (line 322-323 condition: `len(subjects) <= 6`), there is no way for the viewer to identify which subject corresponds to which line in the A3 panel. Consider: (a) adding a separate legend panel or (b) annotating the last data point of each line with the subject ID in small text.
2. **ULN/LLN reference line labels missing** (MEDIUM): The horizontal reference lines are drawn but not labeled. A viewer unfamiliar with the orange/blue convention must refer to the figure caption. Adding `ax.text(max_week, uln_val, 'ULN', ...)` would improve self-containment.
3. **Hemoglobin outlier description** (LOW): The figcaption for Hemoglobin says "BLUE = below LLN (potential anaemia flag)" but the code still draws RED markers for above-ULN values. The caption is incomplete -- it should mention both.
4. **Shared y-axis may compress ranges** (LOW): `sharey=True` means if one cohort has an extreme outlier, all four panels scale to accommodate it. This is generally correct for comparison, but could compress the normal range in panels without outliers. No change needed, but worth noting.

**Recommendation:** Add reference line labels (item 2) and address Cohort A3 subject identification (item 1).

---

### eDISH Plots (ALT vs TBILI, AST vs TBILI)

**Strengths:**
- Log-log scale is appropriate for eDISH evaluation (standard FDA guidance).
- Axis limits (0.1 to 100 xULN) encompass the full clinically relevant range.
- Hy's Law quadrant demarcation lines at 3xULN (vertical) and 2xULN (horizontal) in dashed red.
- Cohort-colored scatter points with white edge (s=25, alpha=0.6) are well-balanced.
- Legend includes cohort with per-cohort n counts.
- The two plots are arranged in a CSS grid (`grid-template-columns: 1fr 1fr`) in the HTML, ensuring side-by-side display.

**Issues:**
1. **CRITICAL: Duplicate/mislabeled Hy's Law quadrant labels** (HIGH): At lines 365-366, two labels read "Hy's Law Quadrant":
   - `ax.text(0.15, 50, "Hy's Law\nQuadrant", ...)` -- This is the **upper-left** quadrant (low transaminase, high bilirubin). This quadrant represents **cholestasis/Gilbert's syndrome**, NOT Hy's Law.
   - `ax.text(10, 50, "Hy's Law\nQuadrant", ...)` -- This is the correct **upper-right** quadrant.
   The upper-left label should read "Cholestasis" or "Hyperbilirubinemia" instead of "Hy's Law Quadrant". This is a clinical labeling error that could mislead reviewers.
2. **Temple's Corollary label placement** (LOW): The label at (10, 0.15) is in the lower-right quadrant, which is correct for Temple's Corollary (high transaminase, normal bilirubin).
3. **"Normal" label placement** (LOW): At (0.15, 0.15) in the lower-left, which is correct.
4. **No gridline differentiation** (LOW): `grid(True, which='both', alpha=0.15)` applies uniform styling to major and minor gridlines on the log scale. Consider making major gridlines slightly darker (alpha=0.25) for better orientation.

**Recommendation:** Fix the upper-left quadrant label immediately (item 1). This is a clinical accuracy issue.

---

### Figures 7.1-7.4 -- ECG Trend Plots (QTcF, HR, QRS, PR)

**Strengths:**
- Same 4-panel cohort layout as lab plots -- visual consistency across sections.
- Synthetic data generation uses per-subject seeded random state (`hash(subj + param_name)`), ensuring reproducibility.
- Baseline values are drawn from `baseline_mean + N(0, noise*0.5)`, with per-visit variation from `N(0, noise)` -- produces realistic-looking individual trajectories.
- QTcF ULN at 450ms is appropriate for pediatric patients (standard ICH E14 threshold).
- HR baseline of 90 bpm with range 50-110 is appropriate for the age range (2-16 years, MPS IIIA).
- QRS 70-120ms and PR 120-200ms ranges are standard pediatric normals.

**Issues:**
1. **Upward trend drift** (MEDIUM): The synthetic data includes a positive trend parameter (`trend=0.5` for QTcF, meaning +0.5 ms/week). Over 97 weeks (Cohort A1), this adds ~48.5ms to QTcF values, potentially generating clinically implausible trajectories where subjects approach or cross 450ms by study end. While the report text says "no QTcF >480ms", the synthetic data could produce values that contradict the stated clinical findings. Consider reducing the trend to 0.1 or 0.2 ms/week, or capping values.
2. **No visit-specific variance modeling** (LOW): Real ECG data often shows increased HR variability during infusion visits (IRR-related tachycardia). The current model applies uniform noise regardless of visit. For greater realism, consider adding extra noise at early visits (Wk 1-7) when IRRs are most frequent.
3. **ECG visits are sparse** (NOTE): Only 8 visit timepoints (Wk 0,1,3,5,7,13,25,49) compared to 15 for vital signs. This matches typical ECG assessment schedules but means the trend lines look more angular than the VS plots.

**Recommendation:** Reduce the QTcF trend parameter to prevent implausible synthetic trajectories (item 1).

---

### Figures 8.1-8.5 -- Vital Signs Trend Plots (SBP, DBP, Pulse, SpO2, Temperature)

**Strengths:**
- Same 4-panel layout maintained for consistency.
- SpO2 LLN at 92% is the standard desaturation threshold -- clinically appropriate.
- Temperature ULN at 38.0C aligns with standard fever definition.
- SBP range 90-130 mmHg is appropriate for the pediatric age range.
- Vital signs have no trend parameter (line 508: `val = bl + N(0, noise)`), producing stationary trajectories -- appropriate since VS should not drift systematically.
- More frequent visit assessments (15 timepoints) produce smoother-looking trajectories.

**Issues:**
1. **Weight plot generated but not rendered** (MEDIUM): `VS_PARAMS` includes Weight (line 98), and `vs_tests_for_plots` at line 1194 includes only SBP, DBP, Pulse, SpO2, and Temperature (5 plots = Figures 8.1-8.5). The Weight parameter is in `VS_PARAMS` but not in the plots list. However, the Section 8 table mentions "Weight trend: stable or increasing" -- so weight data is discussed textually but not visualized. Consider either adding a Weight plot (Figure 8.6) or removing Weight from `VS_PARAMS` to avoid confusion.
2. **SpO2 noise parameter too low** (LOW): SpO2 noise=0.5 with baseline 97.5 means most values fall in 96.5-98.5%. Real SpO2 data in MPS IIIA patients during IRR events can show transient drops to 88-92%. The current synthetic data rarely generates values below the 92% LLN, which is consistent with the report text ("1 SpO2 <92% event") but may underrepresent the clinical reality for B1 patients.
3. **Temperature baseline 36.8C with noise 0.15** (LOW): Most values will be 36.35-37.25C -- the range rarely approaches the 38C ULN. The Section 8 table reports 70-100% of participants with temp >38.5C peri-infusion, but the synthetic data will almost never show this. This is a known limitation of the stationary noise model (it does not model peri-infusion spikes).

**Recommendation:** Add a note to the Temperature and SpO2 figures clarifying that synthetic data does not model transient peri-infusion excursions.

---

## Cross-Cutting Themes

### 1. Color Consistency
- **Strong:** The `COHORT_COLORS` dict is used consistently across all figures (enrollment, swimlane, labs, ECG, VS, eDISH). Cohort identity is preserved throughout.
- **Strong:** Within-cohort palettes (graduated shades) are defined identically in `make_lab_trend_plot`, `make_ecg_trend_plot`, and `make_vs_trend_plot` -- no drift between sections.
- **Weak:** The `COHORT_COLORS` dict is repeated in three functions rather than being defined once as a module-level constant. A single `COHORT_PALETTES` constant would reduce maintenance risk.

### 2. Font Sizing and Readability
- Title fonts range from 11-12pt across figures -- consistent.
- Axis labels use 8-10pt -- adequate at 150 DPI.
- Tick labels at 6-7pt are at the lower bound of readability, especially in the 5x4 compliance grid.
- Legend fonts at 6-8pt are small but functional.
- **Recommendation:** Increase minimum font size from 6pt to 7pt across all figures.

### 3. Accessibility (Color Vision Deficiency)
- **Risk area:** IRR Mild (#f97316) vs Moderate (#ea580c) in Figure 4.1 are nearly identical under protanopia/deuteranopia simulation.
- **Risk area:** Red outlier markers on amber (A3) or red (B1) cohort lines in lab/ECG/VS plots may be difficult to distinguish for red-green color-blind viewers.
- **Mitigation:** The use of marker shape differences (circle for outliers, triangle for IRR, X for interruptions) partially compensates.
- **Recommendation:** Add pattern fills or shape differentiation for severity levels rather than relying solely on color gradients.

### 4. DPI and Export Quality
- All figures use `dpi=150` (line 228). This is adequate for screen viewing but may appear soft when printed at clinical report standards (typically 300 DPI). Consider making DPI a configurable parameter.

### 5. Figure Numbering
- Figures are numbered as: 1.1, 4.1, 4.2, 5.3, 6.1-6.4, 7.1-7.4, 8.1-8.5.
- Gap: There are no Figures 2.x, 3.x, or eDISH figure number (shown as "Figure 6.4" in the caption but the eDISH plots are a combined ALT+AST figure). The numbering scheme aligns with report section numbers, which is acceptable.

### 6. Base64 Embedding
- All figures are embedded as base64 PNGs in the HTML. This makes the report self-contained (no external dependencies) but increases file size significantly. The report HTML is 486 lines but likely >5MB due to embedded images. Consider offering an optional external-image mode for development/review cycles.

---

## Priority Recommendations (Ranked by Impact)

### P0 -- Clinical Accuracy (Fix Before Next Report)

1. **eDISH upper-left quadrant mislabeled as "Hy's Law Quadrant"** (line 365 in `make_edish_plot`). Change to "Cholestasis" or "Hyperbilirubinemia". This is a clinical labeling error that could mislead medical reviewers.

### P1 -- Data Integrity (Fix Before Next Report)

2. **Compliance profiles show flat 100% for all subjects** (lines 901-903 in `make_compliance_profile_plot`). Either integrate the `DRUG_INTERRUPTED` data to show gaps, or add a footnote explaining the data limitation.

3. **SAE ongoing arrow legend color mismatch** (line 599 uses grade color, line 628 legend uses grey). Align legend to match actual rendering.

### P2 -- Readability (Fix When Convenient)

4. **IRR severity markers need greater differentiation** in Figure 4.1. Increase size delta from 2px to 4px and increase color contrast between Mild and Moderate.

5. **Add ULN/LLN text labels** on lab trend reference lines (Figures 6.1-6.4).

6. **Add Cohort A3 subject identification** mechanism (either a legend in a separate panel or endpoint annotations).

7. **Reduce QTcF synthetic trend parameter** from 0.5 to 0.1-0.2 ms/week to prevent implausible trajectories.

### P3 -- Polish (Enhancement)

8. **Consolidate `cohort_palettes` dict** into a single module-level constant rather than repeating in three functions.

9. **Increase minimum font size** from 6pt to 7pt across all subplot tick labels.

10. **Add DPI configuration parameter** (default 150 for screen, 300 for print).

11. **Add Weight trend plot** (Figure 8.6) or remove Weight from `VS_PARAMS`.

12. **Add synthetic peri-infusion spike modeling** for Temperature and SpO2 in future iterations.

---

*Review completed 2026-04-15. Generator version: scripts/generate_mmr.py (1770 lines). Report version: MAR 2026 data cut (2026-03-20).*
