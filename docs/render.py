"""
render.py -- HTML -> PDF with headless Chromium (Playwright).

Usage:  python docs/render.py docs/report.html Assignment2_Divide_and_Conquer_Analysis.pdf

Page numbers are added by Chromium's header template (APA 7 student paper:
page number flush right in the header on every page, including the title page).
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HEADER = """
<div style="width:100%; font-family:'Times New Roman', Times, serif; font-size:12pt;
            padding:0 1in; box-sizing:border-box; text-align:right; margin-top:0.5in;">
  <span class="pageNumber"></span>
</div>"""
FOOTER = "<div></div>"


def render(src: str, dst: str) -> None:
    html = Path(src).resolve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html.as_uri())
        page.wait_for_load_state("networkidle")
        page.pdf(path=dst, format="Letter", print_background=True,
                 display_header_footer=True, header_template=HEADER, footer_template=FOOTER,
                 margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"})
        browser.close()
    print("wrote", dst)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
