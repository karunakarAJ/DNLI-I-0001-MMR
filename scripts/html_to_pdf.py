#!/usr/bin/env python3
"""Convert MMR HTML reports to PDF using Playwright (headless Chromium).

Usage:
    python3 scripts/html_to_pdf.py                          # Convert all reports
    python3 scripts/html_to_pdf.py report/I-0001-MMR-2026MAR20-SafetyOnly.html  # Single file
"""

import sys
import glob
import os
from pathlib import Path


def convert_html_to_pdf(html_path: str, pdf_path: str = None):
    """Convert a single HTML file to PDF."""
    from playwright.sync_api import sync_playwright

    html_path = os.path.abspath(html_path)
    if pdf_path is None:
        pdf_path = html_path.replace('.html', '.pdf')

    print(f"Converting: {os.path.basename(html_path)}")
    print(f"  → {os.path.basename(pdf_path)}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_path}", wait_until="networkidle")
        page.pdf(
            path=pdf_path,
            format="Letter",
            margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"},
            print_background=True,
            scale=0.85,
        )
        browser.close()

    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"  ✓ Generated ({size_mb:.1f} MB)")
    return pdf_path


def main():
    repo_root = Path(__file__).parent.parent
    report_dir = repo_root / "report"

    if len(sys.argv) > 1:
        # Convert specific file(s)
        html_files = sys.argv[1:]
    else:
        # Convert all MMR HTML reports
        html_files = sorted(glob.glob(str(report_dir / "I-0001-MMR-*.html")))
        if not html_files:
            print("No MMR HTML reports found in report/ directory")
            sys.exit(1)

    print(f"PDF Generation — {len(html_files)} file(s)\n")

    pdfs = []
    for html_file in html_files:
        try:
            pdf = convert_html_to_pdf(html_file)
            pdfs.append(pdf)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\nDone: {len(pdfs)}/{len(html_files)} PDFs generated")


if __name__ == "__main__":
    main()
