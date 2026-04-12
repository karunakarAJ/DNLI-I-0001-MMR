# Data Directory

This directory holds the clinical data inputs for the MMR pipeline. **Data files are not committed to the repository** (excluded via .gitignore).

## Expected Data Layout

### EDC Datasets (`data/edc/`)
SAS7BDAT files from the EDC snapshot:

| File | Description |
|------|-------------|
| `dm.sas7bdat` | Demographics |
| `enroll.sas7bdat` | Enrollment |
| `ie.sas7bdat` | Inclusion/Exclusion criteria |
| `ae.sas7bdat` | Adverse Events |
| `irr.sas7bdat` | Infusion-Related Reactions |
| `ex.sas7bdat` | Exposure (primary) |
| `exiv1.sas7bdat` | Exposure (secondary infusion) |
| `eos.sas7bdat` | End of Study |
| `eot.sas7bdat` | End of Treatment |
| `vs.sas7bdat` | Vital Signs |
| `lab.sas7bdat` | Local Laboratory |
| `eg1.sas7bdat` | ECG |
| `cm.sas7bdat` | Concomitant Medications |
| `mh.sas7bdat` | Medical History |
| `dov.sas7bdat` | Date of Visit |
| `dc1.sas7bdat` | Disease Characteristics |
| `abr.sas7bdat` | Auditory Brainstem Response |

### Vendor Data (`data/`)

| File | Source | Description |
|------|--------|-------------|
| `mlm_dnli-i-0001_safety.csv` | MLM Medical Labs | Central safety lab results |
| `bioagilytix_dnli-i-0001_ada.csv` | Bioagilytix | Anti-Drug Antibody data |
| `frontage_dnli-i-0001_urine_hs_ds.csv` | Frontage Labs | Urine Heparan Sulfate |
| `frontage_dnli-i-0001_urine_creatinine.csv` | Frontage Labs | Urine Creatinine (for HS normalization) |
| `ggc_dnli-i-0001_sgsh.csv` | GGC | SGSH Genotyping |
| `Clario_DNLI_I_0001_Organ_Vol.sas7bdat` | Clario | Abdomen MRI organ volumes |
| `CLARIO_DNLI_I_0001_vMRI.sas7bdat` | Clario | Brain MRI |
| `SOA.csv` | Internal | Schedule of Activities reference |
| `IE_Description.csv` | Internal | I/E criteria descriptions |
| `DNLI-I-0001_PROD_*.csv` | 4G Clinical | IRT/PROD data |

### Documents (`documents/`)

| File | Description |
|------|-------------|
| `I1 Specs.xlsx` | Reference ranges (ADEG_RANGE, ADVS_RANGE sheets) |
| `DNLI-I-0001_Deviations_*.xlsx` | Protocol deviation log |
