#!/usr/bin/env python3
"""
Generate a polished Excalidraw Architecture & Data Pipeline diagram for DNLI-I-0001 MMR.
Outputs: docs/mmr-pipeline-architecture.excalidraw
"""

import json
import random
import time
from pathlib import Path

# ── ID & seed helpers ──────────────────────────────────────────────────────
_counter = 0
def uid():
    global _counter
    _counter += 1
    return f"elem_{_counter:04d}"

def seed():
    return random.randint(100000, 999999999)

# ── Color palette ──────────────────────────────────────────────────────────
C = {
    "pri":      "#1a3a5c",   # dark blue (text, borders)
    "accent":   "#0066cc",   # bright blue
    "bg_data":  "#e0f2fe",   # light blue
    "bg_expl":  "#fef3c7",   # amber
    "bg_plan":  "#fff7ed",   # light orange
    "bg_impl":  "#dbeafe",   # blue
    "bg_rev":   "#fce7f3",   # pink
    "bg_integ": "#d1fae5",   # green
    "bg_gen":   "#ede9fe",   # purple
    "bg_out":   "#dcfce7",   # green
    "str_data": "#0284c7",
    "str_expl": "#d97706",
    "str_plan": "#ea580c",
    "str_impl": "#2563eb",
    "str_rev":  "#db2777",
    "str_integ":"#059669",
    "str_gen":  "#7c3aed",
    "str_out":  "#16a34a",
    "white":    "#ffffff",
    "gray":     "#64748b",
    "arrow":    "#475569",
    "arrow_hi": "#0066cc",
    "txt_dark": "#1e293b",
    "txt_sub":  "#64748b",
    "card_bg":  "#f8fafc",
    "card_str": "#cbd5e1",
}

# ── Element factories ─────────────────────────────────────────────────────
def rect(x, y, w, h, bg="#ffffff", stroke="#000000", sw=2, ss="solid",
         roughness=0, opacity=100, rounded=True, group=None, bound=None):
    eid = uid()
    r = {"type": 3} if rounded else {"type": 1}
    return {
        "id": eid, "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": ss,
        "roughness": roughness, "opacity": opacity,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": r,
        "seed": seed(), "version": 1, "versionNonce": seed(),
        "isDeleted": False,
        "boundElements": bound,
        "updated": int(time.time() * 1000),
        "link": None, "locked": False,
    }

def text(x, y, txt, size=16, family=1, color="#000000", align="center",
         valign="middle", w=None, h=None, group=None, bold=False,
         container=None):
    eid = uid()
    lines = txt.split("\n")
    line_h = size * 1.25
    calc_h = line_h * len(lines)
    calc_w = max(len(line) for line in lines) * size * 0.6
    return {
        "id": eid, "type": "text",
        "x": x, "y": y,
        "width": w or calc_w, "height": h or calc_h,
        "angle": 0,
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None, "roundness": None,
        "seed": seed(), "version": 1, "versionNonce": seed(),
        "isDeleted": False,
        "boundElements": None,
        "updated": int(time.time() * 1000),
        "link": None, "locked": False,
        "text": txt,
        "fontSize": size,
        "fontFamily": family,
        "textAlign": align,
        "verticalAlign": valign,
        "containerId": container,
        "originalText": txt,
        "autoResize": True,
        "lineHeight": 1.25,
    }

def arrow(x1, y1, x2, y2, start_id=None, end_id=None, color="#475569",
          sw=2, ss="solid", label=None):
    eid = uid()
    dx = x2 - x1
    dy = y2 - y1
    el = {
        "id": eid, "type": "arrow",
        "x": x1, "y": y1,
        "width": abs(dx), "height": abs(dy),
        "angle": 0,
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": ss,
        "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None,
        "roundness": {"type": 2},
        "seed": seed(), "version": 1, "versionNonce": seed(),
        "isDeleted": False,
        "boundElements": None,
        "updated": int(time.time() * 1000),
        "link": None, "locked": False,
        "points": [[0, 0], [dx, dy]],
        "lastCommittedPoint": None,
        "startBinding": {"elementId": start_id, "focus": 0, "gap": 5} if start_id else None,
        "endBinding": {"elementId": end_id, "focus": 0, "gap": 5} if end_id else None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
    }
    return el

def diamond(x, y, w, h, bg="#ffffff", stroke="#000000", sw=2, group=None):
    eid = uid()
    return {
        "id": eid, "type": "diamond",
        "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": seed(), "version": 1, "versionNonce": seed(),
        "isDeleted": False,
        "boundElements": None,
        "updated": int(time.time() * 1000),
        "link": None, "locked": False,
    }

def ellipse(x, y, w, h, bg="#ffffff", stroke="#000000", sw=2, group=None):
    eid = uid()
    return {
        "id": eid, "type": "ellipse",
        "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": stroke, "backgroundColor": bg,
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100,
        "groupIds": [group] if group else [],
        "frameId": None,
        "roundness": {"type": 2},
        "seed": seed(), "version": 1, "versionNonce": seed(),
        "isDeleted": False,
        "boundElements": None,
        "updated": int(time.time() * 1000),
        "link": None, "locked": False,
    }


# ── Composite helpers ─────────────────────────────────────────────────────
def labeled_box(x, y, w, h, title, subtitle=None, bg="#ffffff", stroke="#000000",
                title_size=14, sub_size=11, group=None):
    """Create a rounded rectangle with centered title and optional subtitle."""
    elems = []
    gid = group or uid()
    r = rect(x, y, w, h, bg=bg, stroke=stroke, sw=2, group=gid)
    elems.append(r)
    # Title
    if subtitle:
        t = text(x, y + h/2 - title_size - 2, title, size=title_size,
                 color=C["txt_dark"], w=w, align="center", group=gid,
                 container=r["id"])
        s = text(x, y + h/2 + 4, subtitle, size=sub_size,
                 color=C["txt_sub"], w=w, align="center", group=gid,
                 container=r["id"])
        elems.extend([t, s])
    else:
        t = text(x, y + h/2 - title_size/2, title, size=title_size,
                 color=C["txt_dark"], w=w, align="center", group=gid,
                 container=r["id"])
        elems.append(t)
    return elems, r["id"], gid

def section_header(x, y, w, title, bg, stroke, num=None):
    """Phase header bar."""
    elems = []
    gid = uid()
    h = 36
    r = rect(x, y, w, h, bg=stroke, stroke=stroke, sw=0, group=gid,
             rounded=True)
    elems.append(r)
    label = f"PHASE {num}: {title}" if num else title
    t = text(x, y + 6, label, size=14, color=C["white"], w=w,
             align="center", group=gid, container=r["id"])
    elems.append(t)
    return elems, gid


# ── BUILD THE DIAGRAM ─────────────────────────────────────────────────────
def build():
    elements = []
    ids = {}  # track box IDs for arrow connections

    # ══════════════════════════════════════════════════════════════════════
    # TITLE
    # ══════════════════════════════════════════════════════════════════════
    elements.append(text(200, 20, "DNLI-I-0001  MMR Pipeline Architecture", size=28,
                         color=C["pri"], w=900, align="center"))
    elements.append(text(200, 58, "Multi-Agent AI Pipeline  |  Claude Code  |  Safety-Focused Medical Monitoring Report",
                         size=13, color=C["gray"], w=900, align="center"))

    # ══════════════════════════════════════════════════════════════════════
    # ROW 1: DATA SOURCES  (y = 110)
    # ══════════════════════════════════════════════════════════════════════
    y0 = 110
    # Group background
    elements.append(rect(40, y0, 1220, 130, bg=C["bg_data"], stroke=C["str_data"],
                         sw=2, ss="solid", opacity=40))
    hdr, _ = section_header(40, y0, 1220, "DATA SOURCES", C["bg_data"], C["str_data"])
    elements.extend(hdr)

    # Individual data source cards
    src_y = y0 + 50
    card_w, card_h, gap = 220, 65, 25
    sx = 60

    sources = [
        ("Box Cloud", "3 monthly folders\n367921607881"),
        ("EDC / SAS", "110 domains\n(binary, not downloadable)"),
        ("MLM Safety Lab", "CSV ~ 2.3 MB/cut\n12K+ lab records"),
        ("IRT / PROD", "CSV ~ 250 KB/cut\nDosing + disposition"),
        ("ADA (Bioagilytix)", "Vendor CSV transfer\nADA + Neutralizing"),
    ]
    src_ids = []
    for i, (title, sub) in enumerate(sources):
        bx, bid, gid = labeled_box(sx + i * (card_w + gap), src_y, card_w, card_h,
                                    title, sub, bg=C["white"], stroke=C["str_data"],
                                    title_size=13, sub_size=10)
        elements.extend(bx)
        src_ids.append(bid)
    ids["src_box"] = src_ids[2]  # MLM as primary connector
    ids["src_prod"] = src_ids[3]

    # ══════════════════════════════════════════════════════════════════════
    # ROW 2: PHASE 1 + 2  (y = 290)
    # ══════════════════════════════════════════════════════════════════════
    y1 = 290

    # Phase 1: Exploration
    elements.append(rect(40, y1, 580, 150, bg=C["bg_expl"], stroke=C["str_expl"],
                         sw=2, opacity=40))
    hdr, _ = section_header(40, y1, 580, "EXPLORATION", C["bg_expl"], C["str_expl"], num=1)
    elements.extend(hdr)

    bx, bid, _ = labeled_box(60, y1 + 55, 260, 75,
                              "Explore Agent 1", "Codebase structure\nFile inventory",
                              bg=C["white"], stroke=C["str_expl"])
    elements.extend(bx)
    ids["e1"] = bid

    bx, bid, _ = labeled_box(340, y1 + 55, 260, 75,
                              "Explore Agent 2", "Study data extraction\nReport format analysis",
                              bg=C["white"], stroke=C["str_expl"])
    elements.extend(bx)
    ids["e2"] = bid

    # Parallel indicator
    elements.append(text(300, y1 + 78, "||", size=20, color=C["str_expl"], w=40))

    # Phase 2: Planning
    elements.append(rect(680, y1, 580, 150, bg=C["bg_plan"], stroke=C["str_plan"],
                         sw=2, opacity=40))
    hdr, _ = section_header(680, y1, 580, "PLANNING", C["bg_plan"], C["str_plan"], num=2)
    elements.extend(hdr)

    bx, bid, _ = labeled_box(700, y1 + 55, 260, 75,
                              "Plan Agent", "Repository design\nFile inclusion/exclusion",
                              bg=C["white"], stroke=C["str_plan"])
    elements.extend(bx)
    ids["p1"] = bid

    bx, bid, _ = labeled_box(980, y1 + 55, 260, 75,
                              "Protocol Explorer", "Protocol V6 analysis\nSafety/efficacy classification",
                              bg=C["white"], stroke=C["str_plan"])
    elements.extend(bx)
    ids["p2"] = bid

    # ══════════════════════════════════════════════════════════════════════
    # ROW 3: PHASE 3 + 4  (y = 490)
    # ══════════════════════════════════════════════════════════════════════
    y2 = 490

    # Phase 3: Implementation
    elements.append(rect(40, y2, 580, 150, bg=C["bg_impl"], stroke=C["str_impl"],
                         sw=2, opacity=40))
    hdr, _ = section_header(40, y2, 580, "IMPLEMENTATION", C["bg_impl"], C["str_impl"], num=3)
    elements.extend(hdr)

    bx, bid, _ = labeled_box(60, y2 + 55, 260, 75,
                              "QMD Template Creator", "5,376-line Quarto template\nSafety-only sections",
                              bg=C["white"], stroke=C["str_impl"])
    elements.extend(bx)
    ids["qmd"] = bid

    bx, bid, _ = labeled_box(340, y2 + 55, 260, 75,
                              "Main Pipeline", "HTML report (6.6 MB)\nPython scripts + config",
                              bg=C["white"], stroke=C["str_impl"])
    elements.extend(bx)
    ids["main"] = bid

    # Phase 4: Safety Review
    elements.append(rect(680, y2, 580, 150, bg=C["bg_rev"], stroke=C["str_rev"],
                         sw=2, opacity=40))
    hdr, _ = section_header(680, y2, 580, "SAFETY REVIEW", C["bg_rev"], C["str_rev"], num=4)
    elements.extend(hdr)

    bx, bid, _ = labeled_box(700, y2 + 55, 260, 75,
                              "Clinician Reviewer", "8-section signal detection\nBenefit-risk assessment",
                              bg=C["white"], stroke=C["str_rev"])
    elements.extend(bx)
    ids["clin"] = bid

    bx, bid, _ = labeled_box(980, y2 + 55, 260, 75,
                              "Biostatistician Reviewer", "Statistical safety analysis\neDISH validation, power",
                              bg=C["white"], stroke=C["str_rev"])
    elements.extend(bx)
    ids["bios"] = bid

    # Parallel indicator
    elements.append(text(940, y2 + 78, "||", size=20, color=C["str_rev"], w=40))

    # ══════════════════════════════════════════════════════════════════════
    # ROW 4: PHASE 5 + 6  (y = 690)
    # ══════════════════════════════════════════════════════════════════════
    y3 = 690

    # Phase 5: Data Integration
    elements.append(rect(40, y3, 580, 150, bg=C["bg_integ"], stroke=C["str_integ"],
                         sw=2, opacity=40))
    hdr, _ = section_header(40, y3, 580, "DATA INTEGRATION", C["bg_integ"], C["str_integ"], num=5)
    elements.extend(hdr)

    bx, bid, _ = labeled_box(60, y3 + 55, 260, 75,
                              "Box MCP Download", "6 CSV files x 3 months\nMLM safety + PROD dosing",
                              bg=C["white"], stroke=C["str_integ"])
    elements.extend(bx)
    ids["dl"] = bid

    bx, bid, _ = labeled_box(340, y3 + 55, 260, 75,
                              "Delta Analysis", "Month-over-month comparison\nJAN30 -> FEB24 -> MAR20",
                              bg=C["white"], stroke=C["str_integ"])
    elements.extend(bx)
    ids["delta"] = bid

    # Phase 6: Report Generation
    elements.append(rect(680, y3, 580, 150, bg=C["bg_gen"], stroke=C["str_gen"],
                         sw=2, opacity=40))
    hdr, _ = section_header(680, y3, 580, "REPORT GENERATION", C["bg_gen"], C["str_gen"], num=6)
    elements.extend(hdr)

    bx, bid, _ = labeled_box(700, y3 + 55, 260, 75,
                              "generate_mmr.py", "pandas + matplotlib\n8 sections + eDISH plots",
                              bg=C["white"], stroke=C["str_gen"])
    elements.extend(bx)
    ids["gen"] = bid

    bx, bid, _ = labeled_box(980, y3 + 55, 260, 75,
                              "html_to_pdf.py", "Playwright / Chromium\nHeadless PDF rendering",
                              bg=C["white"], stroke=C["str_gen"])
    elements.extend(bx)
    ids["pdf"] = bid

    # ══════════════════════════════════════════════════════════════════════
    # ROW 5: PROCESSING DETAIL  (y = 890)
    # ══════════════════════════════════════════════════════════════════════
    y4 = 890
    elements.append(rect(40, y4, 1220, 160, bg="#f1f5f9", stroke="#94a3b8",
                         sw=1, ss="dashed", opacity=60))
    elements.append(text(50, y4 + 8, "generate_mmr.py  Internal Pipeline", size=12,
                         color=C["gray"], w=400, align="left"))

    # Processing steps as a horizontal chain
    steps = [
        ("Load CSV\n& Filter", "20 treated\nsubjects"),
        ("Demographics\nAggregate", "By cohort\nMean/SD/%"),
        ("Lab Analysis\nxULN Calc", "Result / ULN\nOutlier flags"),
        ("eDISH\nPlots", "ALT/AST vs\nTBILI scatter"),
        ("Trend\nPlots", "Per-parameter\nmatplotlib"),
        ("HTML\nAssembly", "8 sections +\nappendix"),
    ]
    step_w, step_h = 170, 80
    step_gap = 22
    step_x = 65
    step_y = y4 + 50
    step_ids = []
    for i, (title, sub) in enumerate(steps):
        bx, bid, _ = labeled_box(step_x + i * (step_w + step_gap), step_y,
                                  step_w, step_h, title, sub,
                                  bg=C["white"], stroke="#94a3b8",
                                  title_size=12, sub_size=10)
        elements.extend(bx)
        step_ids.append(bid)

    # Arrows between steps
    for i in range(len(step_ids) - 1):
        ax = step_x + (i + 1) * (step_w + step_gap) - step_gap + 2
        ay = step_y + step_h / 2
        elements.append(arrow(ax, ay, ax + step_gap - 4, ay,
                              color="#94a3b8", sw=2))

    # ══════════════════════════════════════════════════════════════════════
    # ROW 6: OUTPUTS  (y = 1100)
    # ══════════════════════════════════════════════════════════════════════
    y5 = 1100
    elements.append(rect(40, y5, 1220, 140, bg=C["bg_out"], stroke=C["str_out"],
                         sw=2, opacity=40))
    hdr, _ = section_header(40, y5, 1220, "DELIVERABLES", C["bg_out"], C["str_out"])
    elements.extend(hdr)

    out_y = y5 + 50
    out_w, out_h = 260, 70
    out_gap = 30

    outputs = [
        ("HTML Reports (x3)", "JAN30 / FEB24 / MAR20\n~1.6 MB each, self-contained"),
        ("PDF Reports (x3)", "JAN30 / FEB24 / MAR20\n~1.8 MB each, Playwright"),
        ("Safety Reviews (x2)", "Clinician + Biostatistician\nSignal detection reports"),
        ("GitHub Repository", "karunakarAJ/DNLI-I-0001-MMR\n10 commits, fully tracked"),
    ]
    out_ids = []
    ox = 55
    for i, (title, sub) in enumerate(outputs):
        bx, bid, _ = labeled_box(ox + i * (out_w + out_gap), out_y,
                                  out_w, out_h, title, sub,
                                  bg=C["white"], stroke=C["str_out"],
                                  title_size=13, sub_size=10)
        elements.extend(bx)
        out_ids.append(bid)

    # ══════════════════════════════════════════════════════════════════════
    # ROW 7: TOKEN USAGE SUMMARY  (y = 1290)
    # ══════════════════════════════════════════════════════════════════════
    y6 = 1290
    elements.append(rect(40, y6, 1220, 90, bg="#f8fafc", stroke="#cbd5e1",
                         sw=1, ss="dashed", opacity=80))
    elements.append(text(50, y6 + 10, "TOKEN USAGE", size=12,
                         color=C["gray"], w=200, align="left"))

    metrics = [
        "~5.5M input  |  ~1.8M output  |  ~$43.50 est. cost",
        "13 agent invocations  |  250+ tool uses  |  3 sessions  |  100% agent success rate",
    ]
    elements.append(text(200, y6 + 28, metrics[0], size=14,
                         color=C["pri"], w=900, align="center"))
    elements.append(text(200, y6 + 54, metrics[1], size=12,
                         color=C["txt_sub"], w=900, align="center"))

    # ══════════════════════════════════════════════════════════════════════
    # FLOW ARROWS (between phases)
    # ══════════════════════════════════════════════════════════════════════

    # Data Sources -> Phase 1/2
    elements.append(arrow(330, y0 + 130, 330, y1,
                          color=C["arrow_hi"], sw=2))
    elements.append(arrow(970, y0 + 130, 970, y1,
                          color=C["arrow_hi"], sw=2))

    # Phase 1 -> Phase 2
    elements.append(arrow(620, y1 + 95, 680, y1 + 95,
                          color=C["arrow"], sw=2))

    # Phase 1/2 -> Phase 3/4
    elements.append(arrow(330, y1 + 150, 330, y2,
                          color=C["arrow_hi"], sw=2))
    elements.append(arrow(970, y1 + 150, 970, y2,
                          color=C["arrow_hi"], sw=2))

    # Phase 3 -> Phase 4
    elements.append(arrow(620, y2 + 95, 680, y2 + 95,
                          color=C["arrow"], sw=2))

    # Phase 3/4 -> Phase 5/6
    elements.append(arrow(330, y2 + 150, 330, y3,
                          color=C["arrow_hi"], sw=2))
    elements.append(arrow(970, y2 + 150, 970, y3,
                          color=C["arrow_hi"], sw=2))

    # Phase 5 -> Phase 6
    elements.append(arrow(620, y3 + 95, 680, y3 + 95,
                          color=C["arrow"], sw=2))

    # Phase 6 -> Processing Detail
    elements.append(arrow(850, y3 + 150, 850, y4,
                          color=C["arrow"], sw=2, ss="dashed"))

    # Phase 6 / Processing -> Outputs
    elements.append(arrow(650, y4 + 160, 650, y5,
                          color=C["arrow_hi"], sw=3))

    # Data Sources down to Phase 5 (direct data feed)
    elements.append(arrow(1240, y0 + 130, 1280, y0 + 130,
                          color=C["str_data"], sw=1, ss="dashed"))
    # Long vertical on the right side
    elements.append(rect(1275, y0 + 130, 4, y3 - y0 - 60, bg=C["str_data"],
                         stroke=C["str_data"], sw=0, rounded=False, opacity=30))
    elements.append(arrow(1277, y3 + 10, 1260, y3 + 40,
                          color=C["str_data"], sw=1, ss="dashed"))

    # ══════════════════════════════════════════════════════════════════════
    # ANNOTATIONS (side labels)
    # ══════════════════════════════════════════════════════════════════════

    # Left side: Session labels
    elements.append(text(-85, y1 + 50, "Session 1", size=12, color=C["str_expl"],
                         w=100, align="right"))
    elements.append(text(-85, y2 + 50, "Session 1", size=12, color=C["str_impl"],
                         w=100, align="right"))
    elements.append(text(-85, y3 + 50, "Session 2-3", size=12, color=C["str_integ"],
                         w=100, align="right"))

    # Right side: Duration labels
    elements.append(text(1290, y1 + 50, "~4 min", size=12, color=C["txt_sub"],
                         w=80, align="left"))
    elements.append(text(1290, y2 + 50, "~15 min", size=12, color=C["txt_sub"],
                         w=80, align="left"))
    elements.append(text(1290, y3 + 50, "~30 min", size=12, color=C["txt_sub"],
                         w=80, align="left"))

    return elements


def main():
    elements = build()

    doc = {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
        },
        "files": {},
    }

    out_path = Path(__file__).resolve().parent.parent / "docs" / "mmr-pipeline-architecture.excalidraw"
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2)

    print(f"Excalidraw diagram generated: {out_path}")
    print(f"  Elements: {len(elements)}")
    print(f"  File size: {out_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
