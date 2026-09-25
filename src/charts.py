"""Charts for the FlowDPG project page, in the paper's palette (paperstyle.py / Fig. 2).

Vertical bars and line panels are inline SVG; horizontal bars and the heatmap are HTML so their
text stays readable on phones. Every animated element starts collapsed under `.js [data-anim]`
and grows when flowdpg.js adds `.in` as the chart scrolls into view."""
import json, os
from decimal import Decimal, ROUND_HALF_UP
from html import escape

INK, INK2, MUTED = "#1d1c1a", "#55534e", "#8d8a83"
CARD, AXIS = "#f5f4ed", "#cdc9c0"
BLUE, BLUE_T = "#4a86c0", "#a9cbe8"
TERRA, TERRA_T = "#df7445", "#f2b592"
GREEN, PLUM, BC_GRAY = "#6aa84f", "#94508c", "#cdc9c0"
BLUE_SEQ = ["#eef4f9", "#d6e6f3", "#b7d3eb", "#95bfe1", "#73a9d5", "#5591c6", "#3f79b0"]


def rnd(v, nd):
    q = Decimal("1") if nd == 0 else Decimal("1." + "0" * nd)
    return str(Decimal(str(v)).quantize(q, rounding=ROUND_HALF_UP))


def bar_path(x, y0, w, h, r=4):
    """Bar anchored at baseline y0 growing up by h, rounded data end only."""
    r = min(r, w / 2, h)
    y = y0 - h
    return (f"M{x:.1f},{y0:.1f}V{y + r:.1f}Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f}"
            f"H{x + w - r:.1f}Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f}V{y0:.1f}Z")


# ------------------------------------------------------------------ repeated evaluation (3 panels)
REPEATED = [
    ("AirPods · overall success (%)", 0, [
        ("BC", [("BC", 62.0, 6.5, BC_GRAY)]),
        ("QAM", [("QAM offline", 78.0, 5.5, BLUE_T), ("QAM +online", 80.0, 5.3, BLUE)]),
        ("FlowDPG", [("FlowDPG offline", 86.0, 4.6, TERRA_T), ("FlowDPG +online", 90.0, 3.9, TERRA)])]),
    ("AirPods · rubric score (%)", 1, [
        ("BC", [("BC", 66.58, 3.57, BC_GRAY)]),
        ("QAM", [("QAM offline", 79.42, 2.96, BLUE_T), ("QAM +online", 81.42, 2.88, BLUE)]),
        ("FlowDPG", [("FlowDPG offline", 88.17, 2.41, TERRA_T), ("FlowDPG +online", 92.25, 2.04, TERRA)])]),
    ("Eggs · rubric score (%), offline", 1, [
        ("BC", [("BC", 64.24, 3.81, BC_GRAY)]),
        ("QAM", [("QAM offline", 76.90, 3.12, BLUE_T)]),
        ("FlowDPG", [("FlowDPG offline", 85.76, 2.67, TERRA_T)])]),
]


def repeated_panel(title, nd, groups):
    Wv, Hv = 340, 262
    x0, x1, yb, yt = 40, 332, 226, 18
    Y = lambda v: yb - (yb - yt) * v / 100
    o = [f'<svg class="chart" viewBox="0 0 {Wv} {Hv}" role="img" aria-label="{escape(title)}">']
    for g in (0, 25, 50, 75, 100):
        o.append(f'<line class="gl" x1="{x0}" x2="{x1}" y1="{Y(g):.1f}" y2="{Y(g):.1f}"/>')
        o.append(f'<text class="yt" x="{x0 - 7}" y="{Y(g) + 4:.1f}">{g}</text>')
    gw = (x1 - x0) / 3
    bw, gap = 34, 5
    k = 0
    for gi, (gname, bars) in enumerate(groups):
        cx = x0 + gw * (gi + 0.5)
        tot = len(bars) * bw + (len(bars) - 1) * gap
        for bi, (lab, v, se, col) in enumerate(bars):
            x = cx - tot / 2 + bi * (bw + gap)
            d = 0.08 + 0.12 * k
            k += 1
            val = rnd(v, nd)
            tip = f'{lab}|{val} ± {rnd(se, nd if nd else 1)}'
            o.append(f'<g class="bw" data-tip="{escape(tip)}">')
            o.append(f'<path class="bar v" style="--d:{d:.2f}s" fill="{col}" d="{bar_path(x, yb, bw, yb - Y(v))}"/>')
            ex = x + bw / 2
            o.append(f'<g class="err" style="--d:{d + 0.75:.2f}s"><line x1="{ex:.1f}" x2="{ex:.1f}" y1="{Y(v - se):.1f}" y2="{Y(v + se):.1f}"/>'
                     f'<line x1="{ex - 4:.1f}" x2="{ex + 4:.1f}" y1="{Y(v - se):.1f}" y2="{Y(v - se):.1f}"/>'
                     f'<line x1="{ex - 4:.1f}" x2="{ex + 4:.1f}" y1="{Y(v + se):.1f}" y2="{Y(v + se):.1f}"/></g>')
            strong = " strong" if col == TERRA or (col == TERRA_T and len(bars) == 1) else ""
            o.append(f'<text class="val{strong}" style="--d:{d + 0.75:.2f}s" x="{ex:.1f}" y="{Y(v + se) - 6:.1f}" '
                     f'data-v="{v}" data-dec="{nd}">{val}</text>')
            o.append(f'<rect class="hit" x="{x - 2:.1f}" y="{yt}" width="{bw + 4}" height="{yb - yt}"/></g>')
        o.append(f'<text class="xt{" b" if gname == "FlowDPG" else ""}" x="{cx:.1f}" y="{yb + 22}">{gname}</text>')
    o.append(f'<line class="ax" x1="{x0}" x2="{x1}" y1="{yb}" y2="{yb}"/></svg>')
    return (f'<figure class="card chart-card" data-anim><figcaption class="cc-title">{escape(title)}</figcaption>'
            + "".join(o) + "</figure>")


def repeated():
    legend = [("BC", BC_GRAY), ("QAM offline", BLUE_T), ("QAM +online", BLUE),
              ("FlowDPG offline", TERRA_T), ("FlowDPG +online", TERRA)]
    lg = "".join(f'<span><i style="background:{c}"></i>{escape(n)}</span>' for n, c in legend)
    return (f'<div class="legend">{lg}<span class="lg-note">error bars: s.e. over 5 checkpoints</span></div>'
            f'<div class="grid3">{"".join(repeated_panel(*p) for p in REPEATED)}</div>')


# ------------------------------------------------------------------ horizontal bars (HTML)
def axis_row(ticks=(0, 20, 40, 60, 80, 100), label=""):
    t = "".join(f'<span style="left:{v}%">{v}</span>' for v in ticks)
    return f'<div class="hb-axis"><span class="hb-axis-lab">{escape(label)}</span><div class="hb-ticks">{t}</div></div>'


SWEEP = [
    (None, [("BC (base)", 64, BC_GRAY)]),
    ("Value-conditioning", [("RA-BC", 76, GREEN), ("AWR", 76, GREEN), ("RECAP", 72, GREEN)]),
    ("Auxiliary module", [("DSRL", 68, PLUM), ("PLD", 76, PLUM), ("RLT", 80, PLUM)]),
    ("Adjoint critic gradient", [("QAM", 80, BLUE)]),
    ("Ours", [("FlowDPG (offline)", 88, TERRA_T), ("FlowDPG (+online)", 92, TERRA)]),
]


def sweep():
    rows, k = [], 0
    for fam, items in SWEEP:
        body = []
        for lab, v, col in items:
            d = 0.05 + 0.09 * k
            k += 1
            ours = "FlowDPG" in lab
            body.append(
                f'<div class="hb-row" data-tip="{escape(lab)}|{v}%"><span class="hb-lab{" b" if ours else ""}">{escape(lab)}</span>'
                f'<span class="hb-track"><span class="hb-ref" style="left:64%"></span>'
                f'<span class="hb-bar" style="--w:{v}%;--c:{col};--d:{d:.2f}s"></span>'
                f'<span class="hb-val{" b" if ours else ""}" style="left:{v}%;--d:{d + 0.7:.2f}s" data-v="{v}" data-dec="0" data-suf="%">{v}%</span>'
                f'</span></div>')
        famlab = f'<div class="hb-fam">{escape(fam)}</div>' if fam else '<div class="hb-fam"></div>'
        rows.append(f'<div class="hb-group">{famlab}<div class="hb-rows">{"".join(body)}</div></div>')
    return (f'<div class="card hbars sweep" data-anim>{"".join(rows)}'
            f'{axis_row(label="End-to-end success (%)")}'
            f'<div class="hb-refkey"><i></i>BC base (64%)</div></div>')


DISTURB = [("Re-grasp", "object put back in the tray", 78, 92),
           ("Re-open / close", "case state inverted", 82, 94),
           ("Re-insert", "pod dislodged", 86, 92),
           ("Adapt grasp", "tray reshuffled mid-reach", 70, 88)]


def disturb():
    rows = []
    for k, (nm, sub, off, on) in enumerate(DISTURB):
        d = 0.1 + 0.15 * k
        rows.append(
            f'<div class="db-row"><div class="db-lab"><b>{escape(nm)}</b><span>{escape(sub)}</span></div>'
            f'<div class="db-bars">'
            f'<div class="db-line" data-tip="{escape(nm)} · offline|{off}%"><span class="hb-bar" style="--w:{off}%;--c:{TERRA_T};--d:{d:.2f}s"></span>'
            f'<span class="hb-val" style="left:{off}%;--d:{d + 0.7:.2f}s" data-v="{off}" data-dec="0">{off}</span></div>'
            f'<div class="db-line" data-tip="{escape(nm)} · +online|{on}%"><span class="hb-bar" style="--w:{on}%;--c:{TERRA};--d:{d + 0.9:.2f}s"></span>'
            f'<span class="hb-val b" style="left:{on}%;--d:{d + 1.6:.2f}s" data-v="{on}" data-dec="0">{on}</span></div>'
            f'</div><div class="db-delta{" big" if on - off == max(b - a for *_, a, b in DISTURB) else ""}" style="--d:{d + 1.8:.2f}s">+{on - off}</div></div>')
    lg = (f'<div class="legend left"><span><i style="background:{TERRA_T}"></i>offline</span>'
          f'<span><i style="background:{TERRA}"></i>+online</span><span class="lg-note">recovery rate (%), 50 trials each</span></div>')
    return f'<div class="card dbars" data-anim>{lg}{"".join(rows)}</div>'


# ------------------------------------------------------------------ reward ablation heatmap (HTML grid)
HM_ROWS = ["Full reward", "w/o progress", "w/o stage transition", "Only terminal"]
HM_COLS = ["Grasp case", "Open case", "Grasp R pod", "Insert R pod", "Grasp L pod", "Insert L pod", "Close case", "Place case"]
HM = [[100, 96, 96, 96, 96, 92, 92, 92], [100, 96, 92, 88, 84, 84, 80, 80],
      [100, 96, 92, 88, 84, 80, 76, 76], [100, 80, 76, 72, 68, 64, 60, 60]]


def _hex(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _lum(rgb):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0] / 255) + 0.7152 * f(rgb[1] / 255) + 0.0722 * f(rgb[2] / 255)


def ramp(v, lo=56, hi=100):
    x = min(max((v - lo) / (hi - lo), 0), 1) * (len(BLUE_SEQ) - 1)
    k = min(int(x), len(BLUE_SEQ) - 2)
    f = x - k
    a, b = _hex(BLUE_SEQ[k]), _hex(BLUE_SEQ[k + 1])
    return tuple(round(a[j] + (b[j] - a[j]) * f) for j in range(3))


def heatmap():
    cells = []
    for r, (rn, row) in enumerate(zip(HM_ROWS, HM)):
        cells.append(f'<div class="hm-rl{" b" if r in (0, 3) else ""}">{escape(rn)}</div>')
        for c, v in enumerate(row):
            rgb = ramp(v)
            fg = "#ffffff" if _lum(rgb) < 0.30 else INK
            cells.append(f'<div class="hm-c" data-tip="{escape(rn)} · {escape(HM_COLS[c])}|{v}%" '
                         f'style="background:rgb{rgb};color:{fg};--d:{0.05 + 0.07 * c + 0.12 * r:.2f}s">{v}%</div>')
    cells.append('<div></div>')
    for cn in HM_COLS:
        a, b = cn.split(" ", 1)
        cells.append(f'<div class="hm-cl">{a}<br>{b}</div>')
    return f'<div class="card heat" data-anim><div class="hm">{"".join(cells)}</div></div>'


# ------------------------------------------------------------------ ablation line panels + bars
def ablation():
    D = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ablation_curves.json")))
    P = [("(a) Projection error", "‖â − x₁‖", "0", 0.10, [0, 0.05, 0.10], ("w/o consistency", "w/ consistency")),
         ("(b) Q-value discrepancy", "|Q(s,â) − Q(s,x₁)|", "1", 0.50, [0, 0.25, 0.50], ("w/o consistency", "w/ consistency")),
         ("(c) Training loss", "loss", "2", 0.16, [0, 0.08, 0.16], ("w/o adaptive shift", "w/ adaptive shift"))]
    Wv, Hv = 260, 252
    x0, x1, yb, yt = 49, 252, 208, 66
    out = []
    for pi, (title, ylab, key, ymax, yt_, names) in enumerate(P):
        top = ymax * 1.34
        X = lambda v: x0 + (x1 - x0) * v / 10
        Y = lambda v: yb - (yb - yt) * v / top
        ser = D[key]["series"]
        o = [f'<svg class="chart" viewBox="0 0 {Wv} {Hv}" role="img" aria-label="{escape(title)}">',
             f'<text class="pt" x="{Wv / 2}" y="17">{escape(title)}</text>']
        for g in yt_:
            o.append(f'<line class="gl" x1="{x0}" x2="{x1}" y1="{Y(g):.1f}" y2="{Y(g):.1f}"/>')
            o.append(f'<text class="yt" x="{x0 - 6}" y="{Y(g) + 4:.1f}">{"" if g == 0 else f"{g:g}"}</text>')
        for g in (0, 5, 10):
            o.append(f'<text class="xt sm" x="{X(g):.1f}" y="{yb + 14}">{g}</text>')
        o.append(f'<text class="al" x="{(x0 + x1) / 2}" y="{yb + 30}">training steps (k)</text>')
        o.append(f'<text class="al" transform="translate(9,{(yt + yb) / 2}) rotate(-90)">{escape(ylab)}</text>')
        series_js = []
        for si, (src, col, nm) in enumerate((("#B0A695", BLUE, names[0]), ("#E2643C", TERRA, names[1]))):
            s = ser[src]
            xs, m, lo, up = s["x"], s["mean"], s["lo"], s["up"]
            band = ("M" + " L".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in zip(xs, up)) + " L"
                    + " L".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in zip(reversed(xs), reversed(lo))) + "Z")
            line = "M" + " L".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in zip(xs, m))
            d = 0.1 + 0.35 * si
            o.append(f'<path class="band" style="--d:{d + 1.2:.2f}s" fill="{col}" d="{band}"/>')
            o.append(f'<path class="ln" pathLength="1" style="--d:{d:.2f}s" stroke="{col}" d="{line}"/>')
            step = max(1, len(xs) // 60)
            series_js.append({"n": nm, "c": col, "x": [round(v, 3) for v in xs[::step]],
                              "y": [round(v, 4) for v in m[::step]]})
        # legend (line keys)
        for si, (col, nm) in enumerate(((BLUE, names[0]), (TERRA, names[1]))):
            ly = 37 + si * 14
            o.append(f'<line x1="{x0 + 2}" x2="{x0 + 18}" y1="{ly}" y2="{ly}" stroke="{col}" stroke-width="2.5" stroke-linecap="round"/>'
                     f'<text class="lg" x="{x0 + 23}" y="{ly + 4}">{escape(nm)}</text>')
        o.append(f'<line class="ax" x1="{x0}" x2="{x1}" y1="{yb}" y2="{yb}"/>')
        meta = {"x0": x0, "x1": x1, "yb": yb, "yt": yt, "xmax": 10, "top": top, "s": series_js}
        o.append(f'<g class="xh"><line class="xh-l" y1="{yt}" y2="{yb}"/>'
                 + "".join(f'<circle class="xh-d" r="4" fill="{s_["c"]}"/>' for s_ in series_js) + '</g>')
        o.append(f'<rect class="lhit" x="{x0}" y="{yt}" width="{x1 - x0}" height="{yb - yt}" '
                 f"data-lines='{escape(json.dumps(meta, separators=(',', ':')))}'/>")
        o.append("</svg>")
        out.append(f'<figure class="card chart-card" data-anim>{"".join(o)}</figure>')
    # (d) success
    vals = [("w/o both", 72, BLUE_T), ("w/o shift", 76, BLUE_T), ("w/o consistency", 80, BLUE_T), ("Full", 92, TERRA)]
    Yb, Yt = 208, 66
    Y = lambda v: Yb - (Yb - Yt) * v / 108
    o = [f'<svg class="chart" viewBox="0 0 {Wv} {Hv}" role="img" aria-label="(d) Success rate">',
         f'<text class="pt" x="{Wv / 2}" y="17">(d) Success rate</text>']
    for g in (0, 50, 100):
        o.append(f'<line class="gl" x1="{x0}" x2="{x1}" y1="{Y(g):.1f}" y2="{Y(g):.1f}"/><text class="yt" x="{x0 - 6}" y="{Y(g) + 4:.1f}">{g}</text>')
    o.append(f'<text class="al" transform="translate(9,{(Yt + Yb) / 2}) rotate(-90)">overall success (%)</text>')
    gw = (x1 - x0) / 4
    for j, (lab, v, col) in enumerate(vals):
        cx = x0 + gw * (j + 0.5)
        bw = 30
        d = 0.1 + 0.15 * j
        o.append(f'<g class="bw" data-tip="{escape(lab)}|{v}%"><path class="bar v" style="--d:{d:.2f}s" fill="{col}" d="{bar_path(cx - bw / 2, Yb, bw, Yb - Y(v))}"/>'
                 f'<text class="val{" strong" if col == TERRA else ""}" style="--d:{d + 0.7:.2f}s" x="{cx:.1f}" y="{Y(v) - 6:.1f}" data-v="{v}" data-dec="0">{v}</text>'
                 f'<rect class="hit" x="{cx - bw / 2 - 4:.1f}" y="{Yt}" width="{bw + 8}" height="{Yb - Yt}"/></g>')
        l1, *l2 = lab.split(" ", 1)
        o.append(f'<text class="xt sm{" b" if lab == "Full" else ""}" x="{cx:.1f}" y="{Yb + 15}">{escape(l1)}</text>')
        if l2:
            o.append(f'<text class="xt sm" x="{cx:.1f}" y="{Yb + 28}">{escape(l2[0])}</text>')
    o.append(f'<line class="ax" x1="{x0}" x2="{x1}" y1="{Yb}" y2="{Yb}"/></svg>')
    out.append(f'<figure class="card chart-card" data-anim>{"".join(o)}</figure>')
    return (f'<div class="grid4 bleed">{"".join(out)}</div>'
            '<p class="swipe-hint">Swipe sideways for all four panels.</p>')


CHARTS = {"repeated": repeated, "sweep": sweep, "disturb": disturb, "heatmap": heatmap, "ablation": ablation}
