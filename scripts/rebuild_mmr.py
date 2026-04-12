"""
rebuild_mmr.py
==============
Injects all corrected figures (from gen_corrected_figs.py) into the
MMR HTML file, replacing old figures section-by-section.

Prerequisites:
    1. Run gen_corrected_figs.py first → produces /tmp/figs_corrected/*.png
    2. pip install beautifulsoup4 lxml

Input:
    /sessions/.../mnt/MMR/I-0001-Medical-Monitoring-Report-2026FEB25-AI.html

Output:
    Same file, updated in-place with all corrected figures embedded as base64.

Study: DNLI-I-0001 / DNL-126
Data cut: 2026-02-25
"""

import base64, os, json
from bs4 import BeautifulSoup

# ─── Helpers ─────────────────────────────────────────────────────────────────
def load_b64(fpath):
    with open(fpath, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def img_tag(b64, alt, width='100%', caption=None):
    cap = caption or alt
    return (f'<figure style="margin:20px auto;text-align:center;">'
            f'<img src="data:image/png;base64,{b64}" alt="{alt}" '
            f'style="width:{width};max-width:1400px;display:block;margin:auto;">'
            f'<figcaption style="text-align:center;font-size:0.85em;color:#555;'
            f'margin-top:4px;">{cap}</figcaption></figure>')

def replace_first_figure(html, search_text, new_fig_html, search_window=8000):
    """Find first <figure> near search_text and replace it."""
    pos = html.find(search_text)
    if pos == -1:
        return html, False
    fig_start = html.rfind('<figure', max(0, pos - 500), pos + search_window)
    if fig_start == -1:
        fig_start = html.find('<figure', pos)
    if fig_start == -1:
        return html, False
    fig_end = html.find('</figure>', fig_start) + len('</figure>')
    return html[:fig_start] + new_fig_html + html[fig_end:], True

def replace_consecutive_figures(html, search_text, new_figs_html, max_figs=15, gap=800):
    """Find and replace a run of consecutive <figure> blocks near search_text."""
    pos = html.find(search_text)
    if pos == -1:
        return html, False
    fig_start = html.find('<figure', pos)
    if fig_start == -1:
        return html, False
    cur = fig_start
    last_end = fig_start
    for _ in range(max_figs):
        fe = html.find('</figure>', cur)
        if fe == -1:
            break
        fe += len('</figure>')
        last_end = fe
        nxt = html.find('<figure', fe)
        if nxt == -1 or nxt - fe > gap:
            break
        cur = nxt
    return html[:fig_start] + new_figs_html + html[last_end:], True


# ─── Paths ───────────────────────────────────────────────────────────────────
HTML_PATH  = '/sessions/fervent-busy-euler/mnt/MMR/I-0001-Medical-Monitoring-Report-2026FEB25-AI.html'
FIGS_DIR   = '/tmp/figs_corrected'

COHORTS = {
    'Cohort A1': ['0016-9001', '0016-9003', '0017-9001', '0017-9002'],
    'Cohort A2': ['0016-9004', '0017-9003', '2064-9002', '2065-9002'],
    'Cohort A3': ['0016-9005', '0016-9006', '0017-9005', '0017-9007',
                  '0017-9008', '2064-9003', '2064-9004', '2064-9005',
                  '2065-9001', '2065-9004'],
    'Cohort B1': ['0017-9004', '0017-9006'],
}

VS_PARAMS_FULL = {
    'DIABP': 'Diastolic Blood Pressure (mmHg)',
    'SYSBP': 'Systolic Blood Pressure (mmHg)',
    'PULSE': 'Pulse (beats/min)',
    'RESP':  'Respiratory Rate (breaths/min)',
    'TEMP':  'Temperature (°C)',
    'POX':   'Pulse Oximetry (SpO₂ %)',
}

VS_SEARCH = {
    'DIABP': ['Diastolic', 'DIABP', 'Figure 8.1'],
    'SYSBP': ['Systolic',  'SYSBP', 'Figure 8.2'],
    'PULSE': ['Pulse (beats', 'PULSE', 'Figure 8.3'],
    'RESP':  ['Respiratory', 'Figure 8.4'],
    'TEMP':  ['Temperature', 'TEMP',  'Figure 8.5'],
    'POX':   ['Pulse Ox', 'POX',     'Figure 8.6'],
}

ECG_SEARCH = {
    'HR':     ['Heart Rate', 'HR (beats', 'Figure 7.1'],
    'PRAG':   ['PRAG', 'PR Interval',     'Figure 7.2'],
    'QRSAG':  ['QRS', 'QRSAG',           'Figure 7.3'],
    'QTAG':   ['QTAG', 'QT Interval',    'Figure 7.4'],
    'QTCFAG': ['QTcF', 'QTCFAG',         'Figure 7.5'],
}

LAB_PARAMS_NAMES = [
    'ALT/SGPT', 'AST/SGOT', 'Blood Urea Nitrogen', 'Calcium', 'Chloride',
    'Creatine kinase', 'Creatinine', 'Glucose', 'Potassium', 'Sodium',
    'Total Bilirubin', 'Total Protein',
    'Basophils; Absolute Units', 'Eosinophils; Absolute Units', 'Erythrocytes',
    'Hemoglobin', 'Hematocrit', 'Leukocytes', 'Lymphocytes; Absolute Units',
    'Monocytes; Absolute Units', 'Neutrophils; Absolute Units', 'Platelets',
    'Reticulocyte count; Absolute',
    'C3c-Complement', 'C4 levels', 'CH50', 'CIC: C1q Binding',
    'CIC: C3 Fragments', 'Interleukin 6', 'Total IgE', 'Tryptase',
    'Urine albumin', 'Urine creatinine', 'Urine Albumin/Creatinine Ratio',
]

LAB_SEARCH = {
    'ALT/SGPT':   ['Figure 6.1', 'ALT/SGPT',   'ALT (U/L)'],
    'AST/SGOT':   ['Figure 6.2', 'AST/SGOT',   'AST (U/L)'],
    'Hemoglobin': ['Figure 6.3', 'Hemoglobin'],
    'Creatinine': ['Figure 6.4', 'Creatinine'],
    'Leukocytes': ['Figure 6.5', 'Leukocytes', 'WBC'],
    'Platelets':  ['Figure 6.6', 'Platelets',  'PLT'],
}

COMPLIANCE_SUBJECT_PAIRS = [
    ('0016-9001 / 0016-9003', 'Cohort A1'),
    ('0017-9001 / 0017-9002', 'Cohort A1'),
    ('0016-9004 / 0017-9003', 'Cohort A2'),
    ('2064-9002 / 2065-9002', 'Cohort A2'),
    ('0016-9005 / 0016-9006', 'Cohort A3'),
    ('0017-9005 / 0017-9007', 'Cohort A3'),
    ('0017-9008 / 2064-9003', 'Cohort A3'),
    ('2064-9004 / 2064-9005', 'Cohort A3'),
    ('2065-9001 / 2065-9004', 'Cohort A3'),
    ('0017-9004 / 0017-9006', 'Cohort B1'),
]


def param_to_file(pname):
    safe = pname.replace('/', '_').replace(' ', '_').replace(';', '').replace(':', '')
    return os.path.join(FIGS_DIR, f'lab_{safe}.png')


# ─── Main injection routine ───────────────────────────────────────────────────
def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    print(f"Loaded HTML: {len(html):,} bytes")

    # ── 1. Section 4.1 Exposure ──────────────────────────────────────────────
    print("Injecting Section 4.1 Exposure…")
    exp_b64 = load_b64(os.path.join(FIGS_DIR, 'fig_4_1_exposure.png'))
    new_exp = img_tag(exp_b64,
        'Figure 4.1 — Study Drug Exposure by Cohort',
        caption=('Figure 4.1 — Study Drug Exposure by Cohort (Completion of Scheduled Dosing). '
                 'X=visit week, Y=participant, color=dose level (3/6/10 mg/kg, Skipped, Discontinued). '
                 'Cohorts stacked vertically. Data cut: 2026-02-25.'))
    for s in ['Study Drug Exposure by Cohort', 'Figure 4.1', 'Exposure by Cohort (Cumulative']:
        html, ok = replace_first_figure(html, s, new_exp)
        if ok:
            print(f"  ✓ via '{s}'"); break

    # ── 2. Section 4.2 Dose Compliance ──────────────────────────────────────
    print("Injecting Section 4.2 Compliance (10 pair plots)…")
    comp_pngs = sorted([f for f in os.listdir(FIGS_DIR)
                        if f.startswith('fig_4_2') and f.endswith('.png')])
    comp_html = ''
    for fname, (subjs, cohort) in zip(comp_pngs, COMPLIANCE_SUBJECT_PAIRS):
        b64 = load_b64(os.path.join(FIGS_DIR, fname))
        alt = (f'Figure 4.2 — Dose Compliance: {subjs} ({cohort}). '
               f'Dots = COMPCAT (<50% red, 50-75% blue, 75-90% cyan, 90-100% green). '
               f'Triangle = Drug interrupted. Yellow lines = IRR by severity.')
        comp_html += img_tag(b64, alt, caption=alt)
    for s in ['Derived Weekly Dose Compliance', 'Figure 4.2',
              'Individual Participant Profiles: Drug Exposure', 'sec4-2-compliance']:
        html, ok = replace_consecutive_figures(html, s, comp_html)
        if ok:
            print(f"  ✓ via '{s}'"); break

    # ── 3. Lab figures ───────────────────────────────────────────────────────
    print("Injecting Lab figures…")
    replaced = 0
    for pname in LAB_PARAMS_NAMES:
        fpath = param_to_file(pname)
        if not os.path.exists(fpath):
            continue
        b64 = load_b64(fpath)
        alt = (f'{pname} — Trend Plot. All subjects; color=Participant ID; '
               f'linetype=Cohort; shape=IND (▲HIGH/●NORMAL/▼LOW).')
        new_fig = img_tag(b64, alt, caption=alt)
        searches = LAB_SEARCH.get(pname, [pname])
        for s in searches:
            html, ok = replace_first_figure(html, s, new_fig)
            if ok:
                replaced += 1; break
    print(f"  ✓ Lab replaced: {replaced}")

    # eDISH
    edish_b64 = load_b64(os.path.join(FIGS_DIR, 'lab_eDISH.png'))
    edish_fig = img_tag(edish_b64,
        'eDISH — Hy\'s Law Evaluation',
        caption=("eDISH Plot: ALT×ULN vs TBILI×ULN and AST×ULN vs TBILI×ULN. "
                 "Log-log scale. Hy's Law quadrants annotated."))
    for s in ["eDISH", "Hy's Law", "Drug-Induced Serious Hepatotoxicity"]:
        html, ok = replace_first_figure(html, s, edish_fig)
        if ok:
            print("  ✓ eDISH injected"); break

    # ── 4. ECG figures ───────────────────────────────────────────────────────
    print("Injecting ECG figures…")
    ecg_count = 0
    for pname, searches in ECG_SEARCH.items():
        fpath = os.path.join(FIGS_DIR, f'ecg_{pname}.png')
        if not os.path.exists(fpath):
            continue
        b64 = load_b64(fpath)
        alt = (f'ECG {pname} — Trend Plot. All subjects; color=Participant ID; '
               f'linetype=Cohort; shape=IND. Pre/post-dose timepoints shown.')
        new_fig = img_tag(b64, alt, caption=alt)
        for s in searches:
            html, ok = replace_first_figure(html, s, new_fig)
            if ok:
                ecg_count += 1; break
    print(f"  ✓ ECG replaced: {ecg_count}")

    # ── 5. Vital Signs ───────────────────────────────────────────────────────
    print("Injecting Vital Signs figures…")
    vs_count = 0
    for pname, full_name in VS_PARAMS_FULL.items():
        cohort_block = (f'<h4 style="color:#2E75B6;margin-top:20px;">{full_name}</h4>'
                        f'<p style="font-size:0.85em;color:#555;font-style:italic;">'
                        f'Data points represent the final assessment conducted before dosing. '
                        f'Pre-dose assessments only. Reference ranges age-normalized.</p>')
        for cohort_name in COHORTS:
            safe_c = cohort_name.replace(' ', '_')
            fpath  = os.path.join(FIGS_DIR, f'vs_{pname}_{safe_c}.png')
            if not os.path.exists(fpath):
                continue
            b64 = load_b64(fpath)
            alt = (f'{full_name} — {cohort_name}. Pre-dose only; '
                   f'color=Participant ID; shape=IND; '
                   f'faceted by visit group (BL–Wk49, Wk50–97, Wk98+).')
            cohort_block += (f'<h5 style="color:#444;margin:10px 0 4px 0;">'
                             f'{cohort_name}</h5>')
            cohort_block += img_tag(b64, alt, caption=alt)
        for s in VS_SEARCH.get(pname, [pname]):
            html, ok = replace_consecutive_figures(html, s, cohort_block, max_figs=8)
            if ok:
                vs_count += 1; break
    print(f"  ✓ VS sections replaced: {vs_count}")

    # ── Write output ─────────────────────────────────────────────────────────
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    size = os.path.getsize(HTML_PATH)
    print(f"\n✅ MMR HTML updated: {HTML_PATH}")
    print(f"   Size: {size:,} bytes ({size/1024/1024:.1f} MB)")


if __name__ == '__main__':
    main()
