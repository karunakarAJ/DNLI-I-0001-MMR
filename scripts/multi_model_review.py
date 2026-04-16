#!/usr/bin/env python3
"""
Multi-Model Safety Review Agents for DNLI-I-0001 MMR.

Launches parallel review agents using both Claude (Anthropic) and GPT (OpenAI)
to provide independent safety assessments. Each agent reviews the same report
from a different perspective, and a final consensus report synthesizes findings.

Architecture:
    ┌──────────────────────────────────────────────────────┐
    │  Report HTML → Extract text sections → Build prompts │
    └──────────┬───────────────────────────┬───────────────┘
               │                           │
    ┌──────────▼──────────┐     ┌──────────▼──────────┐
    │   Claude Agents     │     │    GPT Agents        │
    │  ┌───────────────┐  │     │  ┌───────────────┐   │
    │  │ Clinician     │  │     │  │ Clinician     │   │
    │  │ (claude-sonnet)│  │     │  │ (gpt-4o)      │   │
    │  ├───────────────┤  │     │  ├───────────────┤   │
    │  │ Biostatistician│  │     │  │ Patient Safety│   │
    │  │ (claude-sonnet)│  │     │  │ (gpt-4o)      │   │
    │  ├───────────────┤  │     │  ├───────────────┤   │
    │  │ Visual Review │  │     │  │ Visual Review │   │
    │  │ (claude-sonnet)│  │     │  │ (gpt-4o)      │   │
    │  └───────────────┘  │     │  └───────────────┘   │
    └──────────┬──────────┘     └──────────┬───────────┘
               │                           │
    ┌──────────▼───────────────────────────▼───────────────┐
    │         Consensus Synthesizer (Claude Opus)          │
    │   Merges findings, resolves disagreements, produces  │
    │   final safety signal report with confidence levels  │
    └──────────────────────────────────────────────────────┘

Usage:
    # Set API keys as environment variables:
    export ANTHROPIC_API_KEY="sk-ant-..."
    export OPENAI_API_KEY="sk-..."

    # Run all agents:
    python3 scripts/multi_model_review.py report/I-0001-Medical-Monitoring-Report-2026MAR20-SafetyOnly.html

    # Run specific agents only:
    python3 scripts/multi_model_review.py report/...html --agents clinician,biostat

    # Use specific models:
    python3 scripts/multi_model_review.py report/...html --claude-model claude-sonnet-4-20250514 --gpt-model gpt-4o

Dependencies:
    pip install anthropic openai beautifulsoup4 pyyaml
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Configuration ────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

# Default models
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-20250514"
DEFAULT_GPT_MODEL = "gpt-4o"
CONSENSUS_MODEL = "claude-sonnet-4-20250514"  # For final synthesis

# Agent definitions: (agent_id, role, provider, description)
AGENT_REGISTRY = {
    "clinician_claude": {
        "role": "Clinician Safety Reviewer",
        "provider": "anthropic",
        "persona": "Medical Monitor / Clinical Safety Physician with 15+ years in rare disease clinical trials",
        "focus": [
            "AE/SAE pattern recognition and emerging safety signals",
            "IRR severity trends and management adequacy",
            "Hepatotoxicity screening (eDISH validation)",
            "ECG safety (QTcF prolongation clinical significance)",
            "Dose-response safety relationships",
            "ADA-immunogenicity and safety correlations",
            "Overall benefit-risk assessment for pediatric MPS IIIA",
        ],
    },
    "clinician_gpt": {
        "role": "Clinician Safety Reviewer",
        "provider": "openai",
        "persona": "Pediatric Neurologist specializing in lysosomal storage disorders and enzyme replacement therapies",
        "focus": [
            "Disease-specific AE interpretation (MPS IIIA natural history vs drug effect)",
            "Pediatric dosing safety across weight ranges",
            "Neurodevelopmental safety markers",
            "IRR management in pediatric populations",
            "Comparison to other ERT safety profiles (e.g., Elaprase, Aldurazyme)",
            "Long-term developmental safety considerations",
        ],
    },
    "biostat_claude": {
        "role": "Safety Biostatistician",
        "provider": "anthropic",
        "persona": "Senior Biostatistician with expertise in small-sample rare disease trials and Bayesian safety monitoring",
        "focus": [
            "Small sample size statistical limitations (N=20, cohorts N=2-10)",
            "Exact binomial confidence intervals for key safety rates",
            "Exposure-adjusted incidence rate calculations",
            "Time-to-event patterns (IRR, SAE onset)",
            "eDISH computational validation",
            "Missing data patterns and informative censoring",
            "Synthetic data quality assessment (ECG/VS plots)",
        ],
    },
    "patient_safety_gpt": {
        "role": "Patient Safety Officer",
        "provider": "openai",
        "persona": "Patient Safety and Risk Management specialist with pediatric rare disease expertise",
        "focus": [
            "Individual patient risk stratification (all 20 participants)",
            "Pediatric-specific safety concerns and caregiver impact",
            "IRR management protocol adequacy",
            "Informed consent and caregiver communication",
            "Protocol safeguards (stopping rules, DSMB/DEC oversight)",
            "Site-to-site safety variation analysis",
            "Long-term ADA/immunogenicity implications",
        ],
    },
    "visual_claude": {
        "role": "Data Visualization Reviewer",
        "provider": "anthropic",
        "persona": "Clinical Data Visualization specialist ensuring regulatory-quality figures for safety reporting",
        "focus": [
            "Figure quality assessment (all 17+ embedded plots)",
            "Color accessibility (colorblind-safe palettes)",
            "Axis labeling, legend clarity, reference line visibility",
            "Clinical data presentation standards (ICH E3/E6)",
            "Consistency across figure types",
            "Synthetic data realism (ECG/VS patterns)",
        ],
    },
    "visual_gpt": {
        "role": "Data Visualization Reviewer",
        "provider": "openai",
        "persona": "Regulatory Medical Writing and Visualization expert with FDA/EMA submission experience",
        "focus": [
            "Regulatory compliance of figures (FDA guidance on safety reporting)",
            "Figure-table concordance (do plots match tabular data?)",
            "Clinical relevance of visualization choices",
            "Missing visualizations that should be included",
            "Publication-quality assessment",
        ],
    },
}

# ── Report Text Extraction ───────────────────────────────────────────────

def extract_report_text(html_path: str) -> dict:
    """Extract structured text from the MMR HTML report, removing base64 images."""
    from bs4 import BeautifulSoup

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Remove all img tags (base64 encoded, too large for API)
    for img in soup.find_all("img"):
        alt = img.get("alt", "")
        img.replace_with(f"[FIGURE: {alt}]")

    # Remove style tags
    for style in soup.find_all("style"):
        style.decompose()

    sections = {}
    current_section = "cover"
    current_text = []

    for elem in soup.body.children if soup.body else []:
        text = elem.get_text(strip=True, separator=" ") if hasattr(elem, "get_text") else str(elem).strip()
        if not text:
            continue

        # Detect section boundaries
        if hasattr(elem, "find"):
            h2 = elem.find("h2")
            if h2:
                # Save previous section
                if current_text:
                    sections[current_section] = "\n".join(current_text)
                section_title = h2.get_text(strip=True)
                current_section = section_title
                current_text = [text]
                continue

        current_text.append(text)

    if current_text:
        sections[current_section] = "\n".join(current_text)

    return sections


def build_report_summary(sections: dict, max_chars: int = 60000) -> str:
    """Build a condensed report summary that fits within token limits."""
    parts = []
    total = 0

    for section_name, content in sections.items():
        # Truncate long sections
        max_per_section = max_chars // max(len(sections), 1)
        truncated = content[:max_per_section]
        if len(content) > max_per_section:
            truncated += f"\n[... truncated {len(content) - max_per_section} chars ...]"

        parts.append(f"=== {section_name} ===\n{truncated}\n")
        total += len(truncated)

    return "\n".join(parts)


# ── Prompt Templates ─────────────────────────────────────────────────────

def build_agent_prompt(agent_config: dict, report_summary: str, study_context: str) -> str:
    """Build the full prompt for a review agent."""
    focus_items = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(agent_config["focus"]))

    return f"""You are a {agent_config['role']}.

**Your persona:** {agent_config['persona']}

**Study Context:**
{study_context}

**Your specific focus areas:**
{focus_items}

**Instructions:**
1. Review the MMR report content below thoroughly
2. Identify safety signals, data quality issues, and areas of concern
3. Provide actionable recommendations
4. Rate each finding as CRITICAL / HIGH / MEDIUM / LOW priority
5. State your confidence level (HIGH / MODERATE / LOW) for each finding

**Report Content:**
{report_summary}

**Output Format:**
Provide your review as structured markdown with:

# {agent_config['role']} — Safety Review

## Executive Summary
[2-3 sentence overall assessment with benefit-risk conclusion]

## Findings

### [Finding Title]
- **Priority:** [CRITICAL/HIGH/MEDIUM/LOW]
- **Confidence:** [HIGH/MODERATE/LOW]
- **Section(s):** [Which report section(s)]
- **Description:** [Detailed finding]
- **Recommendation:** [Specific action item]

[Repeat for each finding — aim for 8-15 findings]

## Risk Assessment Matrix
| Domain | Risk Level | Key Signal | Action Required |
|--------|-----------|------------|-----------------|
[Fill in for each safety domain]

## Summary Recommendations
[Numbered list of top 5 recommendations, most critical first]
"""


STUDY_CONTEXT = """
Study: DNLI-I-0001 | Drug: DNL-126 (ETV:SGSH-BioM) | Phase 1/2
Indication: MPS IIIA (Sanfilippo Syndrome Type A) — rare pediatric lysosomal storage disorder
Population: N=20 pediatric patients (mean age 64 months, range 27-198 months), 65% female, 95% White
Protocol: Version 6 (26-Aug-2025) | Data Cut: 2026-02-25 (EDC)

Cohorts:
  A1 (N=4): 3 mg/kg QW Wks 1-2 → 10 mg/kg Q2W (longest exposure ~97 wks)
  A2 (N=4): 3 mg/kg QW → escalate 3→6→10 mg/kg
  A3 (N=10): 3 mg/kg QW ×6 → 6 mg/kg QW ×6 → 10 mg/kg QW (newest cohort ~25-45 wks)
  B1 (N=2): Same as A3

Key Safety Signals:
  - IRR: 100% incidence (442 cumulative events); 75% moderate-severe; 1 anaphylactic reaction (B1)
  - SAEs: 15 events in 13/20 participants; 1 drug-related (Grade 3 IRR, participant 0017-9004)
  - ADA: 19/20 (95%) ADA-positive; 12/20 (60%) neutralizing antibodies
  - Hepatotoxicity: 0/20 in Hy's Law quadrant (eDISH clean)
  - ECG: QTcF >450ms in 3/20 (single observations, IRR-related)
  - Vitals: SpO2 <92% in 2/20; Temperature >38.5°C in 16/20 (80%)

Sites: UNC Chapel Hill (N=8), UCSF (N=5), U Iowa (N=4), Baylor/TCH (N=3)
"""


# ── API Callers ──────────────────────────────────────────────────────────

async def call_anthropic(prompt: str, model: str, agent_id: str) -> dict:
    """Call Anthropic Claude API."""
    import anthropic

    client = anthropic.AsyncAnthropic()  # Uses ANTHROPIC_API_KEY env var

    start = time.time()
    try:
        response = await client.messages.create(
            model=model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
        elapsed = time.time() - start
        text = response.content[0].text
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
        return {
            "agent_id": agent_id,
            "provider": "anthropic",
            "model": model,
            "status": "success",
            "content": text,
            "usage": usage,
            "elapsed_seconds": round(elapsed, 1),
        }
    except Exception as e:
        return {
            "agent_id": agent_id,
            "provider": "anthropic",
            "model": model,
            "status": "error",
            "content": str(e),
            "usage": {},
            "elapsed_seconds": round(time.time() - start, 1),
        }


async def call_openai(prompt: str, model: str, agent_id: str) -> dict:
    """Call OpenAI GPT API."""
    import openai

    client = openai.AsyncOpenAI()  # Uses OPENAI_API_KEY env var

    start = time.time()
    try:
        response = await client.chat.completions.create(
            model=model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
        elapsed = time.time() - start
        text = response.choices[0].message.content
        usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
        }
        return {
            "agent_id": agent_id,
            "provider": "openai",
            "model": model,
            "status": "success",
            "content": text,
            "usage": usage,
            "elapsed_seconds": round(elapsed, 1),
        }
    except Exception as e:
        return {
            "agent_id": agent_id,
            "provider": "openai",
            "model": model,
            "status": "error",
            "content": str(e),
            "usage": {},
            "elapsed_seconds": round(time.time() - start, 1),
        }


# ── Consensus Synthesis ──────────────────────────────────────────────────

async def synthesize_consensus(results: list, model: str) -> dict:
    """Use Claude to synthesize a consensus report from all agent reviews."""

    reviews_text = ""
    for r in results:
        if r["status"] == "success":
            agent_cfg = AGENT_REGISTRY.get(r["agent_id"], {})
            reviews_text += f"\n\n{'='*60}\n"
            reviews_text += f"AGENT: {r['agent_id']} ({agent_cfg.get('role', 'Unknown')}) — {r['provider']}/{r['model']}\n"
            reviews_text += f"{'='*60}\n"
            reviews_text += r["content"]

    prompt = f"""You are the **Consensus Safety Synthesizer** for a multi-model safety review of clinical study DNLI-I-0001.

Multiple AI agents (both Claude and GPT models) have independently reviewed the same Medical Monitoring Report from different perspectives. Your job is to:

1. **Identify areas of agreement** — findings that multiple agents flagged (high confidence)
2. **Identify areas of disagreement** — findings where agents differ (investigate why)
3. **Resolve conflicts** — use clinical judgment to determine which assessment is more appropriate
4. **Synthesize a unified safety assessment** — combining the best insights from all agents
5. **Flag any blind spots** — safety concerns that NO agent identified

**Study Context:**
{STUDY_CONTEXT}

**Agent Reviews:**
{reviews_text}

**Output Format:**

# Consensus Safety Review — DNLI-I-0001 MMR
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Models Used:** [list all models]
**Agents:** [list all agent roles]

## Cross-Agent Agreement Matrix
| Safety Domain | Claude Clinician | GPT Clinician | Claude Biostat | GPT Patient Safety | Claude Visual | GPT Visual | Consensus |
|...|

## High-Confidence Findings (≥2 agents agree)
[Numbered list with priority ratings]

## Divergent Findings (agents disagree)
[For each: what the disagreement is, why, and your resolution]

## Unified Risk Assessment
| Domain | Risk Level | Confidence | Evidence | Action |
|...|

## Top 10 Recommendations (Priority-Ordered)
[Specific, actionable items]

## Blind Spot Analysis
[Safety concerns that may have been missed]

## Model Performance Notes
[Any observations about differences between Claude and GPT assessments]
"""

    return await call_anthropic(prompt, model, "consensus_synthesizer")


# ── Main Pipeline ────────────────────────────────────────────────────────

async def run_review_pipeline(
    html_path: str,
    agents: Optional[list] = None,
    claude_model: str = DEFAULT_CLAUDE_MODEL,
    gpt_model: str = DEFAULT_GPT_MODEL,
    skip_consensus: bool = False,
):
    """Run the full multi-model review pipeline."""

    print(f"\n{'='*70}")
    print(f"  Multi-Model Safety Review — DNLI-I-0001 MMR")
    print(f"  Report: {html_path}")
    print(f"  Claude Model: {claude_model}")
    print(f"  GPT Model:    {gpt_model}")
    print(f"  Timestamp:    {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

    # 1. Extract report text
    print("Step 1: Extracting report text...")
    sections = extract_report_text(html_path)
    report_summary = build_report_summary(sections)
    print(f"  Extracted {len(sections)} sections, {len(report_summary):,} chars total\n")

    # 2. Determine which agents to run
    if agents:
        active_agents = {k: v for k, v in AGENT_REGISTRY.items()
                        if any(a in k for a in agents)}
    else:
        active_agents = AGENT_REGISTRY

    print(f"Step 2: Launching {len(active_agents)} review agents in parallel...\n")

    # 3. Build and launch all agents concurrently
    tasks = []
    for agent_id, agent_config in active_agents.items():
        prompt = build_agent_prompt(agent_config, report_summary, STUDY_CONTEXT)
        model = claude_model if agent_config["provider"] == "anthropic" else gpt_model

        print(f"  → {agent_id}: {agent_config['role']} ({agent_config['provider']}/{model})")

        if agent_config["provider"] == "anthropic":
            tasks.append(call_anthropic(prompt, model, agent_id))
        else:
            tasks.append(call_openai(prompt, model, agent_id))

    # 4. Await all results
    print(f"\n  Waiting for {len(tasks)} agents to complete...\n")
    results = await asyncio.gather(*tasks)

    # 5. Print results summary
    print(f"\n{'='*70}")
    print("  Agent Results Summary")
    print(f"{'='*70}")

    total_input = 0
    total_output = 0
    output_dir = BASE_DIR / "docs"
    output_dir.mkdir(exist_ok=True)

    for r in results:
        status_icon = "✓" if r["status"] == "success" else "✗"
        tokens_str = ""
        if r["usage"]:
            inp = r["usage"].get("input_tokens", 0)
            out = r["usage"].get("output_tokens", 0)
            total_input += inp
            total_output += out
            tokens_str = f" | {inp:,} in / {out:,} out"

        print(f"  {status_icon} {r['agent_id']:25s} ({r['provider']:9s}/{r['model']:25s}) "
              f"{r['elapsed_seconds']:5.1f}s{tokens_str}")

        # Write individual review to docs/
        if r["status"] == "success":
            fname = f"{r['agent_id']}-review.md"
            fpath = output_dir / fname
            header = (
                f"# {AGENT_REGISTRY[r['agent_id']]['role']} — {r['agent_id']}\n\n"
                f"**Model:** {r['provider']}/{r['model']}  \n"
                f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n"
                f"**Tokens:** {r['usage'].get('input_tokens', '?')} input / "
                f"{r['usage'].get('output_tokens', '?')} output  \n"
                f"**Duration:** {r['elapsed_seconds']}s  \n\n---\n\n"
            )
            fpath.write_text(header + r["content"], encoding="utf-8")
            print(f"    → Saved: {fpath}")

    # 6. Consensus synthesis
    consensus_result = None
    if not skip_consensus and len([r for r in results if r["status"] == "success"]) >= 2:
        print(f"\nStep 3: Running consensus synthesis ({CONSENSUS_MODEL})...")
        consensus_result = await synthesize_consensus(results, CONSENSUS_MODEL)

        if consensus_result["status"] == "success":
            fpath = output_dir / "consensus-safety-review.md"
            header = (
                f"# Consensus Safety Review — Multi-Model\n\n"
                f"**Synthesizer Model:** {CONSENSUS_MODEL}  \n"
                f"**Date:** {datetime.now().strftime('%Y-%m-%d')}  \n"
                f"**Agents Synthesized:** {len([r for r in results if r['status'] == 'success'])}  \n"
                f"**Tokens:** {consensus_result['usage'].get('input_tokens', '?')} input / "
                f"{consensus_result['usage'].get('output_tokens', '?')} output  \n\n---\n\n"
            )
            fpath.write_text(header + consensus_result["content"], encoding="utf-8")
            print(f"  ✓ Consensus saved: {fpath}")

            total_input += consensus_result["usage"].get("input_tokens", 0)
            total_output += consensus_result["usage"].get("output_tokens", 0)
        else:
            print(f"  ✗ Consensus failed: {consensus_result['content']}")

    # 7. Cost estimate
    print(f"\n{'='*70}")
    print("  Token Usage & Cost Estimate")
    print(f"{'='*70}")
    print(f"  Total input tokens:  {total_input:>10,}")
    print(f"  Total output tokens: {total_output:>10,}")

    # Cost estimates (approximate)
    claude_input = sum(r["usage"].get("input_tokens", 0) for r in results
                      if r["status"] == "success" and r["provider"] == "anthropic")
    claude_output = sum(r["usage"].get("output_tokens", 0) for r in results
                       if r["status"] == "success" and r["provider"] == "anthropic")
    gpt_input = sum(r["usage"].get("input_tokens", 0) for r in results
                   if r["status"] == "success" and r["provider"] == "openai")
    gpt_output = sum(r["usage"].get("output_tokens", 0) for r in results
                    if r["status"] == "success" and r["provider"] == "openai")

    if consensus_result and consensus_result["status"] == "success":
        claude_input += consensus_result["usage"].get("input_tokens", 0)
        claude_output += consensus_result["usage"].get("output_tokens", 0)

    # Pricing: Claude Sonnet $3/$15 per MTok; GPT-4o $2.50/$10 per MTok
    claude_cost = (claude_input * 3 + claude_output * 15) / 1_000_000
    gpt_cost = (gpt_input * 2.5 + gpt_output * 10) / 1_000_000
    total_cost = claude_cost + gpt_cost

    print(f"\n  Claude ({claude_model}): ~${claude_cost:.2f}")
    print(f"  GPT    ({gpt_model}):    ~${gpt_cost:.2f}")
    print(f"  Total estimated cost:    ~${total_cost:.2f}")

    # 8. Write metadata
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "report": html_path,
        "models": {"claude": claude_model, "gpt": gpt_model, "consensus": CONSENSUS_MODEL},
        "agents": {r["agent_id"]: {
            "provider": r["provider"],
            "model": r["model"],
            "status": r["status"],
            "tokens": r["usage"],
            "elapsed_seconds": r["elapsed_seconds"],
        } for r in results},
        "totals": {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "estimated_cost_usd": round(total_cost, 2),
        },
    }
    if consensus_result:
        metadata["consensus"] = {
            "status": consensus_result["status"],
            "tokens": consensus_result["usage"],
            "elapsed_seconds": consensus_result["elapsed_seconds"],
        }

    meta_path = output_dir / "multi-model-review-metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"\n  Metadata: {meta_path}")

    print(f"\n{'='*70}")
    print(f"  Review complete. {len([r for r in results if r['status'] == 'success'])}/{len(results)} agents succeeded.")
    print(f"  Output directory: {output_dir}/")
    print(f"{'='*70}\n")

    return results, consensus_result


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Multi-Model Safety Review for DNLI-I-0001 MMR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/multi_model_review.py report/I-0001-Medical-Monitoring-Report-2026MAR20-SafetyOnly.html
  python3 scripts/multi_model_review.py report/...html --agents clinician,biostat
  python3 scripts/multi_model_review.py report/...html --claude-model claude-sonnet-4-20250514 --gpt-model gpt-4o
  python3 scripts/multi_model_review.py report/...html --skip-consensus
        """,
    )
    parser.add_argument("report", help="Path to the HTML MMR report")
    parser.add_argument("--agents", help="Comma-separated agent filter (e.g., clinician,biostat,visual,patient)")
    parser.add_argument("--claude-model", default=DEFAULT_CLAUDE_MODEL, help=f"Claude model (default: {DEFAULT_CLAUDE_MODEL})")
    parser.add_argument("--gpt-model", default=DEFAULT_GPT_MODEL, help=f"GPT model (default: {DEFAULT_GPT_MODEL})")
    parser.add_argument("--skip-consensus", action="store_true", help="Skip consensus synthesis step")

    args = parser.parse_args()

    # Validate API keys
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Export it before running.")
        sys.exit(1)
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set. Export it before running.")
        sys.exit(1)

    # Validate report exists
    if not Path(args.report).exists():
        print(f"ERROR: Report not found: {args.report}")
        sys.exit(1)

    agent_filter = args.agents.split(",") if args.agents else None

    asyncio.run(run_review_pipeline(
        html_path=args.report,
        agents=agent_filter,
        claude_model=args.claude_model,
        gpt_model=args.gpt_model,
        skip_consensus=args.skip_consensus,
    ))


if __name__ == "__main__":
    main()
