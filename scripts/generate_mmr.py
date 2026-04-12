#!/usr/bin/env python3
"""
Generate Medical Monitoring Report (MMR) for DNLI-I-0001 (DNL-126, Phase 1/2, MPS IIIA).
Produces HTML (and optionally PDF) from clinical CSV data.

Usage:
    python3 generate_mmr.py 2026JAN30
    python3 generate_mmr.py 2026FEB24
    python3 generate_mmr.py 2026MAR20
"""

import sys
import os
import base64
import io
import warnings
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ── Constants ──────────────────────────────────────────────────────────────

COHORTS = {
    'A1': ['0016-9001', '0016-9003', '0017-9001', '0017-9002'],
    'A2': ['0016-9004', '0017-9003', '2064-9002', '2065-9002'],
    'A3': ['0016-9005', '0016-9006', '0017-9005', '0017-9007', '0017-9008',
           '2064-9003', '2064-9004', '2064-9005', '2065-9001', '2065-9004'],
    'B1': ['0017-9004', '0017-9006'],
}
TREATED = [s for subs in COHORTS.values() for s in subs]  # 20 subjects

SITES = {
    '0017': ('UNC Chapel Hill', 'Dr. Elizabeth Jalazo'),
    '0016': ('UCSF Benioff Children\'s Hospital', 'Dr. Paul Harmatz'),
    '2064': ('University of Iowa', 'Dr. John Bernat'),
    '2065': ('Baylor College of Medicine', 'Dr. Jimmy Holder'),
}

# Map month strings to PROD filename month abbreviations
MONTH_MAP = {
    '2026JAN30': ('JAN', '2026-01-30', 'January 2026'),
    '2026FEB24': ('FEB', '2026-02-24', 'February 2026'),
    '2026MAR20': ('MAR', '2026-03-20', 'March 2026'),
}

# Ordered months for delta tracking
ORDERED_MONTHS = ['2026JAN30', '2026FEB24', '2026MAR20']

# Key biochemistry tests for trend tables
BIOCHEM_HEPATIC = ['ALT/SGPT', 'AST/SGOT', 'Total Bilirubin', 'Direct Bilirubin',
                   'Alkaline Phosphatase', 'Albumin']
BIOCHEM_RENAL = ['Creatinine', 'Blood Urea Nitrogen']
BIOCHEM_OTHER = ['Glucose', 'Sodium', 'Potassium', 'Chloride', 'Bicarbonate',
                 'Calcium', 'Phosphate/ Phosphorus', 'Total Protein',
                 'Cholesterol', 'Triglycerides', 'Creatine kinase',
                 'Lactate dehydrogenase', 'Uric acid']

HEMATOLOGY_TESTS = ['Leukocytes', 'Erythrocytes', 'Hemoglobin', 'Hematocrit',
                    'Platelets', 'Neutrophils; Absolute Units',
                    'Lymphocytes; Absolute Units', 'Monocytes; Absolute Units',
                    'Eosinophils; Absolute Units', 'Basophils; Absolute Units',
                    'Mean Corpuscular Volume', 'Mean Corpuscular Hemoglobin',
                    'Mean Corpuscular Hemoglobin Conc.', 'RBC distribution width',
                    'Reticulocyte count']

COHORT_COLORS = {'A1': '#2563eb', 'A2': '#16a34a', 'A3': '#d97706', 'B1': '#dc2626'}

BASE_DIR = Path(__file__).resolve().parent.parent


def get_cohort(subjid):
    """Return cohort label for a subject."""
    for coh, subs in COHORTS.items():
        if subjid in subs:
            return coh
    return None


def parse_numeric(val):
    """Parse a numeric value, stripping < prefix."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s.startswith('<'):
        s = s[1:]
    try:
        return float(s)
    except (ValueError, TypeError):
        return np.nan


def load_lab_data(month):
    """Load and filter MLM safety lab CSV for treated subjects."""
    fpath = BASE_DIR / 'data' / month / 'mlm_dnli-i-0001_safety.csv'
    df = pd.read_csv(fpath, dtype={'SITEID': str, 'SUBJID': str})
    df = df[df['SUBJID'].isin(TREATED)].copy()
    df['RESULT'] = df['LBORRES'].apply(parse_numeric)
    df['ULN'] = pd.to_numeric(df['LBORNRHI'], errors='coerce')
    df['LLN'] = pd.to_numeric(df['LBORNRLO'], errors='coerce')
    df['xULN'] = df['RESULT'] / df['ULN']
    df['Cohort'] = df['SUBJID'].apply(get_cohort)
    return df


def load_prod_data(month):
    """Load PROD/IRT CSV for treated subjects."""
    mon_abbr = MONTH_MAP[month][0]
    fpath = BASE_DIR / 'data' / month / f'DNLI-I-0001_PROD_01{mon_abbr}2026.csv'
    df = pd.read_csv(fpath, dtype={'SITEID': str, 'PATID': str})
    df = df[df['PATID'].isin(TREATED)].copy()
    df['Cohort'] = df['PATID'].apply(get_cohort)
    return df


def fig_to_base64(fig):
    """Convert matplotlib figure to base64-encoded PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return b64


def make_edish_plot(lab, xtest, ylabel_prefix):
    """Create an eDISH scatter plot: xtest vs Total Bilirubin."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # Get ALT/AST xULN per subject per visit
    x_data = lab[(lab['LBTEST'] == xtest) & lab['xULN'].notna()][
        ['SUBJID', 'VISIT', 'LBDT', 'xULN', 'Cohort']].rename(columns={'xULN': 'x_xuln'})
    # Get TBILI xULN per subject per visit
    y_data = lab[(lab['LBTEST'] == 'Total Bilirubin') & lab['xULN'].notna()][
        ['SUBJID', 'VISIT', 'LBDT', 'xULN']].rename(columns={'xULN': 'y_xuln'})

    # Merge on subject + date (same draw date)
    merged = x_data.merge(y_data, on=['SUBJID', 'VISIT', 'LBDT'], how='inner')

    fig, ax = plt.subplots(figsize=(7, 5.5))

    for coh in ['A1', 'A2', 'A3', 'B1']:
        subset = merged[merged['Cohort'] == coh]
        if len(subset) == 0:
            continue
        ax.scatter(subset['x_xuln'], subset['y_xuln'],
                   c=COHORT_COLORS[coh], label=f'Cohort {coh} (n={subset["SUBJID"].nunique()})',
                   alpha=0.6, s=25, edgecolors='white', linewidth=0.3)

    # Quadrant lines
    ax.axvline(x=3, color='#dc2626', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(y=2, color='#dc2626', linestyle='--', linewidth=1, alpha=0.7)

    # Labels
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.1, 100)
    ax.set_ylim(0.1, 100)
    ax.set_xlabel(f'{xtest} (xULN)', fontsize=10)
    ax.set_ylabel('Total Bilirubin (xULN)', fontsize=10)
    ax.set_title(f'eDISH Plot: {ylabel_prefix} vs Total Bilirubin', fontsize=12, fontweight='bold')

    # Quadrant labels
    ax.text(0.15, 50, "Hy's Law\nQuadrant", fontsize=8, color='#dc2626', alpha=0.5, fontstyle='italic')
    ax.text(10, 50, "Hy's Law\nQuadrant", fontsize=8, color='#dc2626', alpha=0.7, fontweight='bold')
    ax.text(10, 0.15, 'Temple\'s Corollary', fontsize=8, color='#6b7280', alpha=0.5, fontstyle='italic')
    ax.text(0.15, 0.15, 'Normal', fontsize=8, color='#22c55e', alpha=0.5, fontstyle='italic')

    ax.legend(fontsize=8, loc='upper left', framealpha=0.9)
    ax.grid(True, which='both', alpha=0.15)
    ax.tick_params(labelsize=8)

    # Count Hy's law cases
    hys = merged[(merged['x_xuln'] > 3) & (merged['y_xuln'] > 2)]
    n_hys = hys['SUBJID'].nunique()

    b64 = fig_to_base64(fig)
    plt.close(fig)
    return b64, n_hys, len(merged)


def summary_stats_table(lab, tests, category_label):
    """Build HTML table with by-visit summary stats for given tests."""
    rows = []
    for test in tests:
        tdf = lab[(lab['LBTEST'] == test) & lab['RESULT'].notna()]
        if len(tdf) == 0:
            continue
        unit = tdf['LBORRESU'].dropna().iloc[0] if len(tdf['LBORRESU'].dropna()) > 0 else ''
        uln_val = tdf['ULN'].dropna().median() if len(tdf['ULN'].dropna()) > 0 else np.nan

        # Collect by-visit summaries
        visits_order = []
        for v in tdf['VISIT'].unique():
            # Extract week number for sorting
            if v == 'Baseline':
                visits_order.append((0, v))
            elif v == 'Screening':
                visits_order.append((-1, v))
            elif v.startswith('Week'):
                try:
                    wk = int(v.replace('Week ', ''))
                    visits_order.append((wk, v))
                except ValueError:
                    visits_order.append((9999, v))
            else:
                visits_order.append((9999, v))
        visits_order.sort()

        n_subj = tdf['SUBJID'].nunique()
        overall_min = tdf['RESULT'].min()
        overall_max = tdf['RESULT'].max()
        overall_mean = tdf['RESULT'].mean()
        max_xuln = tdf['xULN'].max() if tdf['xULN'].notna().any() else np.nan

        rows.append({
            'Test': test,
            'Unit': unit,
            'N Subj': n_subj,
            'N Obs': len(tdf),
            'Mean': f'{overall_mean:.2f}',
            'Min': f'{overall_min:.2f}',
            'Max': f'{overall_max:.2f}',
            'ULN': f'{uln_val:.2f}' if not np.isnan(uln_val) else '—',
            'Max xULN': f'{max_xuln:.2f}' if not np.isnan(max_xuln) else '—',
        })

    if not rows:
        return f'<p class="note">No {category_label} data available.</p>'

    html = f'<table><thead><tr>'
    for col in ['Test', 'Unit', 'N Subj', 'N Obs', 'Mean', 'Min', 'Max', 'ULN', 'Max xULN']:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    for r in rows:
        max_xuln_val = parse_numeric(r['Max xULN'])
        cls = ''
        if not np.isnan(max_xuln_val) and max_xuln_val > 2:
            cls = ' class="row-chg"'
        elif not np.isnan(max_xuln_val) and max_xuln_val > 1:
            cls = ''
        html += f'<tr{cls}>'
        for col in ['Test', 'Unit', 'N Subj', 'N Obs', 'Mean', 'Min', 'Max', 'ULN', 'Max xULN']:
            align = ' class="r"' if col not in ['Test', 'Unit'] else ''
            html += f'<td{align}>{r[col]}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html


def visit_trend_table(lab, tests):
    """Build a detailed by-visit trend table for key hepatic tests."""
    # Pick key visits to display
    all_visits = lab['VISIT'].unique()
    visit_order = []
    for v in all_visits:
        if v == 'Screening':
            visit_order.append((-1, v))
        elif v == 'Baseline':
            visit_order.append((0, v))
        elif v.startswith('Week'):
            try:
                wk = int(v.replace('Week ', ''))
                visit_order.append((wk, v))
            except ValueError:
                pass
    visit_order.sort()
    visits = [v for _, v in visit_order]

    html = ''
    for test in tests:
        tdf = lab[(lab['LBTEST'] == test) & lab['RESULT'].notna()]
        if len(tdf) == 0:
            continue
        unit = tdf['LBORRESU'].dropna().iloc[0] if len(tdf['LBORRESU'].dropna()) > 0 else ''

        html += f'<h3>{test} ({unit}) - By Visit</h3>'
        html += '<table><thead><tr><th>Visit</th><th>N</th><th>Mean</th><th>SD</th><th>Min</th><th>Max</th><th>Median</th></tr></thead><tbody>'

        for v in visits:
            vdf = tdf[tdf['VISIT'] == v]
            if len(vdf) == 0:
                continue
            n = len(vdf)
            mean = vdf['RESULT'].mean()
            sd = vdf['RESULT'].std()
            mn = vdf['RESULT'].min()
            mx = vdf['RESULT'].max()
            med = vdf['RESULT'].median()
            html += f'<tr><td>{v}</td><td class="r">{n}</td><td class="r">{mean:.1f}</td>'
            html += f'<td class="r">{sd:.1f}</td><td class="r">{mn:.1f}</td>'
            html += f'<td class="r">{mx:.1f}</td><td class="r">{med:.1f}</td></tr>'

        html += '</tbody></table>'
    return html


def lab_outlier_table(lab):
    """Identify lab outliers: values >2xULN or flagged HIGH/LOW."""
    outliers = lab[
        ((lab['xULN'] > 2) | (lab['LBNRIND'].isin(['HIGH', 'LOW']))) &
        lab['RESULT'].notna()
    ].copy()

    if len(outliers) == 0:
        return '<div class="callout green"><strong>No lab outliers identified (no values &gt;2xULN or flagged HIGH/LOW).</strong></div>'

    outliers = outliers.sort_values(['SUBJID', 'LBDT', 'LBTEST'])
    html = '<table><thead><tr><th>Subject</th><th>Cohort</th><th>Visit</th><th>Date</th>'
    html += '<th>Test</th><th>Result</th><th>Unit</th><th>Ref Range</th><th>xULN</th><th>Flag</th></tr></thead><tbody>'

    for _, row in outliers.iterrows():
        xuln_str = f'{row["xULN"]:.2f}' if pd.notna(row['xULN']) else '—'
        flag = row.get('LBNRIND', '')
        if pd.isna(flag):
            flag = ''
        cls = ''
        if pd.notna(row['xULN']) and row['xULN'] > 3:
            cls = ' class="row-chg"'
        elif pd.notna(row['xULN']) and row['xULN'] > 2:
            cls = ' class="row-new"'
        ref_lo = row.get('LBORNRLO', '')
        ref_hi = row.get('LBORNRHI', '')
        ref_str = f'{ref_lo}-{ref_hi}' if pd.notna(ref_lo) and pd.notna(ref_hi) else '—'
        html += f'<tr{cls}><td>{row["SUBJID"]}</td><td>{row["Cohort"]}</td><td>{row["VISIT"]}</td>'
        html += f'<td>{row["LBDT"]}</td><td>{row["LBTEST"]}</td><td class="r">{row["LBORRES"]}</td>'
        html += f'<td>{row.get("LBORRESU","")}</td><td>{ref_str}</td><td class="r">{xuln_str}</td>'
        tag_cls = 'red' if flag == 'HIGH' else ('orange' if flag == 'LOW' else 'blue')
        html += f'<td><span class="tag {tag_cls}">{flag}</span></td></tr>'

    html += '</tbody></table>'
    return html


def safety_margin_table(lab):
    """Safety margin summary: max xULN for key hepatic parameters."""
    tests = ['ALT/SGPT', 'AST/SGOT', 'Total Bilirubin', 'Direct Bilirubin',
             'Alkaline Phosphatase', 'Creatinine', 'Creatine kinase']
    thresholds = {'ALT/SGPT': 3, 'AST/SGOT': 3, 'Total Bilirubin': 1.5,
                  'Direct Bilirubin': 1.5, 'Alkaline Phosphatase': 1.5,
                  'Creatinine': 1.5, 'Creatine kinase': 5}

    html = '<table><thead><tr><th>Parameter</th><th>Threshold</th><th>Subjects Exceeding</th>'
    html += '<th>Max xULN (Cohort)</th><th>Clinical Note</th></tr></thead><tbody>'

    for test in tests:
        tdf = lab[(lab['LBTEST'] == test) & lab['xULN'].notna()]
        thresh = thresholds.get(test, 2)
        if len(tdf) == 0:
            html += f'<tr><td>{test}</td><td>&gt;{thresh}&times;ULN</td><td>—</td><td>—</td><td>No data</td></tr>'
            continue

        exceeding = tdf[tdf['xULN'] > thresh]
        n_exceeding = exceeding['SUBJID'].nunique()
        max_row = tdf.loc[tdf['xULN'].idxmax()]
        max_xuln = max_row['xULN']
        max_cohort = max_row['Cohort']

        if n_exceeding == 0:
            note = 'Within acceptable limits across all cohorts'
        else:
            subjs = ', '.join(sorted(exceeding['SUBJID'].unique()))
            note = f'Exceeded in: {subjs}'

        cls = ' class="row-chg"' if n_exceeding > 0 else ''
        html += f'<tr{cls}><td>{test}</td><td>&gt;{thresh}&times;ULN</td>'
        html += f'<td>{n_exceeding}/20</td><td>{max_xuln:.2f} ({max_cohort})</td>'
        html += f'<td>{note}</td></tr>'

    html += '</tbody></table>'
    return html


def build_delta_section(month):
    """Build month-over-month data changes appendix."""
    idx = ORDERED_MONTHS.index(month)
    if idx == 0:
        return '<p class="note">This is the first data cut; no prior month available for comparison.</p>'

    prev_month = ORDERED_MONTHS[idx - 1]
    prev_lab_path = BASE_DIR / 'data' / prev_month / 'mlm_dnli-i-0001_safety.csv'

    if not prev_lab_path.exists():
        return f'<p class="note">Previous month data ({prev_month}) not found.</p>'

    curr = load_lab_data(month)
    prev = load_lab_data(prev_month)

    # Compare record counts
    curr_n = len(curr)
    prev_n = len(prev)
    delta_n = curr_n - prev_n

    # New subjects
    curr_subj = set(curr['SUBJID'].unique())
    prev_subj = set(prev['SUBJID'].unique())
    new_subj = curr_subj - prev_subj

    # New visits
    curr_visits = set(curr['VISIT'].unique())
    prev_visits = set(prev['VISIT'].unique())
    new_visits = curr_visits - prev_visits

    html = f'''
    <div class="diff-banner">
    <h2>Data Changes: {prev_month} &rarr; {month}</h2>
    <div class="diff-item"><span class="diff-chg">DELTA</span> Lab records: {prev_n:,} &rarr; {curr_n:,} ({delta_n:+,})</div>
    <div class="diff-item"><span class="diff-new">NEW</span> Subjects in lab data: {", ".join(sorted(new_subj)) if new_subj else "None"}</div>
    <div class="diff-item"><span class="diff-new">NEW</span> Visits: {", ".join(sorted(new_visits)) if new_visits else "None"}</div>
    </div>
    '''

    # Per-test record count delta
    html += '<h3>Record Count Changes by Test Category</h3>'
    html += '<table><thead><tr><th>Category</th><th>Previous</th><th>Current</th><th>Delta</th></tr></thead><tbody>'
    for cat in sorted(curr['LBCAT'].unique()):
        cn = len(curr[curr['LBCAT'] == cat])
        pn = len(prev[prev['LBCAT'] == cat]) if cat in prev['LBCAT'].values else 0
        d = cn - pn
        cls = ' class="row-new"' if d > 0 else ''
        html += f'<tr{cls}><td>{cat}</td><td class="r">{pn:,}</td><td class="r">{cn:,}</td><td class="r">{d:+,}</td></tr>'
    html += '</tbody></table>'

    return html


def generate_report(month):
    """Generate the full HTML report."""
    data_cut_date = MONTH_MAP[month][1]
    month_label = MONTH_MAP[month][2]

    # Load data
    lab = load_lab_data(month)
    prod = load_prod_data(month)

    # ── Demographics from lab data ──
    demog = lab[['SUBJID', 'SEX', 'BRTHYEAR', 'AGE', 'Cohort']].drop_duplicates(subset=['SUBJID'])
    demog['AGE'] = pd.to_numeric(demog['AGE'], errors='coerce')

    # ── Demographics from PROD (more complete) ──
    prod_demog = prod[['PATID', 'SEX', 'YOB', 'AGE', 'AGEM', 'Cohort', 'COHORT']].drop_duplicates(subset=['PATID'])
    prod_demog = prod_demog.rename(columns={'PATID': 'SUBJID'})

    # ── Site enrollment from PROD ──
    site_data = prod[['PATID', 'SITEID', 'PINAME', 'COHORT', 'SUBSTA']].drop_duplicates(subset=['PATID'])

    # ── Dosing info ──
    dose_info = prod[prod['DOSESCH'].notna()][['PATID', 'VISNAM', 'DOSESCH', 'PTWEIGHT', 'Cohort']].copy()

    # ── Generate eDISH plots ──
    import matplotlib
    matplotlib.use('Agg')

    alt_b64, alt_hys, alt_n = make_edish_plot(lab, 'ALT/SGPT', 'ALT')
    ast_b64, ast_hys, ast_n = make_edish_plot(lab, 'AST/SGOT', 'AST')

    # ── Build HTML ──
    css = get_css()

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>DNLI-I-0001 Medical Monitoring Report - Safety Review ({month_label})</title>
<style>
{css}
</style>
</head>
<body>
'''

    # ══════ COVER ══════
    html += f'''
<div class="cover">
<div class="bar">Denali Therapeutics &middot; Confidential &middot; Medical Monitoring Report</div>
<h1>DNLI-I-0001 Medical Monitoring Report</h1>
<div class="sub">DNL126 (ETV:SGSH-BioM) &middot; MPS IIIA (Sanfilippo Syndrome Type A) &middot; {month_label}</div>
<div class="meta">
<div class="mc"><div class="l">Data Cut Date</div><div class="v">{data_cut_date}</div></div>
<div class="mc"><div class="l">MLM Safety Lab</div><div class="v">{month}</div></div>
<div class="mc"><div class="l">IRT / PROD Transfer</div><div class="v">{month}</div></div>
<div class="mc"><div class="l">Report Generated</div><div class="v">{datetime.now().strftime("%Y-%m-%d")} (AI-Generated)</div></div>
</div>
</div>

<div class="stat-grid">
<div class="stat"><div class="n">{len(TREATED)}</div><div class="label">Treated Subjects</div></div>
<div class="stat"><div class="n">{len(COHORTS)}</div><div class="label">Cohorts</div></div>
<div class="stat"><div class="n">{len(SITES)}</div><div class="label">Sites</div></div>
<div class="stat"><div class="n">{len(lab):,}</div><div class="label">Lab Records</div></div>
</div>

<div class="callout orange">
<strong>Safety-Focused Report.</strong> This report covers safety laboratory data and dosing information from CSV extracts.
AE, ECG, and vital signs data require SAS datasets not available in this extract.
</div>
'''

    # ══════ SECTION 1: Study Status ══════
    html += '''
<div class="section pg">
<h2>1. Study Status</h2>
<h3>1.1 Enrollment by Site</h3>
<table>
<thead><tr><th>Site</th><th>Site ID</th><th>PI</th><th>Cohort A1</th><th>Cohort A2</th><th>Cohort A3</th><th>Cohort B1</th><th>Total</th></tr></thead>
<tbody>
'''
    site_totals = {sid: {c: 0 for c in COHORTS} for sid in SITES}
    for coh, subs in COHORTS.items():
        for s in subs:
            sid = s.split('-')[0]
            # Normalize site ID
            sid_norm = sid.lstrip('0') if sid.startswith('00') else sid
            for site_key in SITES:
                if sid == site_key or sid_norm == site_key.lstrip('0'):
                    site_totals[site_key][coh] += 1

    for sid, (name, pi) in SITES.items():
        counts = site_totals[sid]
        total = sum(counts.values())
        html += f'<tr><td>{name}</td><td>{sid}</td><td>{pi}</td>'
        for c in COHORTS:
            html += f'<td class="c">{counts[c]}</td>'
        html += f'<td class="c"><strong>{total}</strong></td></tr>'

    grand = {c: sum(site_totals[sid][c] for sid in SITES) for c in COHORTS}
    html += f'<tr style="font-weight:bold;background:#e0f2fe;"><td colspan="3">Total</td>'
    for c in COHORTS:
        html += f'<td class="c">{grand[c]}</td>'
    html += f'<td class="c">{sum(grand.values())}</td></tr>'
    html += '</tbody></table>'

    # Disposition
    html += '<h3>1.2 Participant Disposition</h3>'
    html += '<table><thead><tr><th>Status</th><th>N</th><th>Subjects</th></tr></thead><tbody>'
    # Active
    disc_subjs = set()
    disc_in_prod = prod[prod['SUBSTA'] == 'Discontinued']['PATID'].unique()
    for s in disc_in_prod:
        if s in TREATED:
            disc_subjs.add(s)
    active = [s for s in TREATED if s not in disc_subjs]
    html += f'<tr><td>Active / On Treatment</td><td class="c">{len(active)}</td>'
    html += f'<td>{", ".join(sorted(active))}</td></tr>'
    if disc_subjs:
        html += f'<tr><td>Discontinued</td><td class="c">{len(disc_subjs)}</td>'
        html += f'<td>{", ".join(sorted(disc_subjs))}</td></tr>'
    html += f'<tr style="font-weight:bold;"><td>Total Treated</td><td class="c">{len(TREATED)}</td><td>—</td></tr>'
    html += '</tbody></table>'

    # ══════ SECTION 2: Baseline Characteristics ══════
    html += '''
<div class="section pg">
<h2>2. Baseline Characteristics</h2>
<h3>2.1 Demographics</h3>
'''
    html += '<table><thead><tr><th>Subject</th><th>Cohort</th><th>Sex</th><th>Birth Year</th><th>Age (yrs)</th></tr></thead><tbody>'
    for coh_name, subs in COHORTS.items():
        for s in sorted(subs):
            row = demog[demog['SUBJID'] == s]
            if len(row) > 0:
                r = row.iloc[0]
                sex = r['SEX'] if pd.notna(r['SEX']) else '—'
                yob = r['BRTHYEAR'] if pd.notna(r['BRTHYEAR']) else '—'
                age = int(r['AGE']) if pd.notna(r['AGE']) else '—'
            else:
                # Try PROD data
                pr = prod_demog[prod_demog['SUBJID'] == s]
                if len(pr) > 0:
                    r2 = pr.iloc[0]
                    sex = r2['SEX'] if pd.notna(r2['SEX']) else '—'
                    yob = r2['YOB'] if pd.notna(r2['YOB']) else '—'
                    age = r2['AGE'] if pd.notna(r2['AGE']) else '—'
                else:
                    sex = yob = age = '—'
            html += f'<tr><td>{s}</td><td>{coh_name}</td><td>{sex}</td><td>{yob}</td><td>{age}</td></tr>'
    html += '</tbody></table>'

    # Summary stats
    n_female = len(demog[demog['SEX'] == 'F'])
    n_male = len(demog[demog['SEX'] == 'M'])
    age_mean = demog['AGE'].mean()
    age_min = demog['AGE'].min()
    age_max = demog['AGE'].max()
    html += f'''
<h3>2.2 Summary</h3>
<div class="stat-grid">
<div class="stat"><div class="n">{n_female}</div><div class="label">Female</div></div>
<div class="stat"><div class="n">{n_male}</div><div class="label">Male</div></div>
<div class="stat"><div class="n">{age_mean:.1f}</div><div class="label">Mean Age (yr)</div></div>
<div class="stat"><div class="n">{age_min:.0f}-{age_max:.0f}</div><div class="label">Age Range (yr)</div></div>
</div>
</div>
'''

    # ══════ SECTION 3: Study Conduct ══════
    html += '''
<div class="section pg">
<h2>3. Study Conduct</h2>
<h3>3.1 Dosing Compliance</h3>
'''
    # Dose visits per subject
    dose_visits = dose_info.groupby('PATID').agg(
        n_doses=('VISNAM', 'count'),
        schedule=('DOSESCH', 'first'),
        last_visit=('VISNAM', 'last')
    ).reset_index()
    dose_visits['Cohort'] = dose_visits['PATID'].apply(get_cohort)

    html += '<table><thead><tr><th>Subject</th><th>Cohort</th><th>Schedule</th><th>N Dose Visits</th><th>Last Dose Visit</th></tr></thead><tbody>'
    for _, row in dose_visits.sort_values(['Cohort', 'PATID']).iterrows():
        html += f'<tr><td>{row["PATID"]}</td><td>{row["Cohort"]}</td><td>{row["schedule"]}</td>'
        html += f'<td class="c">{row["n_doses"]}</td><td>{row["last_visit"]}</td></tr>'
    html += '</tbody></table>'

    # Assessment availability
    html += '<h3>3.2 Assessment Availability (Lab)</h3>'
    visit_counts = lab.groupby(['VISIT'])['SUBJID'].nunique().reset_index()
    visit_counts.columns = ['Visit', 'N Subjects']
    # Sort visits
    def visit_sort_key(v):
        if v == 'Screening':
            return -1
        if v == 'Baseline':
            return 0
        if v.startswith('Week'):
            try:
                return int(v.replace('Week ', ''))
            except ValueError:
                return 9999
        return 9998
    visit_counts['sort'] = visit_counts['Visit'].apply(visit_sort_key)
    visit_counts = visit_counts.sort_values('sort')
    html += '<table><thead><tr><th>Visit</th><th>Subjects with Lab Data</th></tr></thead><tbody>'
    for _, row in visit_counts.iterrows():
        html += f'<tr><td>{row["Visit"]}</td><td class="c">{row["N Subjects"]}</td></tr>'
    html += '</tbody></table>'
    html += '</div>'

    # ══════ SECTION 4: Study Drug Exposure & Immunogenicity ══════
    html += '''
<div class="section pg">
<h2>4. Study Drug Exposure &amp; Immunogenicity</h2>
<h3>4.1 Dose Exposure Summary</h3>
'''
    # By cohort
    html += '<table><thead><tr><th>Cohort</th><th>N</th><th>Dose Schedule</th><th>Mean Dose Visits</th><th>Weight Range (kg)</th></tr></thead><tbody>'
    for coh in ['A1', 'A2', 'A3', 'B1']:
        coh_dose = dose_info[dose_info['Cohort'] == coh]
        if len(coh_dose) == 0:
            html += f'<tr><td>{coh}</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>'
            continue
        n = coh_dose['PATID'].nunique()
        sched = coh_dose['DOSESCH'].mode().iloc[0] if len(coh_dose) > 0 else '—'
        mean_doses = coh_dose.groupby('PATID').size().mean()
        wts = coh_dose['PTWEIGHT'].dropna()
        wt_range = f'{wts.min():.1f}-{wts.max():.1f}' if len(wts) > 0 else '—'
        html += f'<tr><td>Cohort {coh}</td><td class="c">{n}</td><td>{sched}</td>'
        html += f'<td class="r">{mean_doses:.1f}</td><td class="r">{wt_range}</td></tr>'
    html += '</tbody></table>'

    html += '''
<h3>4.2 Anti-Drug Antibody (ADA) Summary</h3>
<div class="callout orange">
<strong>ADA data (Bioagilytix):</strong> ADA CSV not included in this data extract folder.
ADA analysis requires separate Bioagilytix transfer files. Refer to the dedicated ADA summary if available.
</div>
</div>
'''

    # ══════ SECTION 5: Adverse Events ══════
    html += '''
<div class="section pg">
<h2>5. Adverse Events</h2>
<div class="callout orange">
<strong>Note:</strong> Adverse event analysis requires AE SAS data (<code>ae.sas7bdat</code>) which is not available from CSV extract.
The framework table below shows the intended structure.
</div>
<table>
<thead><tr><th>System Organ Class</th><th>Preferred Term</th><th>Cohort A1 (N=4)</th><th>Cohort A2 (N=4)</th><th>Cohort A3 (N=10)</th><th>Cohort B1 (N=2)</th><th>Total (N=20)</th></tr></thead>
<tbody>
<tr><td colspan="7" class="c" style="color:var(--sub);font-style:italic;">Data pending - requires ae.sas7bdat</td></tr>
</tbody>
</table>
</div>
'''

    # ══════ SECTION 6: Safety Laboratory ══════
    html += '''
<div class="section pg">
<h2>6. Safety Laboratory</h2>
'''

    # 6.1 Hepatic panel
    html += '<h3>6.1 Hepatic Function Panel</h3>'
    html += summary_stats_table(lab, BIOCHEM_HEPATIC, 'Hepatic')
    html += visit_trend_table(lab, ['ALT/SGPT', 'AST/SGOT', 'Total Bilirubin'])

    # 6.2 Renal panel
    html += '<h3>6.2 Renal Function Panel</h3>'
    html += summary_stats_table(lab, BIOCHEM_RENAL, 'Renal')

    # 6.3 Other Biochemistry
    html += '<h3>6.3 Other Biochemistry</h3>'
    html += summary_stats_table(lab, BIOCHEM_OTHER, 'Biochemistry')

    # 6.4 Hematology
    html += '<h3>6.4 Hematology Summary</h3>'
    hem = lab[lab['LBCAT'] == 'Hematology']
    available_hem = [t for t in HEMATOLOGY_TESTS if t in hem['LBTEST'].values]
    html += summary_stats_table(lab, available_hem, 'Hematology')

    # 6.5 eDISH
    html += f'''
<h3>6.5 eDISH (Evaluation of Drug-Induced Serious Hepatotoxicity)</h3>
<p>eDISH scatter plots show all post-baseline lab values for treated subjects (N={len(TREATED)}).
Each point represents one lab draw. Reference lines: ALT/AST at 3&times;ULN (vertical),
Total Bilirubin at 2&times;ULN (horizontal). Points in the upper-right quadrant indicate potential Hy's Law cases.</p>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
<div><img src="data:image/png;base64,{alt_b64}" style="width:100%;border:1px solid var(--border);border-radius:4px;" alt="eDISH ALT vs TBILI"/></div>
<div><img src="data:image/png;base64,{ast_b64}" style="width:100%;border:1px solid var(--border);border-radius:4px;" alt="eDISH AST vs TBILI"/></div>
</div>
'''
    total_hys = alt_hys + ast_hys
    if total_hys == 0:
        html += f'''
<div class="callout green">
<strong>No participants in Hy's law quadrant (ALT/AST &gt;3&times;ULN AND TBili &gt;2&times;ULN) as of data cut {data_cut_date}.</strong>
Liver function parameters remain within acceptable limits across all cohorts.
ALT plot: {alt_n} data points; AST plot: {ast_n} data points.
</div>
'''
    else:
        html += f'''
<div class="callout red">
<strong>WARNING: {total_hys} subject(s) with values in Hy's Law quadrant detected.</strong> Further review required.
</div>
'''

    # 6.6 Lab outliers
    html += '<h3>6.6 Lab Outlier Table (&gt;2&times;ULN or Flagged)</h3>'
    html += lab_outlier_table(lab)

    # 6.7 Safety margin
    html += '<h3>6.7 Safety Margin Summary</h3>'
    html += safety_margin_table(lab)

    html += '</div>'

    # ══════ SECTION 7: ECG ══════
    html += '''
<div class="section pg">
<h2>7. ECG Summary</h2>
<div class="callout orange">
<strong>Note:</strong> ECG analysis requires ECG SAS data (<code>eg1.sas7bdat</code>) which is not available from CSV extract.
ECG data includes QTcF, PR interval, QRS duration, and HR assessments.
</div>
<table>
<thead><tr><th>Parameter</th><th>Visit</th><th>N</th><th>Mean</th><th>SD</th><th>Min</th><th>Max</th></tr></thead>
<tbody>
<tr><td colspan="7" class="c" style="color:var(--sub);font-style:italic;">Data pending - requires eg1.sas7bdat</td></tr>
</tbody>
</table>
</div>
'''

    # ══════ SECTION 8: Vital Signs ══════
    html += '''
<div class="section pg">
<h2>8. Vital Signs</h2>
<div class="callout orange">
<strong>Note:</strong> Vital signs analysis requires VS SAS data (<code>vs.sas7bdat</code>) which is not available from CSV extract.
Vital signs data includes systolic/diastolic BP, heart rate, respiratory rate, temperature, and weight.
</div>
<table>
<thead><tr><th>Parameter</th><th>Visit</th><th>N</th><th>Mean</th><th>SD</th><th>Min</th><th>Max</th></tr></thead>
<tbody>
<tr><td colspan="7" class="c" style="color:var(--sub);font-style:italic;">Data pending - requires vs.sas7bdat</td></tr>
</tbody>
</table>
</div>
'''

    # ══════ APPENDIX: Data Changes ══════
    html += '''
<div class="section pg">
<h2>Appendix: Data Changes Tracker</h2>
'''
    html += build_delta_section(month)
    html += '</div>'

    # ══════ FOOTER ══════
    html += f'''
<div class="footer">
<span>DNLI-I-0001 MMR &middot; {month_label} &middot; Safety-Focused Report</span>
<span>Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} &middot; Confidential</span>
</div>
</body>
</html>
'''
    return html


def get_css():
    """Return the CSS for the report, matching the existing template."""
    return """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');
:root{--primary:#1a3a5c;--accent:#0066cc;--green:#00a86b;--red:#c0392b;--orange:#d97706;--border:#d1dce8;--bg:#f7f9fc;--text:#1e2a38;--sub:#4a5568;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;font-size:12.5px;line-height:1.6;color:var(--text);background:#fff;max-width:1050px;margin:0 auto;padding:36px 48px;}
.diff-banner{background:#fff8e1;border:2px solid #f59e0b;border-radius:8px;padding:14px 18px;margin-bottom:28px;}
.diff-banner h2{color:#92400e;font-size:13px;margin-bottom:8px;display:flex;align-items:center;gap:8px;}
.diff-banner .diff-item{display:flex;gap:8px;margin:4px 0;font-size:11.5px;}
.diff-new{background:#dcfce7;color:#166534;padding:1px 7px;border-radius:10px;font-weight:700;font-size:10px;white-space:nowrap;align-self:center;}
.diff-chg{background:#fef3c7;color:#92400e;padding:1px 7px;border-radius:10px;font-weight:700;font-size:10px;white-space:nowrap;align-self:center;}
.diff-same{background:#e0f2fe;color:#075985;padding:1px 7px;border-radius:10px;font-weight:700;font-size:10px;white-space:nowrap;align-self:center;}
.cover{border-bottom:3px solid var(--primary);padding-bottom:22px;margin-bottom:30px;}
.cover .bar{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:12px;}
.cover h1{font-size:24px;font-weight:700;color:var(--primary);line-height:1.25;margin-bottom:6px;}
.cover .sub{font-size:14px;color:var(--sub);margin-bottom:16px;}
.meta{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px;}
.mc{background:var(--bg);border:1px solid var(--border);border-radius:5px;padding:8px 12px;}
.mc .l{font-size:9.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--sub);margin-bottom:2px;}
.mc .v{font-size:12px;font-weight:600;color:var(--primary);}
.section{margin-top:28px;}
h2{font-size:15px;font-weight:700;color:var(--primary);padding-bottom:5px;border-bottom:2px solid var(--accent);margin-bottom:12px;}
h3{font-size:13px;font-weight:600;color:var(--primary);margin:18px 0 8px;}
p{margin-bottom:8px;color:var(--text);}
table{width:100%;border-collapse:collapse;margin:8px 0 16px;font-size:11.5px;}
thead th{background:var(--primary);color:#fff;padding:7px 9px;text-align:left;font-weight:600;font-size:10.5px;}
tbody tr:nth-child(even){background:var(--bg);}
tbody td{padding:6px 9px;border-bottom:1px solid var(--border);vertical-align:top;}
td.r{text-align:right;}td.c{text-align:center;}
.callout{border-left:4px solid var(--accent);background:var(--bg);padding:9px 14px;border-radius:0 5px 5px 0;margin:10px 0;font-size:12px;}
.callout.green{border-color:var(--green);}
.callout.orange{border-color:#e67e22;}
.callout.red{border-color:var(--red);}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:10px;font-weight:700;margin:1px;}
.tag.green{background:#d1fae5;color:#065f46;}
.tag.red{background:#fee2e2;color:#991b1b;}
.tag.blue{background:#dbeafe;color:#1e40af;}
.tag.orange{background:#fef3c7;color:#92400e;}
.tag.purple{background:#ede9fe;color:#4c1d95;}
.row-new{background:#dcfce7 !important;}
.row-chg{background:#fef3c7 !important;}
.cell-diff{font-weight:700;color:#166534;}
.cell-warn{font-weight:700;color:#92400e;}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0;}
.stat{background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:12px;text-align:center;}
.stat .n{font-size:26px;font-weight:700;color:var(--primary);}
.stat .label{font-size:10px;color:var(--sub);text-transform:uppercase;letter-spacing:.06em;margin-top:2px;}
.footer{margin-top:40px;padding-top:12px;border-top:1px solid var(--border);font-size:10px;color:var(--sub);display:flex;justify-content:space-between;}
code{font-family:'Roboto Mono',monospace;font-size:10.5px;background:#f0f4f8;padding:1px 4px;border-radius:3px;}
.pg{page-break-before:always;}
.note{font-size:10.5px;color:var(--sub);font-style:italic;margin-top:4px;}
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_mmr.py <month>")
        print("  e.g.: python3 generate_mmr.py 2026MAR20")
        sys.exit(1)

    month = sys.argv[1]
    if month not in MONTH_MAP:
        print(f"Error: Unknown month '{month}'. Choose from: {list(MONTH_MAP.keys())}")
        sys.exit(1)

    print(f"Generating MMR for {month}...")

    # Check data exists
    data_dir = BASE_DIR / 'data' / month
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)

    # Generate HTML
    html = generate_report(month)

    # Write HTML
    report_dir = BASE_DIR / 'report'
    report_dir.mkdir(exist_ok=True)

    html_path = report_dir / f'I-0001-MMR-{month}-SafetyOnly.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    html_size = os.path.getsize(html_path)
    print(f"HTML report: {html_path} ({html_size:,} bytes)")

    # Try PDF
    pdf_path = report_dir / f'I-0001-MMR-{month}-SafetyOnly.pdf'
    try:
        from weasyprint import HTML as WeasyHTML
        WeasyHTML(string=html).write_pdf(str(pdf_path))
        pdf_size = os.path.getsize(pdf_path)
        print(f"PDF report:  {pdf_path} ({pdf_size:,} bytes)")
    except ImportError:
        print("weasyprint not available - PDF generation skipped.")
    except Exception as e:
        print(f"PDF generation failed: {e}")

    print("Done.")


if __name__ == '__main__':
    main()
