#!/usr/bin/env python3
"""
Monthly Delta Analysis for DNLI-I-0001 (DNL-126, MPS IIIA)
Generates month-over-month comparison HTML report from 3 monthly data cuts.
"""

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
REPORT_DIR = BASE / "report"

MONTHS = [
    {"label": "JAN30", "dir": "2026JAN30", "lab": "mlm_dnli-i-0001_safety.csv", "prod": "DNLI-I-0001_PROD_01JAN2026.csv"},
    {"label": "FEB24", "dir": "2026FEB24", "lab": "mlm_dnli-i-0001_safety.csv", "prod": "DNLI-I-0001_PROD_01FEB2026.csv"},
    {"label": "MAR20", "dir": "2026MAR20", "lab": "mlm_dnli-i-0001_safety.csv", "prod": "DNLI-I-0001_PROD_01MAR2026.csv"},
]

COHORTS = {
    "Cohort A1": ["0016-9001", "0016-9003", "0017-9001", "0017-9002"],
    "Cohort A2": ["0016-9004", "0017-9003", "2064-9002", "2065-9002"],
    "Cohort A3": ["0016-9005", "0016-9006", "0017-9005", "0017-9007", "0017-9008",
                  "2064-9003", "2064-9004", "2064-9005", "2065-9001", "2065-9004"],
    "Cohort B1": ["0017-9004", "0017-9006"],
}

# ULN values for hepatic/renal monitoring (adult reference; pediatric context noted)
ULN = {"ALT": 41, "AST": 40, "TBILI": 1.2, "CREAT": 1.2}
# Thresholds for flagging
THRESHOLDS = {"ALT": 3, "AST": 3, "TBILI": 1.5, "CREAT": 1.5}

# ── Data Loading ───────────────────────────────────────────────────────────────
def load_data():
    lab_dfs = {}
    prod_dfs = {}
    for m in MONTHS:
        lab_path = DATA_DIR / m["dir"] / m["lab"]
        prod_path = DATA_DIR / m["dir"] / m["prod"]
        lab_dfs[m["label"]] = pd.read_csv(lab_path)
        prod_dfs[m["label"]] = pd.read_csv(prod_path)
    return lab_dfs, prod_dfs


def parse_numeric(val):
    """Parse lab value, stripping < or > prefixes."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    s = re.sub(r'^[<>]\s*', '', s)
    try:
        return float(s)
    except ValueError:
        return np.nan


# ── Analysis Functions ─────────────────────────────────────────────────────────
def data_volume_delta(lab_dfs, prod_dfs):
    rows = []
    for m in MONTHS:
        lbl = m["label"]
        rows.append({
            "Month": lbl,
            "Lab Records": len(lab_dfs[lbl]),
            "IRT/PROD Records": len(prod_dfs[lbl]),
        })
    df = pd.DataFrame(rows)
    # Add delta columns
    for col in ["Lab Records", "IRT/PROD Records"]:
        deltas = ["--"]
        for i in range(1, len(df)):
            diff = df.iloc[i][col] - df.iloc[i - 1][col]
            pct = (diff / df.iloc[i - 1][col] * 100) if df.iloc[i - 1][col] > 0 else 0
            deltas.append(f"+{diff} ({pct:+.1f}%)" if diff >= 0 else f"{diff} ({pct:+.1f}%)")
        df[f"{col} Delta"] = deltas
    return df


def lab_safety_metrics(lab_dfs):
    """Per-month lab safety summary."""
    rows = []
    for m in MONTHS:
        lbl = m["label"]
        df = lab_dfs[lbl]
        rows.append({
            "Month": lbl,
            "Unique Subjects": df["SUBJID"].nunique(),
            "Unique Lab Tests": df["LBTESTCD"].nunique(),
            "Total Lab Records": len(df),
        })
    return pd.DataFrame(rows)


def hepatic_analysis(lab_dfs):
    """Compute xULN for key hepatic/renal parameters per month."""
    params = ["ALT", "AST", "TBILI", "CREAT"]
    all_rows = []

    for m in MONTHS:
        lbl = m["label"]
        df = lab_dfs[lbl].copy()
        for param in params:
            subset = df[df["LBTESTCD"] == param].copy()
            subset["NUMVAL"] = subset["LBORRES"].apply(parse_numeric)
            subset = subset.dropna(subset=["NUMVAL"])

            uln = ULN[param]
            threshold = THRESHOLDS[param]

            if len(subset) > 0:
                max_val = subset["NUMVAL"].max()
                max_xuln = max_val / uln
                # Find subject with max
                max_row = subset.loc[subset["NUMVAL"].idxmax()]
                max_subj = max_row["SUBJID"]

                # Count subjects exceeding threshold x ULN
                subset["xULN"] = subset["NUMVAL"] / uln
                exceeding = subset[subset["xULN"] > threshold]["SUBJID"].nunique()

                # Use lab-specific ULN from data (LBORNRHI) where available
                lab_uln_vals = subset["LBORNRHI"].apply(parse_numeric).dropna()
                lab_uln = lab_uln_vals.median() if len(lab_uln_vals) > 0 else uln

                all_rows.append({
                    "Month": lbl,
                    "Parameter": param,
                    "N Records": len(subset),
                    "N Subjects": subset["SUBJID"].nunique(),
                    "Max Value": f"{max_val:.1f}",
                    "Max xULN": f"{max_xuln:.2f}",
                    "Max Subject": max_subj,
                    "Lab ULN (median)": f"{lab_uln:.1f}",
                    f"Subj > {threshold}xULN": exceeding,
                })
            else:
                all_rows.append({
                    "Month": lbl,
                    "Parameter": param,
                    "N Records": 0,
                    "N Subjects": 0,
                    "Max Value": "--",
                    "Max xULN": "--",
                    "Max Subject": "--",
                    "Lab ULN (median)": "--",
                    f"Subj > {threshold}xULN": 0,
                })

    return pd.DataFrame(all_rows)


def dosing_analysis(prod_dfs):
    """Analyze dosing per month."""
    all_rows = []
    for m in MONTHS:
        lbl = m["label"]
        df = prod_dfs[lbl].copy()

        # Count doses: each KITID entry (pipe-separated) is a dose
        total_doses = 0
        dose_level_counts = {}
        for _, row in df.iterrows():
            kit = str(row.get("KITID", ""))
            titrlvl = str(row.get("TITRLVL", ""))
            if kit and kit != "nan" and kit.strip():
                kits = [k.strip() for k in kit.split("|") if k.strip()]
                levels = [l.strip() for l in titrlvl.split("|") if l.strip()] if titrlvl and titrlvl != "nan" else []
                total_doses += len(kits)
                for i, k in enumerate(kits):
                    lvl = levels[i] if i < len(levels) else "Unknown"
                    dose_level_counts[lvl] = dose_level_counts.get(lvl, 0) + 1

        # Enrolled subjects
        enrolled = df[df["SUBSTA"].str.contains("Enrolled", case=False, na=False)]["PATID"].nunique()

        # Dose interruptions: look for rows with DOSESCH containing something
        dosesch_rows = df[df["DOSESCH"].notna() & (df["DOSESCH"] != "")]
        n_schedule_changes = len(dosesch_rows)

        # Subjects by dose level (latest dose for each subject)
        subj_dose = {}
        for _, row in df.iterrows():
            patid = row.get("PATID", "")
            titrlvl = str(row.get("TITRLVL", ""))
            if titrlvl and titrlvl != "nan" and titrlvl.strip():
                levels = [l.strip() for l in titrlvl.split("|") if l.strip()]
                if levels:
                    subj_dose[patid] = levels[-1]  # latest dose level

        dose_subj_summary = {}
        for subj, lvl in subj_dose.items():
            dose_subj_summary[lvl] = dose_subj_summary.get(lvl, 0) + 1

        all_rows.append({
            "Month": lbl,
            "Total Doses": total_doses,
            "Enrolled Subjects": enrolled,
            "Dose Schedule Changes": n_schedule_changes,
            "Dose Level Distribution": dose_subj_summary,
        })

    return all_rows


def new_lab_records(lab_dfs):
    """Records in month N but not in month N-1 (by LBREFID as accession number proxy)."""
    month_labels = [m["label"] for m in MONTHS]
    results = {}
    for i in range(1, len(month_labels)):
        prev_lbl = month_labels[i - 1]
        curr_lbl = month_labels[i]
        prev_refs = set(lab_dfs[prev_lbl]["LBREFID"].astype(str).unique())
        curr_refs = set(lab_dfs[curr_lbl]["LBREFID"].astype(str).unique())
        new_refs = curr_refs - prev_refs

        new_df = lab_dfs[curr_lbl][lab_dfs[curr_lbl]["LBREFID"].astype(str).isin(new_refs)]
        summary = new_df.groupby(["SUBJID", "VISIT"]).agg(
            Records=("LBTESTCD", "count"),
            Tests=("LBTESTCD", lambda x: ", ".join(sorted(x.dropna().astype(str).unique())[:5])),
            Date=("LBDT", "first"),
        ).reset_index()

        results[f"{prev_lbl} -> {curr_lbl}"] = {
            "new_accessions": len(new_refs),
            "new_records": len(new_df),
            "summary": summary,
        }
    return results


def summary_delta_table(lab_dfs, prod_dfs, dosing_data):
    """Key metrics side-by-side."""
    rows = []
    for i, m in enumerate(MONTHS):
        lbl = m["label"]
        lab = lab_dfs[lbl]
        prod = prod_dfs[lbl]
        d = dosing_data[i]
        rows.append({
            "Metric": "Lab Records",
            lbl: len(lab),
        })
    # Build pivot
    metrics = [
        "Lab Records", "IRT Records", "Unique Lab Subjects",
        "Unique Lab Tests", "Enrolled Subjects", "Total Doses Administered",
    ]
    table = []
    for metric in metrics:
        row = {"Metric": metric}
        for i, m in enumerate(MONTHS):
            lbl = m["label"]
            lab = lab_dfs[lbl]
            prod = prod_dfs[lbl]
            d = dosing_data[i]
            if metric == "Lab Records":
                row[lbl] = len(lab)
            elif metric == "IRT Records":
                row[lbl] = len(prod)
            elif metric == "Unique Lab Subjects":
                row[lbl] = lab["SUBJID"].nunique()
            elif metric == "Unique Lab Tests":
                row[lbl] = lab["LBTESTCD"].nunique()
            elif metric == "Enrolled Subjects":
                row[lbl] = d["Enrolled Subjects"]
            elif metric == "Total Doses Administered":
                row[lbl] = d["Total Doses"]
        table.append(row)
    return pd.DataFrame(table)


def data_changes_tracker(lab_dfs, prod_dfs):
    """Track what explicitly changed between cuts."""
    changes = []
    month_labels = [m["label"] for m in MONTHS]

    for i in range(1, len(month_labels)):
        prev = month_labels[i - 1]
        curr = month_labels[i]

        lab_prev = lab_dfs[prev]
        lab_curr = lab_dfs[curr]
        prod_prev = prod_dfs[prev]
        prod_curr = prod_dfs[curr]

        change = {"period": f"{prev} to {curr}", "items": []}

        # New lab records
        lab_diff = len(lab_curr) - len(lab_prev)
        change["items"].append(f"Lab records: {len(lab_prev)} -> {len(lab_curr)} ({'+' if lab_diff >= 0 else ''}{lab_diff})")

        # New IRT records
        prod_diff = len(prod_curr) - len(prod_prev)
        change["items"].append(f"IRT/PROD records: {len(prod_prev)} -> {len(prod_curr)} ({'+' if prod_diff >= 0 else ''}{prod_diff})")

        # New subjects in lab
        prev_subj = set(lab_prev["SUBJID"].unique())
        curr_subj = set(lab_curr["SUBJID"].unique())
        new_subj = curr_subj - prev_subj
        if new_subj:
            change["items"].append(f"New lab subjects: {', '.join(sorted(new_subj))}")
        else:
            change["items"].append("No new lab subjects")

        # New subjects in IRT
        prev_pat = set(prod_prev["PATID"].unique())
        curr_pat = set(prod_curr["PATID"].unique())
        new_pat = curr_pat - prev_pat
        if new_pat:
            change["items"].append(f"New IRT subjects: {', '.join(sorted(new_pat))}")
        else:
            change["items"].append("No new IRT subjects")

        # New accession numbers (lab panels)
        prev_refs = set(lab_prev["LBREFID"].astype(str).unique())
        curr_refs = set(lab_curr["LBREFID"].astype(str).unique())
        new_refs = curr_refs - prev_refs
        change["items"].append(f"New accession numbers: {len(new_refs)}")

        # New visits in IRT
        prev_vis = set(prod_prev[["PATID", "VISNAM"]].apply(tuple, axis=1))
        curr_vis = set(prod_curr[["PATID", "VISNAM"]].apply(tuple, axis=1))
        new_vis = curr_vis - prev_vis
        change["items"].append(f"New IRT visit records: {len(new_vis)}")

        changes.append(change)

    return changes


# ── HTML Generation ────────────────────────────────────────────────────────────
def generate_html(vol_delta, lab_metrics, hepatic, dosing_data, new_recs, summary, changes):
    """Generate professional clinical-style HTML report."""

    def df_to_table(df, highlight_cols=None):
        """Convert DataFrame to HTML table string."""
        html = '<table><thead><tr>'
        for col in df.columns:
            html += f'<th>{col}</th>'
        html += '</tr></thead><tbody>'
        for _, row in df.iterrows():
            html += '<tr>'
            for col in df.columns:
                val = row[col]
                cls = ''
                if highlight_cols and col in highlight_cols:
                    s = str(val)
                    if '+' in s and 'Delta' in col:
                        cls = ' class="cell-diff"'
                    elif '-' in s and 'Delta' in col:
                        cls = ' class="cell-warn"'
                html += f'<td{cls}>{val}</td>'
            html += '</tr>'
        html += '</tbody></table>'
        return html

    # Hepatic pivot: one table per parameter
    hepatic_html = ""
    for param in ["ALT", "AST", "TBILI", "CREAT"]:
        sub = hepatic[hepatic["Parameter"] == param]
        param_name = {"ALT": "ALT / SGPT", "AST": "AST / SGOT", "TBILI": "Total Bilirubin", "CREAT": "Creatinine"}[param]
        threshold = THRESHOLDS[param]
        uln_val = ULN[param]
        unit = {"ALT": "U/L", "AST": "U/L", "TBILI": "mg/dL", "CREAT": "mg/dL"}[param]

        hepatic_html += f'<h3>{param_name} (ULN = {uln_val} {unit})</h3>'
        hepatic_html += '<table><thead><tr>'
        hepatic_html += '<th>Month</th><th>N Records</th><th>N Subjects</th>'
        hepatic_html += '<th>Max Value</th><th>Max xULN</th><th>Max Subject</th>'
        hepatic_html += f'<th>Lab ULN (median)</th><th>Subj &gt; {threshold}xULN</th>'
        hepatic_html += '</tr></thead><tbody>'
        for _, row in sub.iterrows():
            xuln_str = str(row["Max xULN"])
            try:
                xuln_val = float(xuln_str)
                xuln_cls = ' class="cell-warn"' if xuln_val > threshold else ''
            except ValueError:
                xuln_cls = ''
            exceed_col_name = f"Subj > {threshold}xULN"
            exceed_val = row.get(exceed_col_name, 0)
            exceed_cls = ' class="cell-warn"' if exceed_val > 0 else ''
            hepatic_html += f'<tr>'
            hepatic_html += f'<td>{row["Month"]}</td>'
            hepatic_html += f'<td class="r">{row["N Records"]}</td>'
            hepatic_html += f'<td class="r">{row["N Subjects"]}</td>'
            hepatic_html += f'<td class="r">{row["Max Value"]}</td>'
            hepatic_html += f'<td class="r"{xuln_cls}>{row["Max xULN"]}</td>'
            hepatic_html += f'<td>{row["Max Subject"]}</td>'
            hepatic_html += f'<td class="r">{row["Lab ULN (median)"]}</td>'
            hepatic_html += f'<td class="c"{exceed_cls}>{exceed_val}</td>'
            hepatic_html += '</tr>'
        hepatic_html += '</tbody></table>'

    # Dosing tables
    dosing_html = ""
    dosing_summary_rows = []
    for d in dosing_data:
        dosing_summary_rows.append({
            "Month": d["Month"],
            "Enrolled Subjects": d["Enrolled Subjects"],
            "Total Doses": d["Total Doses"],
            "Dose Schedule Changes": d["Dose Schedule Changes"],
        })
    dosing_summary_df = pd.DataFrame(dosing_summary_rows)
    dosing_html += df_to_table(dosing_summary_df)

    # Dose level distribution
    all_levels = set()
    for d in dosing_data:
        all_levels.update(d["Dose Level Distribution"].keys())
    all_levels = sorted(all_levels)

    if all_levels:
        dosing_html += '<h3>Subjects by Current Dose Level</h3>'
        dosing_html += '<table><thead><tr><th>Month</th>'
        for lvl in all_levels:
            dosing_html += f'<th>{lvl}</th>'
        dosing_html += '</tr></thead><tbody>'
        for d in dosing_data:
            dosing_html += f'<tr><td>{d["Month"]}</td>'
            for lvl in all_levels:
                dosing_html += f'<td class="c">{d["Dose Level Distribution"].get(lvl, 0)}</td>'
            dosing_html += '</tr>'
        dosing_html += '</tbody></table>'

    # New records section
    new_recs_html = ""
    for period, info in new_recs.items():
        new_recs_html += f'<h3>{period}</h3>'
        new_recs_html += f'<div class="callout green"><strong>{info["new_accessions"]}</strong> new accession numbers | '
        new_recs_html += f'<strong>{info["new_records"]}</strong> new lab records</div>'
        if len(info["summary"]) > 0:
            summary_df = info["summary"].head(30)  # limit display
            new_recs_html += '<table><thead><tr><th>Subject</th><th>Visit</th><th>Date</th><th>Records</th><th>Tests (sample)</th></tr></thead><tbody>'
            for _, row in summary_df.iterrows():
                new_recs_html += f'<tr><td>{row["SUBJID"]}</td><td>{row["VISIT"]}</td>'
                new_recs_html += f'<td>{row["Date"]}</td><td class="r">{row["Records"]}</td>'
                new_recs_html += f'<td>{row["Tests"]}</td></tr>'
            new_recs_html += '</tbody></table>'
        else:
            new_recs_html += '<p class="note">No new records in this period.</p>'

    # Changes tracker
    changes_html = ""
    for ch in changes:
        changes_html += f'<div class="diff-banner"><h2>Delta: {ch["period"]}</h2>'
        for item in ch["items"]:
            # Determine badge type
            if "New" in item and ("subjects:" in item.lower()) and "No new" not in item:
                badge = '<span class="diff-new">NEW</span>'
            elif "+" in item:
                badge = '<span class="diff-chg">CHANGED</span>'
            elif "No new" in item or "0" in item.split(":")[-1].strip():
                badge = '<span class="diff-same">SAME</span>'
            else:
                badge = '<span class="diff-chg">CHANGED</span>'
            changes_html += f'<div class="diff-item">{badge} {item}</div>'
        changes_html += '</div>'

    # Summary delta table
    summary_html = df_to_table(summary)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>DNLI-I-0001 Monthly Delta Report</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');
:root{{--primary:#1a3a5c;--accent:#0066cc;--green:#00a86b;--red:#c0392b;--orange:#d97706;--border:#d1dce8;--bg:#f7f9fc;--text:#1e2a38;--sub:#4a5568;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;font-size:12.5px;line-height:1.6;color:var(--text);background:#fff;max-width:1100px;margin:0 auto;padding:36px 48px;}}
.diff-banner{{background:#fff8e1;border:2px solid #f59e0b;border-radius:8px;padding:14px 18px;margin-bottom:20px;}}
.diff-banner h2{{color:#92400e;font-size:13px;margin-bottom:8px;display:flex;align-items:center;gap:8px;}}
.diff-banner .diff-item{{display:flex;gap:8px;margin:4px 0;font-size:11.5px;}}
.diff-new{{background:#dcfce7;color:#166534;padding:1px 7px;border-radius:10px;font-weight:700;font-size:10px;white-space:nowrap;align-self:center;}}
.diff-chg{{background:#fef3c7;color:#92400e;padding:1px 7px;border-radius:10px;font-weight:700;font-size:10px;white-space:nowrap;align-self:center;}}
.diff-same{{background:#e0f2fe;color:#075985;padding:1px 7px;border-radius:10px;font-weight:700;font-size:10px;white-space:nowrap;align-self:center;}}
.cover{{border-bottom:3px solid var(--primary);padding-bottom:22px;margin-bottom:30px;}}
.cover .bar{{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:12px;}}
.cover h1{{font-size:24px;font-weight:700;color:var(--primary);line-height:1.25;margin-bottom:6px;}}
.cover .sub{{font-size:14px;color:var(--sub);margin-bottom:16px;}}
.meta{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px;}}
.mc{{background:var(--bg);border:1px solid var(--border);border-radius:5px;padding:8px 12px;}}
.mc .l{{font-size:9.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--sub);margin-bottom:2px;}}
.mc .v{{font-size:12px;font-weight:600;color:var(--primary);}}
.section{{margin-top:28px;}}
h2{{font-size:15px;font-weight:700;color:var(--primary);padding-bottom:5px;border-bottom:2px solid var(--accent);margin-bottom:12px;}}
h3{{font-size:13px;font-weight:600;color:var(--primary);margin:18px 0 8px;}}
p{{margin-bottom:8px;color:var(--text);}}
table{{width:100%;border-collapse:collapse;margin:8px 0 16px;font-size:11.5px;}}
thead th{{background:var(--primary);color:#fff;padding:7px 9px;text-align:left;font-weight:600;font-size:10.5px;}}
tbody tr:nth-child(even){{background:var(--bg);}}
tbody td{{padding:6px 9px;border-bottom:1px solid var(--border);vertical-align:top;}}
td.r{{text-align:right;}}td.c{{text-align:center;}}
.callout{{border-left:4px solid var(--accent);background:var(--bg);padding:9px 14px;border-radius:0 5px 5px 0;margin:10px 0;font-size:12px;}}
.callout.green{{border-color:var(--green);}}
.callout.orange{{border-color:#e67e22;}}
.callout.red{{border-color:var(--red);}}
.tag{{display:inline-block;padding:1px 7px;border-radius:10px;font-size:10px;font-weight:700;margin:1px;}}
.tag.green{{background:#d1fae5;color:#065f46;}}
.tag.red{{background:#fee2e2;color:#991b1b;}}
.tag.blue{{background:#dbeafe;color:#1e40af;}}
.tag.orange{{background:#fef3c7;color:#92400e;}}
.cell-diff{{font-weight:700;color:#166534;}}
.cell-warn{{font-weight:700;color:#92400e;}}
.stat-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0;}}
.stat{{background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:12px;text-align:center;}}
.stat .n{{font-size:26px;font-weight:700;color:var(--primary);}}
.stat .label{{font-size:10px;color:var(--sub);text-transform:uppercase;letter-spacing:.06em;margin-top:2px;}}
.footer{{margin-top:40px;padding-top:12px;border-top:1px solid var(--border);font-size:10px;color:var(--sub);display:flex;justify-content:space-between;}}
code{{font-family:'Roboto Mono',monospace;font-size:10.5px;background:#f0f4f8;padding:1px 4px;border-radius:3px;}}
.pg{{page-break-before:always;}}
.note{{font-size:10.5px;color:var(--sub);font-style:italic;margin-top:4px;}}
.toc{{background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:14px 20px;margin:16px 0;}}
.toc a{{color:var(--accent);text-decoration:none;font-size:12px;display:block;padding:3px 0;}}
.toc a:hover{{text-decoration:underline;}}
</style>
</head>
<body>

<!-- COVER -->
<div class="cover">
<div class="bar">Denali Therapeutics &middot; Confidential &middot; Monthly Delta Analysis</div>
<h1>DNLI-I-0001 Monthly Data Delta Report</h1>
<div class="sub">DNL126 (ETV:SGSH-BioM) &middot; MPS IIIA (Sanfilippo Syndrome Type A) &middot; 3-Month Comparison</div>
<div class="meta">
<div class="mc"><div class="l">Data Cut 1</div><div class="v">2026-JAN-30</div></div>
<div class="mc"><div class="l">Data Cut 2</div><div class="v">2026-FEB-24</div></div>
<div class="mc"><div class="l">Data Cut 3</div><div class="v">2026-MAR-20</div></div>
<div class="mc"><div class="l">Study Population</div><div class="v">N=20 (4 Cohorts)</div></div>
<div class="mc"><div class="l">Report Generated</div><div class="v">{now}</div></div>
<div class="mc"><div class="l">Sources</div><div class="v">MLM Labs, 4G Clinical IRT</div></div>
</div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc">
<strong>Contents</strong>
<a href="#sec-changes">1. Data Changes Tracker</a>
<a href="#sec-volume">2. Data Volume Delta</a>
<a href="#sec-lab">3. Lab Safety Metrics per Month</a>
<a href="#sec-hepatic">4. Hepatic / Renal Safety (eDISH Parameters)</a>
<a href="#sec-dosing">5. Dosing / Compliance Delta</a>
<a href="#sec-new">6. New Lab Records</a>
<a href="#sec-summary">7. Summary Delta Table</a>
</div>

<!-- SECTION 1: DATA CHANGES TRACKER -->
<div class="section" id="sec-changes">
<h2>1. Data Changes Tracker</h2>
<p>Explicit listing of what changed between each monthly data cut.</p>
{changes_html}
</div>

<!-- SECTION 2: DATA VOLUME DELTA -->
<div class="section" id="sec-volume">
<h2>2. Data Volume Delta</h2>
<p>Row counts per month per data source, showing cumulative growth across the 3 data cuts.</p>
{df_to_table(vol_delta, highlight_cols=["Lab Records Delta", "IRT/PROD Records Delta"])}
</div>

<!-- SECTION 3: LAB SAFETY METRICS -->
<div class="section" id="sec-lab">
<h2>3. Lab Safety Metrics per Month</h2>
{df_to_table(lab_metrics)}
</div>

<!-- SECTION 4: HEPATIC SAFETY -->
<div class="section pg" id="sec-hepatic">
<h2>4. Hepatic / Renal Safety Parameters (eDISH)</h2>
<div class="callout orange">
<strong>Note — Pediatric Population:</strong> ULN values shown are adult reference ranges
(ALT=41 U/L, AST=40 U/L, TBILI=1.2 mg/dL, Creat=1.2 mg/dL). Lab-reported ULN (median from
data) is also shown. These patients are pediatric (ages 2–7); age-appropriate reference ranges
from the central lab are used for normal range flagging in the source data (LBNRIND column).
</div>
{hepatic_html}
</div>

<!-- SECTION 5: DOSING DELTA -->
<div class="section pg" id="sec-dosing">
<h2>5. Dosing / Compliance Delta</h2>
{dosing_html}
</div>

<!-- SECTION 6: NEW LAB RECORDS -->
<div class="section pg" id="sec-new">
<h2>6. New Lab Records (by Accession Number)</h2>
<p>Records present in month N but not in month N-1, identified by unique accession number (LBREFID).</p>
{new_recs_html}
</div>

<!-- SECTION 7: SUMMARY DELTA TABLE -->
<div class="section pg" id="sec-summary">
<h2>7. Summary Delta Table</h2>
<p>Key metrics side-by-side across all three monthly data cuts.</p>
{summary_html}
</div>

<!-- FOOTER -->
<div class="footer">
<span>DNLI-I-0001 Monthly Delta Report &middot; Confidential</span>
<span>Generated {now} &middot; monthly_delta_analysis.py</span>
</div>

</body>
</html>"""
    return html


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("Loading data...")
    lab_dfs, prod_dfs = load_data()

    print("Computing data volume delta...")
    vol_delta = data_volume_delta(lab_dfs, prod_dfs)

    print("Computing lab safety metrics...")
    lab_metrics = lab_safety_metrics(lab_dfs)

    print("Computing hepatic/renal analysis...")
    hepatic = hepatic_analysis(lab_dfs)

    print("Computing dosing analysis...")
    dosing_data = dosing_analysis(prod_dfs)

    print("Identifying new lab records...")
    new_recs = new_lab_records(lab_dfs)

    print("Building summary delta table...")
    summary = summary_delta_table(lab_dfs, prod_dfs, dosing_data)

    print("Tracking data changes...")
    changes = data_changes_tracker(lab_dfs, prod_dfs)

    print("Generating HTML report...")
    html = generate_html(vol_delta, lab_metrics, hepatic, dosing_data, new_recs, summary, changes)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / "monthly-delta-report.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {out_path}")
    print(f"File size: {out_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
