# Consensus Safety Review — Multi-Model

**Synthesizer Model:** claude-sonnet-4-20250514  
**Date:** 2026-04-15  
**Agents Synthesized:** 4  
**Tokens:** 9080 input / 2436 output  

---

# Consensus Safety Review — DNLI-I-0001 MMR
**Date:** 2026-04-15
**Models Used:** Claude-3.5-Sonnet, GPT-4o
**Agents:** Clinician Safety Reviewer, Safety Biostatistician, Data Visualization Reviewer (×2)

## Cross-Agent Agreement Matrix
| Safety Domain | Claude Clinician | Claude Biostat | Claude Visual | GPT Visual | Consensus |
|---------------|------------------|----------------|---------------|------------|-----------|
| IRR/Anaphylaxis | CRITICAL | HIGH | HIGH | HIGH | **CRITICAL** |
| Immunogenicity | HIGH | HIGH | - | HIGH | **HIGH** |
| Respiratory Safety | HIGH | CRITICAL | HIGH | - | **HIGH** |
| Data Visualization | - | MEDIUM | CRITICAL | CRITICAL | **CRITICAL** |
| Hepatotoxicity | LOW | LOW | LOW | LOW | **LOW** |
| Cardiac Safety | MEDIUM | MEDIUM | HIGH | MEDIUM | **MEDIUM** |
| Statistical Power | - | HIGH | - | - | **HIGH** |

## High-Confidence Findings (≥2 agents agree)

### 1. **CRITICAL: Universal IRR with Anaphylaxis Signal**
- **Agreement:** All 4 agents flagged as HIGH-CRITICAL priority
- **Evidence:** 100% IRR incidence (442 events), 75% moderate-severe, 1 anaphylactic reaction in B1 cohort
- **Risk:** Immediate threat to patient safety, especially in youngest cohort (27 months)

### 2. **CRITICAL: Complete Absence of Data Visualizations**
- **Agreement:** Both visualization agents flagged as CRITICAL
- **Evidence:** All 17+ figures show only placeholder text, rendering report unusable for regulatory review
- **Risk:** Cannot assess safety patterns, trends, or individual patient trajectories

### 3. **HIGH: Severe Immunogenicity Compromising Treatment**
- **Agreement:** 3/4 agents flagged as HIGH priority
- **Evidence:** 95% ADA positivity (19/20), 60% neutralizing antibodies, dose adjustments required
- **Risk:** Treatment effectiveness compromised, may drive increased IRR severity

### 4. **HIGH: Respiratory Safety Signals**
- **Agreement:** Clinician (HIGH) and Biostatistician (CRITICAL)
- **Evidence:** SpO2 <92% in 10% of patients, anaphylaxis in 50% of B1 cohort (1/2 patients)
- **Risk:** Life-threatening respiratory compromise during infusions

### 5. **HIGH: Inadequate Statistical Power for Safety Conclusions**
- **Agreement:** Biostatistician identified, supported by visualization concerns
- **Evidence:** Cohorts as small as N=2, confidence intervals 1.3%-98.7% for critical events
- **Risk:** Cannot reliably detect or rule out serious safety signals

## Divergent Findings (agents disagree)

### **QTcF Prolongation Risk Level**
- **Disagreement:** Clinician (MEDIUM) vs Visual Claude (HIGH) vs GPT Visual (MEDIUM)
- **Issue:** 3/20 patients (15%) with QTcF >450ms during IRR events
- **Resolution:** **MEDIUM risk** - Events appear transient and IRR-related, but require enhanced monitoring given repeated cardiac stress over extended treatment periods
- **Action:** Implement continuous cardiac monitoring during infusions with clear stopping criteria

### **Age-Related Safety Concerns**
- **Disagreement:** Only Clinician identified as HIGH priority
- **Issue:** Youngest cohort (B1, 27 months) shows 100% moderate-severe IRR rate
- **Resolution:** **HIGH risk** - Pediatric vulnerability is clinically significant even if not statistically powered
- **Action:** Establish age-specific monitoring protocols and consider minimum age restrictions

### **Site Heterogeneity Assessment**
- **Disagreement:** Only Biostatistician flagged this concern
- **Issue:** UNC Chapel Hill enrolled 40% of patients including only drug-related SAE
- **Resolution:** **MEDIUM priority** - Important for data integrity but secondary to immediate safety signals
- **Action:** Perform site-level safety analysis in future reports

## Unified Risk Assessment
| Domain | Risk Level | Confidence | Evidence | Action |
|--------|-----------|------------|----------|--------|
| IRR/Anaphylaxis | **CRITICAL** | Very High | 100% IRR, 1 anaphylaxis, 75% mod-severe | Immediate protocol modifications |
| Data Integrity | **CRITICAL** | Very High | 0/17+ plots functional | Complete visualization reconstruction |
| Immunogenicity | **HIGH** | High | 95% ADA+, 60% neutralizing | Immunosuppressive strategy |
| Respiratory Safety | **HIGH** | High | 10% hypoxia, 50% B1 anaphylaxis | Enhanced monitoring protocols |
| Statistical Power | **HIGH** | High | N=2-10 per cohort | Bayesian modeling approach |
| Cardiac Safety | **MEDIUM** | Moderate | 15% QTcF >450ms | Continuous ECG monitoring |
| Hepatotoxicity | **LOW** | High | 0/20 Hy's Law cases | Continue standard monitoring |

## Top 10 Recommendations (Priority-Ordered)

### 1. **IMMEDIATE: Implement Emergency Anaphylaxis Protocols**
- Mandate epinephrine availability and intensivist backup at all infusion sites
- Require continuous pulse oximetry and cardiac monitoring during all infusions
- Establish SpO2 <95% as mandatory infusion stop criterion

### 2. **URGENT: Generate Complete Safety Visualization Suite**
- Reconstruct all 17+ missing safety plots before any regulatory submission
- Create IRR timeline showing all 442 events by severity and dose relationship
- Generate eDISH plots to confirm hepatotoxicity assessment

### 3. **CRITICAL: Develop Immunosuppressive Premedication Strategy**
- Implement rituximab/methotrexate protocols similar to other enzyme replacement therapies
- Establish ADA titer thresholds for dose modifications
- Add comprehensive premedication: H1/H2 antihistamines, corticosteroids, montelukast

### 4. **HIGH: Implement Bayesian Safety Monitoring**
- Use informative priors from similar gene therapy trials given small sample sizes
- Establish formal early stopping criteria for respiratory events
- Create hierarchical modeling borrowing strength across cohorts

### 5. **HIGH: Establish Age-Specific Safety Protocols**
- Require pediatric critical care consultation for participants <48 months
- Consider minimum age restriction (>36 months) given B1 cohort severity
- Implement age-adjusted monitoring frequency and intervention thresholds

### 6. **MEDIUM: Enhance IRR Management Algorithm**
- Develop standardized prophylaxis and restart criteria
- Consider extended infusion times (>4 hours) or split dosing
- Implement IRR severity scoring system with clear intervention triggers

### 7. **MEDIUM: Implement Comprehensive Cardiac Monitoring**
- Add quarterly echocardiograms and 6-monthly Holter monitoring
- Include BNP/troponin in safety laboratories
- Establish QTcF stopping criteria (>480ms any time, >460ms recurrent)

### 8. **MEDIUM: Develop Statistical Modeling Framework**
- Implement negative binomial regression for recurrent IRR events
- Create exposure-response models incorporating ADA status
- Perform time-to-event analysis for IRR patterns and SAEs

### 9. **MEDIUM: Enhance Infectious Disease Monitoring**
- Regular cultures and infectious disease consultation protocols
- Consider prophylaxis in high-risk participants
- Monitor for immunocompromise from underlying disease vs. drug effect

### 10. **LOW: Improve Data Management and Audit Trails**
- Implement formal data lock procedures with clear version control
- Create comprehensive change tracking for post-publication updates
- Develop missing data analysis plan with sensitivity testing

## Blind Spot Analysis

### **Potential Missed Safety Concerns:**

1. **Long-term Neurological Effects:** With neurological SAEs (seizure, dyskinesia, cognitive disorder) in a neurodegenerative disease, distinguishing drug effects from disease progression requires more sophisticated assessment tools than currently implemented.

2. **Cumulative Cardiac Stress:** While individual QTcF prolongations appear transient, the cumulative effect of 442 IRR episodes with repeated cardiac stress over 52+ weeks median exposure lacks adequate assessment.

3. **Growth and Development Impact:** In pediatric patients aged 27-198 months, potential effects on growth velocity, pubertal development, and cognitive development are not systematically monitored.

4. **Caregiver/Family Impact:** Psychological burden on families from 100% IRR incidence and frequent hospitalizations may affect treatment compliance and quality of life.

5. **Drug-Drug Interactions:** Potential interactions between DNL-126 and concurrent medications (seizure medications, supportive care drugs) are not systematically evaluated.

6. **Reproductive Toxicology:** For older adolescent participants, future reproductive health implications are not addressed.

## Model Performance Notes

### **Claude vs GPT Assessment Differences:**

1. **Analytical Depth:** Claude models provided more granular statistical and clinical analysis with specific recommendations, while GPT focused more on high-level regulatory compliance.

2. **Risk Prioritization:** Claude consistently rated risks higher (CRITICAL/HIGH) while GPT was more conservative (HIGH/MEDIUM), suggesting different risk tolerance thresholds.

3. **Clinical Context:** Claude Clinician provided more detailed clinical management recommendations, while GPT Visual focused more on regulatory presentation standards.

4. **Statistical Sophistication:** Claude Biostatistician provided more advanced statistical modeling suggestions (Bayesian hierarchical models, negative binomial regression) compared to GPT's more standard approaches.

5. **Consistency:** Claude agents showed better cross-domain integration and consistent terminology, while GPT assessments were more isolated by agent role.

### **Overall Model Reliability:**
Both model families identified the same critical safety signals (IRR/anaphylaxis, immunogenicity, visualization absence), suggesting high reliability for major safety concerns. Differences emerged primarily in risk gradation and statistical methodology preferences rather than fundamental safety signal detection.