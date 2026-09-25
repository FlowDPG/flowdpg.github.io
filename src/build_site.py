"""Fill src/template.html -> index.html (charts, rubric tables, BibTeX).  Run from anywhere: python3 src/build_site.py"""
import os, re
from html import escape
from PIL import Image
from charts import CHARTS

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)                       # site root (index.html, static/, video/)

BIBTEX = """@inproceedings{shi2026flowdpg,
  title     = {FlowDPG: Deterministic Policy Gradient on Flow Matching Policies
               for Real-World Manipulation},
  author    = {Shi, Kexin and Shi, Junyao and Hebbar, Poorvi and Zhao, Zhuolun and
               Amarnath, Tarun and Su, Yifan and Bahl, Shikhar and Pathak, Deepak},
  booktitle = {Conference on Robot Learning (CoRL)},
  year      = {2026}
}"""


def rubrics():
    bodies = [open(os.path.join(SRC, "data", f)).read().strip() for f in ("rubrics_airpods.html", "rubrics_eggs.html")]
    head = ('<thead><tr><th style="width:17%">Stage</th><th>3 &ndash; Successful</th><th>2 &ndash; Minor error</th>'
            '<th>1 &ndash; Major error</th><th>0 &ndash; Failed</th></tr></thead>')
    rows = [re.sub(r"\s+<tr>", "\n          <tr>", b.strip()) for b in bodies]
    return (f'<h4>AirPods assembly (Franka) &middot; 8 stages, 24 points</h4>\n'
            f'<div class="tablewrap"><table class="rub">{head}<tbody>\n          {rows[0]}\n</tbody></table></div>\n'
            f'<h4>Scrambled eggs (YAM) &middot; 14 stages, 42 points</h4>\n'
            f'<p class="note" style="margin:0 0 8px">Pick up and crack occur twice, once per egg: 14 scored stages from 12 types.</p>\n'
            f'<div class="tablewrap"><table class="rub">{head}<tbody>\n          {rows[1]}\n</tbody></table></div>')


def main():
    html = open(os.path.join(SRC, "template.html")).read()
    for k, fn in CHARTS.items():
        html = html.replace("{{" + k + "}}", fn())
    html = html.replace("{{rubrics}}", rubrics()).replace("{{bibtex}}", escape(BIBTEX))
    # true pixel sizes on <img> (prevents layout shift)
    for name in ("egg_setup.jpg", "airpods_setup.jpg"):
        w, h = Image.open(os.path.join(ROOT, "static/images", name)).size
        html = re.sub(rf'(src="static/images/{re.escape(name)}"[^>]*?)width="\d+" height="\d+"',
                      rf'\1width="{w}" height="{h}"', html)
    left = re.findall(r"\{\{\w+\}\}", html)
    assert not left, left
    open(os.path.join(ROOT, "index.html"), "w").write(html)
    print("index.html", len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
