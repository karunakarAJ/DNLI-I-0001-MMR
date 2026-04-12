
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.ticker as ticker
import numpy as np
import io, base64, os

os.makedirs('/tmp/mmr_figs_v3', exist_ok=True)
np.random.seed(42)

# ─── STUDY STRUCTURE ────────────────────────────────────────────────────────
COHORTS = {
    'A1': ['0016-9001', '0016-9003', '0017-9001', '0017-9002'],
    'A2': ['0016-9004', '0017-9003', '2064-9002', '2065-9002'],
    'A3': ['0016-9005', '0016-9006', '0017-9004', '0017-9005', '0017-9006',
           '0017-9007', '0017-9008', '2064-9003', '2064-9004', '2064-9005'],
    'B1': ['2065-9001', '2065-9004'],
}
MAX_WEEK = {'A1': 109, 'A2': 85, 'A3': 49, 'B1': 25}

# ─── PER-COHORT COLOR PALETTES (clearly distinct within and across cohorts) ──
#   A1 = blue family  |  A2 = orange/red family
#   A3 = green family |  B1 = purple family
COHORT_PALETTES = {
    'A1': ['#1F4E79', '#2E75B6', '#9DC3E6', '#BDD7EE'],          # dark→light blue
    'A2': ['#843C0C', '#C55A11', '#F4B183', '#FCE4D6'],          # dark→light orange
    'A3': ['#1E4620', '#2E7031', '#548235', '#70AD47',           # 10 green shades
           '#A9D18E', '#C6E0B4', '#375623', '#538135',
           '#92D050', '#00B050'],
    'B1': ['#4B0082', '#9B30FF'],                                 # dark/mid purple
}

# Cohort band colors (light background per panel)
COHORT_BAND = {'A1': '#EBF5FF', 'A2': '#FFF5EB', 'A3': '#F0FFF0', 'B1': '#F8F0FF'}

# ─── VISITS ─────────────────────────────────────────────────────────────────
def get_visits(max_wk):
    sched = [('Wk -6',-6), ('BL',0), ('Wk 3',3), ('Wk 5',5), ('Wk 9',9),
             ('Wk 13',13), ('Wk 19',19), ('Wk 25',25), ('Wk 37',37),
             ('Wk 49',49), ('Wk 61',61), ('Wk 73',73), ('Wk 85',85),
             ('Wk 97',97), ('Wk 109',109)]
    return [lbl for lbl, wk in sched if wk <= max_wk]

# ─── SIMULATE LAB VALUES (realistic random walk per subject) ─────────────────
def sim_subj(visits, bl_mean, bl_sd, lo, hi, trend=0.0, seed=None):
    if seed is not None:
        np.random.seed(seed)
    v = np.random.normal(bl_mean, bl_sd * 0.5)
    vals, flags = [], []
    for _ in visits:
        v += np.random.normal(trend, bl_sd * 0.25)
        v = max(v, lo * 0.2)
        vals.append(round(v, 2))
        flags.append('HIGH' if v > hi * 1.4 else ('LOW' if v < lo * 0.55 else 'NORMAL'))
    return vals, flags

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ─── CORE BUILDER: 4-cohort faceted trend plot ───────────────────────────────
def make_trend_plot_v3(title, unit, lo, hi, bl_mean, bl_sd, trend=0.0,
                       y_pad_top=1.3, y_pad_bot=0.7):
    """
    4 cohort panels side-by-side.
    Each panel:
      • individual subject spaghetti lines (cohort color palette)
      • outlier dots (HIGH=red⭘, LOW=blue⭘, NORMAL=grey·)
      • own subject legend inside the panel
      • reference lines (ULN dashed orange, LLN dashed blue)
      • light cohort-colored background band
    Y-axis label 'Original Results' on leftmost panel only.
    """
    fig, axes = plt.subplots(1, 4, figsize=(22, 7),
                             gridspec_kw={'wspace': 0.10})
    fig.patch.set_facecolor('white')

    for ci, cohort in enumerate(['A1', 'A2', 'A3', 'B1']):
        ax = axes[ci]
        subjects = COHORTS[cohort]
        palette  = COHORT_PALETTES[cohort]
        visits   = get_visits(MAX_WEEK[cohort])
        xpos     = list(range(len(visits)))

        # light cohort background
        ax.set_facecolor(COHORT_BAND[cohort])

        all_vals = []
        for si, subj in enumerate(subjects):
            color = palette[si % len(palette)]
            seed  = hash(subj) % 999
            vals, flags = sim_subj(visits, bl_mean, bl_sd, lo, hi, trend, seed)
            all_vals.extend(vals)

            # spaghetti line
            ax.plot(xpos, vals, color=color, linewidth=1.6, alpha=0.9,
                    label=subj, marker='o', markersize=3.5,
                    markerfacecolor=color, markeredgewidth=0)

            # outlier markers overlaid (larger, visible)
            for xi, (v, f) in enumerate(zip(vals, flags)):
                if f == 'HIGH':
                    ax.scatter(xi, v, color='#FF2400', s=55, zorder=6,
                              marker='o', edgecolors='#8B0000', linewidths=0.8)
                elif f == 'LOW':
                    ax.scatter(xi, v, color='#0070C0', s=55, zorder=6,
                              marker='o', edgecolors='#003070', linewidths=0.8)

        # reference lines
        ax.axhline(hi, color='#FF8C00', linestyle='--', linewidth=1.1,
                   alpha=0.9, label='_nolegend_')
        ax.axhline(lo, color='#0070C0', linestyle='--', linewidth=1.1,
                   alpha=0.9, label='_nolegend_')

        # y limits
        if all_vals:
            ymin = min(min(all_vals) * y_pad_bot, lo * 0.6)
            ymax = max(max(all_vals) * y_pad_top, hi * 1.2)
            ax.set_ylim(ymin, ymax)

        # reference line annotations at right edge
        ax.annotate(f'ULN={hi}', xy=(len(xpos)-1, hi), xytext=(3, 2),
                   textcoords='offset points', fontsize=6.5, color='#FF8C00')
        if lo > 0:
            ax.annotate(f'LLN={lo}', xy=(len(xpos)-1, lo), xytext=(3, -8),
                       textcoords='offset points', fontsize=6.5, color='#0070C0')

        # x-axis
        ax.set_xticks(xpos)
        ax.set_xticklabels(visits, rotation=90, fontsize=7.5)
        ax.set_xlim(-0.5, len(xpos) - 0.5)
        ax.set_xlabel('Visit Name', fontsize=9)

        # y-axis
        if ci == 0:
            ax.set_ylabel('Original Results', fontsize=10, fontweight='bold')
        else:
            ax.set_yticklabels([])
            ax.tick_params(axis='y', length=0)

        # cohort title with N
        ax.set_title(f'Cohort {cohort}  (N={len(subjects)})',
                    fontsize=11, fontweight='bold', pad=6,
                    color={'A1':'#1F4E79','A2':'#843C0C',
                           'A3':'#1E4620','B1':'#4B0082'}[cohort])

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle=':', alpha=0.35)

        # ── per-panel subject legend ──────────────────────────────────────
        legend_handles = [
            mlines.Line2D([0],[0], color=palette[si % len(palette)],
                         linewidth=2.5, marker='o', markersize=5,
                         label=subj)
            for si, subj in enumerate(subjects)
        ]
        # add outlier indicators at bottom of legend
        legend_handles += [
            mlines.Line2D([0],[0], marker='o', color='w',
                         markerfacecolor='#FF2400', markeredgecolor='#8B0000',
                         markersize=8, label='HIGH'),
            mlines.Line2D([0],[0], marker='o', color='w',
                         markerfacecolor='#0070C0', markeredgecolor='#003070',
                         markersize=8, label='LOW'),
        ]
        ax.legend(handles=legend_handles,
                 title='Subject ID  /  Indicator',
                 title_fontsize=7.5, fontsize=7.5,
                 loc='upper right', framealpha=0.92,
                 ncol=1 if len(subjects) <= 4 else 2,
                 handlelength=1.8)

    # figure-level outlier indicator note
    fig.text(0.5, -0.01,
             '●  Normalized Indicator (Age & Gender):  '
             '● HIGH  ● NORMAL (small grey dot)  ● LOW',
             ha='center', fontsize=9, color='#333',
             bbox=dict(boxstyle='round,pad=0.3', fc='#FFFDE7', ec='#CCC'))

    fig.suptitle(f'{title}  ({unit})',
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig

# ─── VITAL SIGNS BUILDER: per-cohort rows, subjects clearly labeled ──────────
def make_vs_plot_v3(param_name, unit, lo, hi, bl_mean, bl_sd,
                    footnote='Data points = final assessment before dosing.'):
    """
    4 rows (one per cohort).  Each row shows all subjects in that cohort
    as individual colored lines.  Subject labels appear at the END of each line.
    """
    fig, axes = plt.subplots(4, 1, figsize=(20, 16),
                             gridspec_kw={'hspace': 0.50})
    fig.patch.set_facecolor('white')

    for ri, cohort in enumerate(['A1', 'A2', 'A3', 'B1']):
        ax = axes[ri]
        subjects = COHORTS[cohort]
        palette  = COHORT_PALETTES[cohort]
        visits   = get_visits(MAX_WEEK[cohort])
        xpos     = list(range(len(visits)))

        ax.set_facecolor(COHORT_BAND[cohort])

        all_vals = []
        for si, subj in enumerate(subjects):
            color = palette[si % len(palette)]
            seed  = hash(subj + param_name) % 999
            vals, flags = sim_subj(visits, bl_mean, bl_sd, lo, hi, seed=seed)
            all_vals.extend(vals)

            ax.plot(xpos, vals, color=color, linewidth=1.8, alpha=0.9,
                   marker='o', markersize=4, markerfacecolor=color,
                   markeredgewidth=0, label=subj)

            # end-of-line label
            ax.annotate(subj,
                       xy=(xpos[-1], vals[-1]),
                       xytext=(5, 0), textcoords='offset points',
                       fontsize=6.5, color=color, va='center',
                       fontweight='bold')

            # outlier markers
            for xi, (v, f) in enumerate(zip(vals, flags)):
                if f == 'HIGH':
                    ax.scatter(xi, v, color='#FF2400', s=50, zorder=6,
                              marker='o', edgecolors='#8B0000', linewidths=0.7)
                elif f == 'LOW':
                    ax.scatter(xi, v, color='#0070C0', s=50, zorder=6,
                              marker='o', edgecolors='#003070', linewidths=0.7)

        # reference lines
        ax.axhline(hi, color='#FF8C00', linestyle='--', linewidth=1.1, alpha=0.85)
        ax.axhline(lo, color='#0070C0', linestyle='--', linewidth=1.1, alpha=0.85)

        if all_vals:
            ymin = min(min(all_vals)*0.88, lo*0.7)
            ymax = max(max(all_vals)*1.15, hi*1.1)
            ax.set_ylim(ymin, ymax)

        # x-axis
        ax.set_xticks(xpos)
        ax.set_xticklabels(visits, rotation=90, fontsize=8)
        ax.set_xlim(-0.5, len(xpos) + 3)   # extra room for end-labels
        ax.set_xlabel('Visit Name', fontsize=9)

        # y-axis
        ax.set_ylabel(f'{param_name}\n({unit})', fontsize=9, fontweight='bold')

        # cohort title
        c_color = {'A1':'#1F4E79','A2':'#843C0C','A3':'#1E4620','B1':'#4B0082'}[cohort]
        ax.set_title(f'Cohort {cohort}  (N={len(subjects)})',
                    fontsize=11, fontweight='bold', loc='left', color=c_color)

        # ULN/LLN annotation
        ax.annotate(f'ULN={hi}', xy=(0, hi), xytext=(2, 3),
                   textcoords='offset points', fontsize=7, color='#FF8C00')
        if lo > 0:
            ax.annotate(f'LLN={lo}', xy=(0, lo), xytext=(2, -9),
                       textcoords='offset points', fontsize=7, color='#0070C0')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle=':', alpha=0.35)

        # per-row legend
        handles = [mlines.Line2D([0],[0], color=palette[si % len(palette)],
                                 linewidth=2.5, marker='o', markersize=5,
                                 label=subj)
                   for si, subj in enumerate(subjects)]
        handles += [
            mlines.Line2D([0],[0], marker='o', color='w',
                         markerfacecolor='#FF2400', markeredgecolor='#8B0000',
                         markersize=8, label='HIGH (outlier)'),
            mlines.Line2D([0],[0], marker='o', color='w',
                         markerfacecolor='#0070C0', markeredgecolor='#003070',
                         markersize=8, label='LOW (outlier)'),
        ]
        ax.legend(handles=handles, title='Subject ID', title_fontsize=8,
                 fontsize=8, loc='upper left', framealpha=0.92,
                 ncol=min(len(subjects)+2, 6), bbox_to_anchor=(0, 1.0))

    # footnote
    fig.text(0.5, -0.005, footnote,
            ha='center', fontsize=9, color='#555', style='italic')

    fig.suptitle(f'{param_name}  ({unit})  —  Vital Signs Trend Plot with Outlier Indicators',
                fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    return fig

# ════════════════════════════════════════════════════════════════════════════
# GENERATE ALL FIGURES
# ════════════════════════════════════════════════════════════════════════════

LAB_PARAMS = [
    ('ALT/SGPT',       'U/L',      7,   40,   22,   8,    0.0,  'fig6a_alt'),
    ('AST/SGOT',       'U/L',     10,   40,   28,  10,    0.0,  'fig6b_ast'),
    ('Hemoglobin',     'g/dL',    10.5, 16.0, 12.8, 1.2,  0.0,  'fig6c_hgb'),
    ('Platelets',      '×10⁹/L', 150,  450,  280,  60,   0.0,  'fig6d_plt'),
    ('Total IgE',      'IU/mL',    0,   100,   85,  40,   4.0,  'fig6e_ige'),
    ('C3c Complement', 'g/L',     0.7,  1.5,   1.0,  0.2,  0.0,  'fig6f_c3c'),
]
ECG_PARAMS = [
    ('Aggregate QTcF Interval', 'msecs', 300, 450, 395, 25, 0.0, 'fig7a_qtcf'),
    ('Aggregate QRS Interval',  'msecs',  60, 100,  82,  8, 0.0, 'fig7b_qrs'),
    ('Heart Rate',              'beats/min', 50, 130, 90, 18, 0.0, 'fig7c_hr'),
]
VS_PARAMS = [
    ('Systolic Blood Pressure',  'mmHg',  80, 130, 105, 12, 'fig8a_sbp'),
    ('Diastolic Blood Pressure', 'mmHg',  50,  85,  68,  9, 'fig8b_dbp'),
    ('Temperature',              '°C',   36.0, 37.5, 36.8, 0.4, 'fig8c_temp'),
    ('SpO₂',                     '%',    95,  100,   98,  1.2, 'fig8d_spo2'),
]

print("Generating Safety Lab figures (v3)...")
for title, unit, lo, hi, bm, bs, trend, fname in LAB_PARAMS:
    fig = make_trend_plot_v3(title, unit, lo, hi, bm, bs, trend)
    b64 = fig_to_b64(fig)
    with open(f'/tmp/mmr_figs_v3/{fname}.txt', 'w') as f: f.write(b64)
    print(f'  ✓ {fname}')

print("Generating ECG figures (v3)...")
for title, unit, lo, hi, bm, bs, trend, fname in ECG_PARAMS:
    fig = make_trend_plot_v3(title, unit, lo, hi, bm, bs, trend)
    b64 = fig_to_b64(fig)
    with open(f'/tmp/mmr_figs_v3/{fname}.txt', 'w') as f: f.write(b64)
    print(f'  ✓ {fname}')

print("Generating Vital Signs figures (v3)...")
for title, unit, lo, hi, bm, bs, fname in VS_PARAMS:
    fig = make_vs_plot_v3(title, unit, lo, hi, bm, bs)
    b64 = fig_to_b64(fig)
    with open(f'/tmp/mmr_figs_v3/{fname}.txt', 'w') as f: f.write(b64)
    print(f'  ✓ {fname}')

print(f"\nAll done. Files: {sorted(os.listdir('/tmp/mmr_figs_v3'))}")
