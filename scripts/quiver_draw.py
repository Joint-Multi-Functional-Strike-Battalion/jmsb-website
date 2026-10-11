"""Shared drawing kit for the Quiver's own diagrams (user, 2026-10-10:
"replace images in quiver with your own" - diagrams only; screenshots and
item photos stay).

Plain SVG, white ground, red / green / blue team markers, black arrows.
Fonts are generic sans-serif because an <img> cannot use the page's fonts.
Every page module in scripts/quiver_pages/ builds on these helpers so all
the pictures read as one book.
"""
import math
import os

RED, GREEN, BLUE, INK, MUTE = "#d32f2f", "#2e7d32", "#1565c0", "#20261c", "#6b7260"
TAN, OLIVE, GROUND, LIGHT, GRID = "#c2a878", "#3a4433", "#c8b98f", "#eef0ea", "#d7dbd0"
FONT = "font-family='Arial, Helvetica, sans-serif'"
ROOT = os.path.join("public", "quiver", "img")


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def svg(w, h, body, title):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' "
            f"role='img' aria-label='{esc(title)}'>\n<title>{esc(title)}</title>\n"
            f"<defs><marker id='ah' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
            f"<path d='M0,0 L10,5 L0,10 z' fill='{INK}'/></marker>"
            f"<marker id='ahr' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
            f"<path d='M0,0 L10,5 L0,10 z' fill='{RED}'/></marker>"
            f"<marker id='ahg' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
            f"<path d='M0,0 L10,5 L0,10 z' fill='{GREEN}'/></marker>"
            f"<marker id='ahb' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
            f"<path d='M0,0 L10,5 L0,10 z' fill='{BLUE}'/></marker></defs>\n"
            f"<rect width='{w}' height='{h}' fill='#ffffff'/>\n{body}\n</svg>\n")


HEAD = {RED: "ahr", GREEN: "ahg", BLUE: "ahb"}


def man(x, y, colour, facing=-90, label=""):
    """A soldier: a dot with a pointer the way he faces (degrees, -90 = up)."""
    a = math.radians(facing)
    tip = (x + 16 * math.cos(a), y + 16 * math.sin(a))
    l = (x + 8 * math.cos(a + 2.2), y + 8 * math.sin(a + 2.2))
    r = (x + 8 * math.cos(a - 2.2), y + 8 * math.sin(a - 2.2))
    s = (f"<path d='M{tip[0]:.1f},{tip[1]:.1f} L{l[0]:.1f},{l[1]:.1f} L{r[0]:.1f},{r[1]:.1f} z' fill='{colour}'/>"
         f"<circle cx='{x}' cy='{y}' r='9' fill='{colour}'/>")
    if label:
        s += f"<text x='{x}' y='{y + 4}' text-anchor='middle' {FONT} font-size='11' font-weight='bold' fill='#fff'>{esc(label)}</text>"
    return s


def text(x, y, t, size=14, colour=INK, anchor="middle", weight="normal"):
    return f"<text x='{x}' y='{y}' text-anchor='{anchor}' {FONT} font-size='{size}' font-weight='{weight}' fill='{colour}'>{esc(t)}</text>"


def lines(x, y, rows, size=13, colour=INK, anchor="middle", weight="normal", gap=None):
    """Several lines of text, one under the other."""
    gap = gap or round(size * 1.35)
    return "".join(text(x, y + i * gap, r, size, colour, anchor, weight) for i, r in enumerate(rows))


def arrow(d, colour=INK, width=2.5, dash="", head=None):
    head = head or HEAD.get(colour, "ah")
    da = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<path d='{d}' fill='none' stroke='{colour}' stroke-width='{width}'{da} marker-end='url(#{head})'/>"


def line(x1, y1, x2, y2, colour=INK, width=2, dash=""):
    da = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{colour}' stroke-width='{width}'{da}/>"


def box(x, y, w, h, fill="none", stroke=INK, width=1.5, rx=0, dash=""):
    da = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fill}' stroke='{stroke}' stroke-width='{width}'{da}/>"


def title(w, t, sub=""):
    """Bold heading across the top, optional grey line under it."""
    s = text(w / 2, 30, t, 16, weight="bold")
    if sub:
        s += text(w / 2, 52, sub, 13, MUTE)
    return s


def wedge(x, y, facing, r, half, colour, opacity=.16):
    """A sector of fire: apex at the man, `half` degrees either side of `facing`."""
    a1, a2 = math.radians(facing - half), math.radians(facing + half)
    p1 = (x + r * math.cos(a1), y + r * math.sin(a1))
    p2 = (x + r * math.cos(a2), y + r * math.sin(a2))
    return (f"<path d='M{x},{y} L{p1[0]:.0f},{p1[1]:.0f} A{r},{r} 0 0 1 {p2[0]:.0f},{p2[1]:.0f} z' "
            f"fill='{colour}' opacity='{opacity}' stroke='{colour}' stroke-width='1.5'/>")


def vehicle(x, y, facing=0, colour=TAN, label="", w=54, h=28):
    """A vehicle from above: a rounded box with a darker cab at the front (facing in degrees, 0 = right)."""
    s = (f"<g transform='translate({x},{y}) rotate({facing})'>"
         f"<rect x='{-w / 2}' y='{-h / 2}' width='{w}' height='{h}' rx='5' fill='{colour}' stroke='{INK}' stroke-width='1.5'/>"
         f"<rect x='{w / 2 - 14}' y='{-h / 2 + 4}' width='9' height='{h - 8}' rx='2' fill='{OLIVE}'/>")
    if label:
        s += f"<text x='-4' y='5' text-anchor='middle' {FONT} font-size='13' font-weight='bold' fill='{INK}' transform='rotate({-facing} -4 0)'>{esc(label)}</text>"
    return s + "</g>"


def unit_box(x, y, w=44, h=30, label=""):
    """A NATO infantry symbol: a box with a cross through it."""
    s = (box(x - w / 2, y - h / 2, w, h, "#fff", INK, 2)
         + line(x - w / 2, y - h / 2, x + w / 2, y + h / 2, INK, 2)
         + line(x - w / 2, y + h / 2, x + w / 2, y - h / 2, INK, 2))
    if label:
        s += text(x, y + h / 2 + 16, label, 12, INK, weight="bold")
    return s


def table(x, y, cols, rows, size=13, head_fill=OLIVE, row_h=None, pad=8):
    """A table. cols = [(heading, width)], rows = [[cell, ...]]; a cell may hold '\\n' for extra lines.
    Returns (svg, height)."""
    out = []
    hh = size * 2.4
    cx = x
    for headtxt, cw in cols:
        out.append(box(cx, y, cw, hh, head_fill, INK, 1))
        parts = headtxt.split("\n")
        for i, p in enumerate(parts):
            out.append(text(cx + cw / 2, y + hh / 2 + size * .35 + (i - (len(parts) - 1) / 2) * size * 1.15,
                            p, size, "#fff", weight="bold"))
        cx += cw
    cy = y + hh
    for ri, row in enumerate(rows):
        n = max(len(str(c).split("\n")) for c in row)
        rh = row_h or (n * size * 1.3 + pad * 1.4)
        cx = x
        for (headtxt, cw), cell in zip(cols, row):
            out.append(box(cx, cy, cw, rh, LIGHT if ri % 2 else "#fff", INK, 1))
            for i, p in enumerate(str(cell).split("\n")):
                out.append(text(cx + pad, cy + pad + size + i * size * 1.3, p, size, INK, "start"))
            cx += cw
        cy += rh
    return "".join(out), cy - y


def write(sub, name, content):
    out = os.path.join(ROOT, sub)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("wrote", sub + "/" + name + ".svg")
