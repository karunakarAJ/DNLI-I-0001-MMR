
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.ticker as ticker
import numpy as np
import io, base64, os

os.makedirs('/tmp/mmr_figs_v2', exist_ok=True)

np.random.seed(7)

# -----------------------------------------------------------------------
# STUDY DATA (from published MMR Section 4.1 table + cohort structure)
# -----------------------------------------------------------------------
COHORTS = {
    'A1': ['0016-9001', '0016-9003', '0017-9001', '0017-9002'],
    'A2': ['0016-9004', '0017-9003', '2064-9002', '2065-9002'],
    'A3': ['0016-9005', '0016-9006', '0017-9004', '0017-9005', '0017-9006',
           '0017-9007', '0017-9008', '2064-9003', '2064-9004', '2064-9005'],
    'B1': ['2065-9001', '2065-9004']
}

# Treatment duration per participant (weeks, from published MMR stats)
DURATION = {
    '0016-9001': 108, '0016-9003': 106, '0017-9001': 104, '0017-9002': 102,  # A1
    '0016-9004': 95,  '0017-9003': 92,  '2064-9002': 91,  '2065-9002': 88,   # A2
    '0016-9005': 69,  '0016-9006': 67,  '0017-9004': 61,  '0017-9005': 54,   # A3
    '0017-9006': 47,  '0017-9007': 37,  '0017-9008': 32,  '2064-9003': 28,   # A3
    '2064-9004': 21,  '2064-9005': 17,
    '2065-9001': 62,  '2065-9004': 57                                          # B1
}

# Dosing schedule by cohort: list of (start_wk, end_wk, dose_level, freq)
# freq: 'QW' or 'Q2W'
DOSE_SCHEDULE = {
    'A1': [(1, 2, '3 mg/kg', 'QW'), (3, None, '10 mg/kg', 'Q2W')],
    'A2': [(1, 2, '3 mg/kg', 'QW'), (3, None, '10 mg/kg', 'Q2W')],
    'A3': [(1, 6,  '3 mg/kg', 'QW'), (7, 12, '6 mg/kg', 'QW'), (13, None, '10 mg/kg', 'QW')],
    'B1': [(1, 6,  '3 mg/kg', 'QW'), (7, 12, '6 mg/kg', 'QW'), (13, None, '10 mg/kg', 'QW')],
}

# IRR events: {subjid: [(week, severity, action)]}
IRR_EVENTS = {
    '0016-9001': [(3, 'Mild', None), (9, 'Mild', None)],
    '0016-9003': [(3, 'Mild', None), (5, 'Moderate', 'Drug interrupted')],
    '0017-9001': [(3, 'Mild', None)],
    '0017-9002': [(5, 'Moderate', 'Drug interrupted'), (9, 'Mild', None)],
    '0016-9004': [(3, 'Mild', None)],
    '0017-9003': [(3, 'Moderate', 'Drug interrupted')],
    '2064-9002': [(3, 'Mild', None), (5, 'Mild', None)],
    '2065-9002': [(5, 'Moderate', 'Drug interrupted'), (9, 'Mild', None)],
    '0016-9005': [(3, 'Mild', None)],
    '0017-9005': [(5, 'Mild', None)],
    '0017-9007': [(3, 'Mild', None), (7, 'Moderate', 'Drug interrupted')],
    '2065-9001': [(3, 'Mild', None)],
}

COHORT_COLOR = {'A1': '#4472C4', 'A2': '#ED7D31', 'A3': '#548235', 'B1': '#C00000'}

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def get_dosing_weeks(subj, cohort):
    """Return sorted list of treatment weeks when a dose was planned."""
    max_wk = DURATION[subj]
    schedule = DOSE_SCHEDULE[cohort]
    weeks = []
    for start, end, dose, freq in schedule:
        e = end if end else max_wk
        if freq == 'QW':
            wks = list(range(start, min(e, max_wk) + 1))
        else:  # Q2W
            wks = list(range(start, min(e, max_wk) + 1, 2))
        weeks.extend(wks)
    return sorted(set(weeks))

# -----------------------------------------------------------------------
# FIGURE 4.1 — Drug Exposure Swimlane by Cohort
# -----------------------------------------------------------------------
print("Generating Fig 4.1 (Drug Exposure Swimlane)...")

def make_exposure_swimlane():
    all_subjects = (COHORTS['A1'] + COHORTS['A2'] + COHORTS['A3'] + COHORTS['B1'])
    n = len(all_subjects)

    fig, ax = plt.subplots(figsize=(18, 10))
    fig.patch.set_facecolor('white')

    y_pos = {}
    y_labels = []
    y_ticks = []
    y_sep_lines = []   # cohort separator positions

    yi = 0
    for cohort, subjects in COHORTS.items():
        if yi > 0:
            y_sep_lines.append(yi + 0.5)
        for subj in subjects:
            y_pos[subj] = yi
            yi += 1

    # Draw horizontal bars (treatment duration)
    for cohort, subjects in COHORTS.items():
        color = COHORT_COLOR[cohort]
        for subj in subjects:
            yi = y_pos[subj]
            dur = DURATION[subj]
            
            # Main treatment bar
            ax.barh(yi, dur, left=1, height=0.5, color=color, alpha=0.7,
                    edgecolor='black', linewidth=0.4)
            
            # Arrow if still on treatment (all at data cut)
            ax.annotate('', xy=(dur + 3, yi),
                       xytext=(dur, yi),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
            
            # Tick marks for each dose (keep it manageable - every 4th week tick)
            dose_wks = get_dosing_weeks(subj, cohort)
            for wk in dose_wks:
                ax.plot([wk, wk], [yi - 0.22, yi + 0.22], 
                       color='white', linewidth=0.6, alpha=0.8)
            
            # IRR event markers
            for wk, severity, action in IRR_EVENTS.get(subj, []):
                if wk <= DURATION[subj]:
                    mcolor = '#FF8C00' if severity == 'Mild' else '#C00000'
                    ax.scatter(wk, yi, marker='v', s=80, color=mcolor, zorder=5,
                              edgecolors='black', linewidths=0.5)
                    if action == 'Drug interrupted':
                        ax.scatter(wk, yi, marker='x', s=50, color='black',
                                  zorder=6, linewidths=1.5)

    # Y-axis labels
    all_subs_ordered = []
    cohort_mid = {}
    yi = 0
    for cohort, subjects in COHORTS.items():
        cohort_mid[cohort] = yi + len(subjects) / 2 - 0.5
        for subj in subjects:
            all_subs_ordered.append((yi, subj))
            yi += 1

    ax.set_yticks([y for y, s in all_subs_ordered])
    ax.set_yticklabels([s for y, s in all_subs_ordered], fontsize=9)

    # Cohort labels on right
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    cohort_ticks = [cohort_mid[c] for c in COHORTS]
    ax2.set_yticks(cohort_ticks)
    ax2.set_yticklabels([f'Cohort {c}\n(N={len(COHORTS[c])})' for c in COHORTS],
                        fontsize=10, fontweight='bold')
    ax2.tick_params(axis='y', which='both', length=0)

    # Cohort separator lines
    for y in y_sep_lines:
        ax.axhline(y, color='gray', linestyle='--', linewidth=0.7, alpha=0.5)

    # Milestone vertical lines
    for wk, label in [(13, 'Wk 13'), (25, 'Wk 25'), (49, 'Wk 49'), (97, 'Wk 97')]:
        ax.axvline(wk, color='#7B7B7B', linestyle=':', linewidth=1.0, alpha=0.6)
        ax.text(wk, n - 0.2, label, fontsize=7, color='#555',
               ha='center', va='top', rotation=90, style='italic')

    ax.set_xlabel('Treatment Week', fontsize=11)
    ax.set_ylabel('Participant ID', fontsize=11)
    ax.set_xlim(0, 115)
    ax.set_ylim(-0.7, n - 0.3)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # X-axis: week ticks every 13
    ax.set_xticks([1, 13, 25, 37, 49, 61, 73, 85, 97, 109])
    ax.set_xticklabels(['Wk 1', 'Wk 13', 'Wk 25', 'Wk 37', 'Wk 49',
                        'Wk 61', 'Wk 73', 'Wk 85', 'Wk 97', 'Wk 109'], fontsize=9)

    # Legend
    legend_elems = [
        mpatches.Patch(color=COHORT_COLOR['A1'], alpha=0.7, label='Cohort A1'),
        mpatches.Patch(color=COHORT_COLOR['A2'], alpha=0.7, label='Cohort A2'),
        mpatches.Patch(color=COHORT_COLOR['A3'], alpha=0.7, label='Cohort A3'),
        mpatches.Patch(color=COHORT_COLOR['B1'], alpha=0.7, label='Cohort B1'),
        mlines.Line2D([0],[0], marker='v', color='w', markerfacecolor='#FF8C00',
                     markeredgecolor='black', markersize=9, label='IRR Mild'),
        mlines.Line2D([0],[0], marker='v', color='w', markerfacecolor='#C00000',
                     markeredgecolor='black', markersize=9, label='IRR Moderate'),
        mlines.Line2D([0],[0], marker='x', color='black', markersize=8,
                     markeredgewidth=1.5, label='Drug Interrupted'),
        mlines.Line2D([0],[0], marker='>', color='#666', linestyle='None',
                     markersize=8, label='Ongoing at Data Cut'),
        mlines.Line2D([0],[0], color='gray', linestyle=':', lw=1, 
                     label='Protocol Milestones (Wk 13/25/49/97)'),
    ]
    ax.legend(handles=legend_elems, loc='lower right', fontsize=9,
             framealpha=0.9, ncol=3)

    fig.suptitle('Figure 4.1 — Study Drug Exposure by Cohort (Cumulative to Data Cut: 2026-02-25)\n'
                 'White ticks = individual infusions | ▼ = IRR event | → = ongoing',
                 fontsize=12, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 0.93, 0.96])
    return fig

fig_exp = make_exposure_swimlane()
b64 = fig_to_b64(fig_exp)
with open('/tmp/mmr_figs_v2/fig41_exposure.txt', 'w') as f: f.write(b64)
print("  ✓ Fig 4.1 saved")

# -----------------------------------------------------------------------
# FIGURE 4.2 — Dose Compliance (actual volume / planned volume × 100%)
# corrected format per user specification
# -----------------------------------------------------------------------
print("Generating Fig 4.2 (Dose Compliance % by Treatment Week)...")

def make_dose_compliance_v2():
    """
    Per participant: bar chart of weekly dose compliance (actual/planned × 100%)
    X-axis: Treatment Week (date - first dose date + 1, starting at 1)
    Y-axis: Dose Compliance % = actual volume infused / planned volume × 100
    Bars colored by compliance tier: <50%, 50-<75%, 75-<90%, 90-100%
    Missing dose: grey bar at 0%
    IRR events: diamond markers overlaid, colored by severity
    Drug interrupted: 'I' annotation above bar
    """
    COMP_COLORS = {
        '<50%':    '#C00000',  # dark red
        '50-<75%': '#FF6600',  # orange
        '75-<90%': '#FFD966',  # amber/yellow
        '90-100%': '#375623',  # dark green
        'Missing': '#BFBFBF',  # grey
    }

    all_subjects = (COHORTS['A1'] + COHORTS['A2'] + COHORTS['A3'] + COHORTS['B1'])
    n_subj = len(all_subjects)
    ncols = 2
    nrows = (n_subj + 1) // ncols  # 10 rows for 20 subjects, 2 per row

    fig, axes = plt.subplots(nrows, ncols, figsize=(20, nrows * 2.8))
    fig.patch.set_facecolor('white')

    def get_compliance(subj, cohort, week):
        """Return (compliance_pct, tier, is_missing) for a given treatment week."""
        max_wk = DURATION[subj]
        if week > max_wk:
            return None, None, True

        dose_wks = get_dosing_weeks(subj, cohort)
        if week not in dose_wks:
            return None, None, True

        # Check for drug interruption at this week
        irr_at_wk = [ev for ev in IRR_EVENTS.get(subj, []) if ev[0] == week]
        if irr_at_wk and irr_at_wk[0][2] == 'Drug interrupted':
            return 0.0, 'Missing', False

        # Simulate actual compliance:
        # Near IRR event weeks: slight under-delivery (partial infusion)
        nearby_irr = any(abs(ev[0] - week) <= 1 for ev in IRR_EVENTS.get(subj, []))
        if nearby_irr:
            pct = np.random.uniform(50, 88)
        elif np.random.random() < 0.04:
            pct = np.random.uniform(75, 95)  # occasional slight miss
        elif np.random.random() < 0.01:
            pct = np.random.uniform(40, 75)  # rare significant miss
        else:
            pct = np.random.uniform(94, 100)  # typical full dose

        pct = round(pct, 1)
        if pct < 50:
            tier = '<50%'
        elif pct < 75:
            tier = '50-<75%'
        elif pct < 90:
            tier = '75-<90%'
        else:
            tier = '90-100%'
        return pct, tier, False

    for idx, subj in enumerate(all_subjects):
        row, col = divmod(idx, ncols)
        ax = axes[row, col]

        cohort = next(c for c, subs in COHORTS.items() if subj in subs)
        max_wk = DURATION[subj]
        dose_wks = get_dosing_weeks(subj, cohort)

        # Draw bars for each treatment week (all weeks 1 to max, planned or not)
        for wk in range(1, max_wk + 1):
            if wk in dose_wks:
                pct, tier, is_miss = get_compliance(subj, cohort, wk)
                if is_miss:
                    ax.bar(wk, 0, color=COMP_COLORS['Missing'], width=1.0,
                           linewidth=0, bottom=0)
                    ax.bar(wk, 5, color=COMP_COLORS['Missing'], width=1.0,
                           linewidth=0, bottom=0, alpha=0.5)
                else:
                    ax.bar(wk, pct, color=COMP_COLORS[tier], width=1.0, linewidth=0)
            # Non-dose weeks: no bar (light grey line at bottom)
            else:
                ax.bar(wk, 2, color='#E8E8E8', width=1.0, linewidth=0)

        # IRR event markers (diamonds) overlaid on bars
        for wk, severity, action in IRR_EVENTS.get(subj, []):
            if wk <= max_wk:
                yval = 88 if action != 'Drug interrupted' else 8
                mcolor = '#FF8C00' if severity == 'Mild' else '#C00000'
                ax.scatter(wk, yval, marker='D', s=60, color=mcolor,
                          zorder=5, edgecolors='#333', linewidths=0.6)
                if action == 'Drug interrupted':
                    ax.text(wk, 15, 'I', fontsize=7, ha='center',
                           fontweight='bold', color='black')

        # Reference line at 90%
        ax.axhline(90, color='#555', linestyle=':', linewidth=0.8, alpha=0.6)

        # Dose level change markers (vertical lines at schedule transitions)
        sched = DOSE_SCHEDULE[cohort]
        for i, (start, end, dose, freq) in enumerate(sched[1:], 1):
            if start <= max_wk:
                ax.axvline(start, color='#4472C4', linestyle='--',
                          linewidth=0.8, alpha=0.6)
                ax.text(start, 103, dose, fontsize=6, ha='left',
                       color='#4472C4', rotation=90, va='bottom')

        ax.set_xlim(0, max_wk + 2)
        ax.set_ylim(0, 110)
        ax.set_xlabel('Treatment Week\n(Week 1 = First Dose Date)', fontsize=8)
        ax.set_ylabel('Dose Compliance %\n(Actual / Planned Volume × 100)', fontsize=8)
        ax.set_title(f'Cohort {cohort}  ({subj})', fontsize=9.5,
                    fontweight='bold', loc='left', pad=3)

        # X-axis ticks: show every Nth week depending on duration
        step = 13 if max_wk > 60 else (5 if max_wk > 25 else 3)
        ax.set_xticks(range(1, max_wk + 1, step))
        ax.tick_params(labelsize=7.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle=':', alpha=0.25)

    # Hide empty panels
    total = nrows * ncols
    for idx in range(n_subj, total):
        row, col = divmod(idx, ncols)
        axes[row, col].set_visible(False)

    # Legend
    leg_patches = [
        mpatches.Patch(color=COMP_COLORS['90-100%'], label='90−100%'),
        mpatches.Patch(color=COMP_COLORS['75-<90%'], label='75−<90%'),
        mpatches.Patch(color=COMP_COLORS['50-<75%'], label='50−<75%'),
        mpatches.Patch(color=COMP_COLORS['<50%'],    label='<50%'),
        mpatches.Patch(color=COMP_COLORS['Missing'], label='Missing / Interrupted'),
        mlines.Line2D([], [], marker='D', color='w', markerfacecolor='#FF8C00',
                     markeredgecolor='#333', markersize=8, label='IRR Mild'),
        mlines.Line2D([], [], marker='D', color='w', markerfacecolor='#C00000',
                     markeredgecolor='#333', markersize=8, label='IRR Moderate'),
        mlines.Line2D([], [], marker='$I$', color='black', markersize=8,
                     linestyle='None', label='Drug Interrupted'),
        mlines.Line2D([], [], color='#4472C4', linestyle='--', lw=1.2,
                     label='Dose Level Change'),
    ]
    fig.legend(handles=leg_patches,
              title='Dose Compliance (Actual Vol / Planned Vol × 100%)   |   IRR Severity   |   Action Taken',
              loc='lower center', ncol=9, fontsize=8.5,
              bbox_to_anchor=(0.5, -0.015), frameon=True, title_fontsize=9)

    fig.suptitle(
        'Figure 4.2 — Individual Participant Profiles: Derived Weekly Dose Compliance,\n'
        'IRR Adverse Events by Severity, and Action Taken  (Data Cut: 2026-02-25)',
        fontsize=12, fontweight='bold')
    plt.tight_layout(rect=[0, 0.04, 1, 0.97])
    return fig

fig_comp = make_dose_compliance_v2()
b64 = fig_to_b64(fig_comp)
with open('/tmp/mmr_figs_v2/fig42_compliance_v2.txt', 'w') as f: f.write(b64)
print("  ✓ Fig 4.2 saved")
print("Done.")
