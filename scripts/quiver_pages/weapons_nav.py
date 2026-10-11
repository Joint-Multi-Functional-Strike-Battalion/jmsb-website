"""Pictures for the Quiver's Heavy weapons, Sniper, Land navigation and Tactical movement (open areas) pages."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiver_draw import *  # noqa: E402,F401,F403

WOOD, WOOD_EDGE, SKY, FIELD = "#d6e6c8", "#9bbb86", "#ffffff", "#ece4cc"
BROWN = "#6d5a3a"


# ---------------------------------------------------------------- helpers

def path(points, colour=INK, width=2, dash="", head=None):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    if head is not None:
        return arrow(d, colour, width, dash, head or None)
    da = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<path d='{d}' fill='none' stroke='{colour}' stroke-width='{width}'{da}/>"


def ellipse(cx, cy, rx, ry, fill="none", stroke=INK, width=1.5, dash="", rot=0, opacity=1):
    da = f" stroke-dasharray='{dash}'" if dash else ""
    tr = f" transform='rotate({rot} {cx} {cy})'" if rot else ""
    return (f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='{fill}' stroke='{stroke}' "
            f"stroke-width='{width}' opacity='{opacity}'{da}{tr}/>")


def wood(x, y, w, h, seed=1):
    """A wood line from above: a soft green block with a bumpy edge."""
    rnd = random.Random(seed)
    s = [f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='26' fill='{WOOD}'/>"]
    step = 30
    for i in range(int(w // step) + 1):
        for yy in (y + 6, y + h - 6):
            s.append(f"<circle cx='{x + i * step + rnd.randint(-4, 4)}' cy='{yy + rnd.randint(-4, 4)}' "
                     f"r='{rnd.randint(14, 20)}' fill='{WOOD}'/>")
    for j in range(int(h // step) + 1):
        for xx in (x + 6, x + w - 6):
            s.append(f"<circle cx='{xx + rnd.randint(-4, 4)}' cy='{y + j * step + rnd.randint(-4, 4)}' "
                     f"r='{rnd.randint(14, 20)}' fill='{WOOD}'/>")
    for _ in range(int(w * h / 2600)):
        s.append(f"<circle cx='{rnd.uniform(x + 15, x + w - 15):.0f}' cy='{rnd.uniform(y + 15, y + h - 15):.0f}' "
                 f"r='{rnd.randint(5, 9)}' fill='{WOOD_EDGE}' opacity='.45'/>")
    return "".join(s)


def rally(x, y, label="", side="right"):
    s = f"<circle cx='{x}' cy='{y}' r='11' fill='#fff' stroke='{INK}' stroke-width='2.5'/>"
    if label:
        if side == "right":
            s += text(x + 18, y + 5, label, 13, INK, "start", "bold")
        elif side == "left":
            s += text(x - 18, y + 5, label, 13, INK, "end", "bold")
        else:
            s += text(x, y - 18, label, 13, INK, "middle", "bold")
    return s


def person(x, y, h, colour=RED, view="front", facing=1):
    """A simple standing figure, feet at (x, y), h tall. view 'front' or 'side' (facing 1 = right)."""
    hr = h * .11
    s = f"<circle cx='{x:.1f}' cy='{y - h + hr:.1f}' r='{hr:.1f}' fill='{colour}'/>"
    bw = h * (.26 if view == "front" else .18)
    top, hip = y - h + 2 * hr + h * .02, y - h * .45
    s += f"<rect x='{x - bw / 2:.1f}' y='{top:.1f}' width='{bw:.1f}' height='{hip - top:.1f}' rx='{bw * .3:.1f}' fill='{colour}'/>"
    lw = max(h * .07, 1.5)
    if view == "front":
        s += line(x - bw * .25, hip, x - bw * .35, y, colour, lw) + line(x + bw * .25, hip, x + bw * .35, y, colour, lw)
    else:
        s += line(x, hip, x - facing * h * .16, y, colour, lw) + line(x, hip, x + facing * h * .16, y, colour, lw)
        gy = top + (hip - top) * .35
        s += line(x - facing * bw * .3, gy + h * .05, x + facing * h * .32, gy - h * .04, INK, max(h * .035, 1.2))
    return s


def ifv(x, y, colour=TAN, dash=""):
    """A tracked vehicle side-on, moving right. x = FRONT end, y = ground. 200 long."""
    L = 200
    op = " fill-opacity='.0' stroke-dasharray='6 5'" if dash else ""
    hull = (f"<path d='M{x - L},{y - 14} L{x - L},{y - 52} L{x - 70},{y - 58} L{x - 8},{y - 46} L{x},{y - 28} "
            f"L{x - 14},{y - 14} z' fill='{colour}' stroke='{INK}' stroke-width='2'{op}/>")
    tur = (f"<path d='M{x - 130},{y - 56} L{x - 122},{y - 74} L{x - 78},{y - 74} L{x - 70},{y - 58} z' "
           f"fill='{colour}' stroke='{INK}' stroke-width='2'{op}/>")
    gun = line(x - 80, y - 68, x - 20, y - 70, INK, 3, "6 5" if dash else "")
    track = (f"<rect x='{x - L + 4}' y='{y - 24}' width='{L - 18}' height='24' rx='12' fill='{'none' if dash else OLIVE}' "
             f"stroke='{INK}' stroke-width='2'{' stroke-dasharray=\"6 5\"' if dash else ''}/>")
    wheels = "" if dash else "".join(
        f"<circle cx='{x - L + 20 + i * 27}' cy='{y - 12}' r='9' fill='{LIGHT}' stroke='{INK}' stroke-width='1.5'/>"
        for i in range(7))
    return hull + tur + gun + track + wheels


def tree(x, y, h=150):
    s = f"<rect x='{x - 6}' y='{y - h}' width='12' height='{h}' fill='{BROWN}'/>"
    for dx, dy, r in ((-30, -h - 8, 32), (22, -h - 14, 34), (-4, -h - 40, 34), (40, -h + 14, 22), (-44, -h + 16, 22)):
        s += f"<circle cx='{x + dx}' cy='{y + dy}' r='{r}' fill='#7cb342' opacity='.75'/>"
    return s


def ground(x1, x2, y, depth=24):
    return (f"<rect x='{x1}' y='{y}' width='{x2 - x1}' height='{depth}' fill='{GROUND}'/>"
            + line(x1, y, x2, y, INK, 2.5))


# ---------------------------------------------------------------- heavy weapons

def clock_method():
    W, H = 800, 640
    cx, cy, R = 400, 345, 225
    b = [title(W, "THE CLOCK  -  12 o'clock is always where the gun points",
               "Call a target by its clock direction from the gun-target line")]
    # frontal arc 9 -> 12 -> 3
    b.append(f"<path d='M{cx - R + 26},{cy} A{R - 26},{R - 26} 0 0 1 {cx + R - 26},{cy} z' fill='{GREEN}' opacity='.10'/>")
    b.append(ellipse(cx, cy, R, R, "none", INK, 2))
    b.append(ellipse(cx, cy, R - 26, R - 26, "none", INK, 1.5))
    b.append(f"<path d='M{cx},{cy} m{-R},0 a{R},{R} 0 1 0 {2 * R},0 a{R},{R} 0 1 0 {-2 * R},0 "
             f"M{cx},{cy} m{-(R - 26)},0 a{R - 26},{R - 26} 0 1 1 {2 * (R - 26)},0 a{R - 26},{R - 26} 0 1 1 {-2 * (R - 26)},0' "
             f"fill='{LIGHT}' fill-rule='evenodd'/>")
    for h in range(1, 13):
        a = math.radians(h * 30 - 90)
        b.append(text(cx + (R - 13) * math.cos(a), cy + (R - 13) * math.sin(a) + 5, str(h), 15, INK, weight="bold"))
    b.append(line(cx, cy - 16, cx, cy - R + 26, INK, 2, "8 5"))
    b.append(line(cx, cy - R, cx, cy - R - 22, INK, 2, "8 5"))
    b.append(text(cx + 10, cy - R - 14, "gun-target line / line of sight", 13, INK, "start", "bold"))
    b.append(text(cx, cy + 90, "left shoulder  -  front  -  right shoulder", 12, GREEN))
    b.append(text(cx, cy + 108, "(9 to 3: the gunner's frontal arc)", 12, GREEN))
    b.append(arrow(f"M{cx - 24},{cy - 70} A90,90 0 0 0 {cx - 110},{cy - 30}", INK, 2.5))
    b.append(arrow(f"M{cx + 24},{cy - 70} A90,90 0 0 1 {cx + 110},{cy - 30}", INK, 2.5))
    b.append(text(cx - 110, cy - 6, "traverse left", 12, MUTE))
    b.append(text(cx + 110, cy - 6, "traverse right", 12, MUTE))
    b.append(man(cx, cy, GREEN, -90))
    b.append(text(cx, cy + 32, "Gun", 13, GREEN, weight="bold"))
    # a called target at 2 o'clock
    a = math.radians(2 * 30 - 90)
    tx, ty = cx + 150 * math.cos(a), cy + 150 * math.sin(a)
    b.append(line(cx + 10, cy - 6, tx - 8, ty + 5, RED, 1.5, "4 4"))
    b.append(man(tx, ty, RED, 150))
    b.append(line(tx + 12, ty - 8, 640, 196, RED, 1.2))
    b.append(text(644, 192, "\"Two o'clock, 300,", 13, RED, "start", "bold"))
    b.append(text(644, 210, "troops in the open\"", 13, RED, "start", "bold"))
    return svg(W, H, "\n".join(b), "The clock method: 12 o'clock is the gun-target line, and targets are called by clock direction")


def maximum_ordinate():
    W, H = 860, 360
    x0, y0, px = 60, 270, 0.68  # px per metre
    b = [title(W, "MAXIMUM ORDINATE  -  the further the target, the higher the round climbs",
               "H = the highest point the round reaches above the line of sight")]
    b.append(line(x0, y0, x0 + 1150 * px, y0, INK, 2.5))
    for m in range(0, 1101, 100):
        x = x0 + m * px
        b.append(line(x, y0 - 6, x, y0 + 6, INK, 2))
        if m and m % 200 == 0 and m != 1000 or m == 1100:
            b.append(text(x, y0 + 26, f"{m:,} m", 13, INK, weight="bold"))
    for rng, top, lab, col in ((600, 60, "H = 1 m", GREEN), (800, 110, "H = 3 m", BLUE), (1100, 175, "H = 6 m", RED)):
        pts = []
        apex = rng * .64
        for i in range(61):
            d = rng * i / 60
            # a flattened arc that peaks about two-thirds of the way out
            if d <= apex:
                hgt = top * (1 - ((apex - d) / apex) ** 2)
            else:
                hgt = top * (1 - ((d - apex) / (rng - apex)) ** 2)
            pts.append((x0 + d * px, y0 - hgt))
        b.append(path(pts, col, 2.5))
        ax = x0 + apex * px
        b.append(line(ax, y0, ax, y0 - top, col, 2, "5 4"))
        b.append(text(ax + 6, y0 - top - 8, lab, 13, col, "start", "bold"))
    b.append(text(W / 2, 330, "The peak sits about two-thirds of the way to the target. Mind it when firing over friendly troops.", 13, MUTE))
    return svg(W, H, "\n".join(b), "Maximum ordinate: at 600, 800 and 1,100 metres the round peaks about 1, 3 and 6 metres above the line of sight")


def cone_beaten_zone():
    W, H = 860, 440
    gx, gy = 70, 300       # muzzle
    top, gnd = 252, 312    # 1.8 m line, ground
    b = [title(W, "CONE OF FIRE, BEATEN ZONE AND DANGER SPACE",
               "Side view, heights exaggerated")]
    b.append(ground(30, 830, gnd, 42))
    b.append(line(30, top, 830, top, MUTE, 1.5, "4 4"))

    # trajectories of one burst
    lands = [600, 640, 680, 720, 760]
    peaks = [150, 135, 120, 105, 90]

    def traj(x_end, peak):
        pts = []
        for i in range(81):
            t = i / 80
            x = gx + (x_end - gx) * t
            y = gy + (gnd - gy) * t - (gy - peak) * math.sin(math.pi * t ** 1.4)
            pts.append((x, min(y, gnd)))
        return pts
    for xe, pk in zip(lands, peaks):
        b.append(path(traj(xe, pk), RED, 1.8))
    # danger space, worked out on the middle round
    mid = traj(lands[2], peaks[2])
    up = next(x for x, y in mid if y < top)
    down = next(x for x, y in reversed(mid) if y < top)
    b.append(f"<rect x='{gx}' y='{top}' width='{up - gx:.0f}' height='{gnd - top}' fill='{RED}' opacity='.16'/>")
    b.append(f"<rect x='{down:.0f}' y='{top}' width='{lands[-1] + 10 - down:.0f}' height='{gnd - top}' fill='{RED}' opacity='.16'/>")
    b.append(text(gx + 4, gnd + 34, "danger space", 13, RED, "start", "bold"))
    b.append(text((down + lands[-1]) / 2, gnd + 34, "danger space", 13, RED, weight="bold"))
    # cone cross-section, sized to the burst where it is drawn
    cxs = 440
    ys = [traj(xe, pk) for xe, pk in zip(lands, peaks)]
    yy = [min(p, key=lambda q: abs(q[0] - cxs))[1] for p in ys]
    b.append(ellipse(cxs, (min(yy) + max(yy)) / 2, 10, (max(yy) - min(yy)) / 2 + 8, "#fff", INK, 2, opacity=.85))
    b.append(text(cxs, min(yy) - 18, "cone of fire", 13, INK, weight="bold"))
    # beaten zone
    b.append(ellipse(680, gnd, 92, 8, "#bdbdbd", INK, 2, opacity=.95))
    b.append(ellipse(680, gnd, 60, 6, MUTE, INK, 1, opacity=.8))
    b.append(text(680, gnd + 62, "beaten zone", 13, INK, weight="bold"))
    b.append(text(680, gnd + 80, "(dark core: the effective 85 per cent)", 12, MUTE))
    b.append(text((up + down) / 2, top - 6, "1.8 m (a standing man)", 12, MUTE))
    b.append(man(gx - 12, gy, GREEN, 0))
    b.append(text(gx - 12, gnd + 62, "Gun", 13, GREEN, weight="bold"))
    b.append(text(W / 2, 426, "Danger space: wherever the rounds are below head height, from muzzle to beaten zone.", 13, MUTE))
    return svg(W, H, "\n".join(b), "Cone of fire, beaten zone and danger space shown side-on")


def grazing_plunging():
    W, H = 860, 600
    b = [text(W / 2, 30, "FIRE AND THE GROUND  -  grazing or plunging", 16, weight="bold")]
    # grazing panel
    b.append(text(40, 66, "GRAZING", 15, GREEN, "start", "bold"))
    b.append(text(140, 66, "the middle of the cone stays within 1 m of the ground", 13, MUTE, "start"))
    gp = [(30, 170), (200, 166), (380, 160), (560, 156), (700, 158), (830, 170)]
    b.append(f"<path d='M{' L'.join(f'{x},{y}' for x, y in gp)} L830,200 L30,200 z' fill='{GROUND}' stroke='{INK}' stroke-width='2'/>")
    b.append(path([(x, y - 34) for x, y in gp], MUTE, 1.2, "4 4"))
    b.append(text(826, 128, "1 m", 12, MUTE, "end"))
    b.append(f"<path d='M70,152 C300,132 560,126 790,150' fill='none' stroke='{RED}' stroke-width='3'/>")
    b.append(f"<path d='M70,152 C300,116 560,106 790,132' fill='none' stroke='{RED}' stroke-width='1.5' stroke-dasharray='6 4'/>")
    b.append(f"<path d='M70,152 C300,148 560,146 790,160' fill='none' stroke='{RED}' stroke-width='1.5' stroke-dasharray='6 4'/>")
    b.append(man(56, 156, GREEN, 0))
    b.append(text(430, 226, "Rounds stay low the whole way: anyone standing on that line is hit.", 13, INK))
    b.append(text(430, 246, "Light/medium MG out to about 600 m, heavy MG about 700 m.", 13, MUTE))
    b.append(line(30, 268, 830, 268, GRID, 2))
    b.append("<g transform='translate(0,-44)'>")
    # plunging panel
    b.append(text(40, 346, "PLUNGING", 15, RED, "start", "bold"))
    b.append(text(150, 346, "the rounds come down steeply: little or no danger space", 13, MUTE, "start"))
    prof = "M30,420 C90,410 130,430 190,470 C260,520 330,575 420,580 C500,585 540,520 580,470 C620,420 700,410 830,400 L830,610 L30,610 z"
    b.append(f"<path d='{prof}' fill='{GROUND}' stroke='{INK}' stroke-width='2'/>")
    # from high ground down into the dip
    b.append(man(60, 404, GREEN, 30))
    b.append(f"<path d='M76,410 C250,420 380,500 420,566' fill='none' stroke='{RED}' stroke-width='2.5' stroke-dasharray='7 4'/>")
    b.append(ellipse(420, 574, 26, 8, "#5f5f5f", INK, 1))
    b.append(text(452, 562, "high ground into low", 12, INK, "start"))
    # at long range onto the far crest
    b.append(f"<path d='M76,408 C300,330 560,330 640,416' fill='none' stroke='{RED}' stroke-width='2.5' stroke-dasharray='7 4'/>")
    b.append(ellipse(646, 420, 24, 7, "#5f5f5f", INK, 1, rot=-12))
    b.append(text(560, 360, "long range", 12, INK, "start"))
    # low ground into rising ground
    b.append(man(250, 520, GREEN, -10))
    b.append(f"<path d='M266,516 C380,500 470,492 552,500' fill='none' stroke='{RED}' stroke-width='2.5' stroke-dasharray='7 4'/>")
    b.append(ellipse(560, 502, 9, 20, "#5f5f5f", INK, 1, rot=30))
    b.append(text(470, 476, "into rising ground", 12, INK))
    b.append("</g>")
    b.append(text(W / 2, 588, "The beaten zone shrinks to a short dark patch, and the dip in between is dead space.", 13, MUTE))
    return svg(W, H, "\n".join(b), "Grazing fire stays within one metre of the ground; plunging fire comes down steeply onto a short beaten zone")


def _formation(cx, cy, n, gap, angle, facing, colour=RED):
    """n men in a row centred on (cx, cy), the row turned `angle` degrees, each facing `facing`."""
    a = math.radians(angle)
    out = []
    for i in range(n):
        o = (i - (n - 1) / 2) * gap
        out.append(man(cx + o * math.cos(a), cy + o * math.sin(a), colour, facing))
    return "".join(out)


def target_classes():
    W, H = 860, 876
    pw, ph = 430, 400
    b = [title(W, "FIRE AND THE TARGET  -  how the beaten zone lies across the enemy",
               "Grey: the beaten zone (long axis along the line of fire). Red arrow: the enemy's direction of travel.")]
    panels = [
        ("FRONTAL", "Fire hits the front of the formation", GREEN),
        ("FLANKING", "Fire hits the side of the formation", GREEN),
        ("OBLIQUE", "Formation at an angle to the line of fire", GREEN),
        ("ENFILADE", "Beaten zone runs the length of the target: the best", RED),
    ]
    for k, (name, sub, col) in enumerate(panels):
        ox, oy = (k % 2) * pw, 70 + (k // 2) * ph
        b.append(box(ox + 6, oy + 6, pw - 12, ph - 12, "none", GRID, 1.5, 8))
        b.append(text(ox + pw / 2, oy + 34, name, 15, INK, weight="bold"))
        b.append(text(ox + pw / 2, oy + 54, sub, 12, MUTE))
        gun = (ox + pw / 2, oy + ph - 40)

        def zone(x, y):
            b.append(ellipse(x, y, 26, 70, "#cfcfcf", MUTE, 1.5, "6 4", opacity=.9))
            b.append(line(x, y + 70, x, oy + ph - 58, MUTE, 1.5, "5 4"))
        if name == "ENFILADE":
            for gx, lab, fac, arr in ((ox + 125, "column coming at you", 90, "down"),
                                      (ox + 305, "line moving across", 0, "right")):
                b.append(ellipse(gx, oy + 190, 26, 92, "#cfcfcf", MUTE, 1.5, "6 4", opacity=.9))
                b.append(line(gx, oy + 282, gx, oy + ph - 58, MUTE, 1.5, "5 4"))
                b.append(_formation(gx, oy + 190, 5, 34, 90, fac))
                if arr == "down":
                    b.append(arrow(f"M{gx - 50},{oy + 130} L{gx - 50},{oy + 190}", RED, 3))
                else:
                    b.append(arrow(f"M{gx + 36},{oy + 120} L{gx + 86},{oy + 120}", RED, 3))
                b.append(text(gx, oy + ph - 70 + 0, "", 12))
                b.append(man(gx, oy + ph - 40, GREEN, -90))
                b.append(text(gx, oy + 86, lab, 12, INK, weight="bold"))
            continue
        zx, zy = gun[0], oy + 200
        zone(zx, zy)
        if name == "FRONTAL":
            b.append(_formation(zx, zy - 20, 5, 34, 0, 90))
            b.append(arrow(f"M{zx - 120},{zy - 50} L{zx - 120},{zy + 10}", RED, 3))
            b.append(text(zx + 40, zy + 34, "line coming at you", 12, INK, "start", "bold"))
        elif name == "FLANKING":
            b.append(_formation(zx, zy - 20, 5, 34, 0, 0))
            b.append(arrow(f"M{zx + 100},{zy - 50} L{zx + 150},{zy - 50}", RED, 3))
            b.append(text(zx + 40, zy + 34, "column crossing your front", 12, INK, "start", "bold"))
        else:
            b.append(_formation(zx, zy - 20, 5, 34, -30, 150))
            b.append(arrow(f"M{zx - 100},{zy + 40} L{zx - 140},{zy + 63}", RED, 3))
            b.append(text(zx + 40, zy + 54, "formation at an angle", 12, INK, "start", "bold"))
        b.append(man(*gun, GREEN, -90))
    return svg(W, H, "\n".join(b), "Classes of fire with respect to the target: frontal, flanking, oblique and enfilade")


def _view_panel(ox, oy, w, h, name, sub, figs, zone_w=44):
    """What the gunner sees: ground, horizon, the beaten zone as a dashed ring, the enemy in it."""
    hz = oy + h * .42
    s = [box(ox, oy, w, h, SKY, INK, 1.5),
         f"<rect x='{ox}' y='{hz:.0f}' width='{w}' height='{oy + h - hz:.0f}' fill='{FIELD}'/>",
         line(ox, hz, ox + w, hz, MUTE, 1.5), box(ox, oy, w, h, "none", INK, 1.5)]
    cx = ox + w / 2
    zy = hz + 10
    s.append(ellipse(cx, zy, zone_w, h * .26, "none", INK, 1.8, "6 4"))
    s.append(line(cx, zy + h * .26, cx, oy + h - 34, INK, 1.5, "5 4"))
    s.extend(figs(cx, zy + h * .12))
    s.append(man(cx, oy + h - 22, GREEN, -90))
    s.append(text(ox + w / 2, oy + h + 24, name, 15, INK, weight="bold"))
    s.append(text(ox + w / 2, oy + h + 42, sub, 12, MUTE))
    return "".join(s)


def gunner_view_frontal_flanking():
    W, H = 860, 400
    b = [title(W, "THROUGH THE GUNNER'S EYES  -  frontal and flanking", "Dashed ring: where the beaten zone lands")]

    def frontal(cx, fy):
        return [person(cx + dx, fy, 46, RED, "front") for dx in (-34, 0, 34)]

    def flanking(cx, fy):
        return [person(cx + dx, fy, 46, RED, "side", 1) for dx in (-130, -80, -30, 20, 70, 120)]
    b.append(_view_panel(20, 70, 400, 260, "FRONTAL", "the enemy faces you: rounds hit their front", frontal))
    b.append(_view_panel(440, 70, 400, 260, "FLANKING", "the enemy crosses your front: rounds hit their side", flanking))
    return svg(W, H, "\n".join(b), "Frontal and flanking fire as the gunner sees them")


def gunner_view_oblique_enfilade():
    W, H = 860, 420
    b = [title(W, "THROUGH THE GUNNER'S EYES  -  oblique and enfilade", "Dashed ring: where the beaten zone lands")]

    def oblique(cx, fy):
        out = []
        for i in range(6):
            sc = 1 - i * .11
            out.append(person(cx - 60 + i * 34, fy - 24 + i * 9 - 30 * (1 - sc), 52 * sc, RED, "side", 1))
        return out[::-1]

    def frontal_enf(cx, fy):
        out = []
        for i in range(5):
            sc = 1 - i * .13
            out.append(person(cx + (i % 2) * 16 - 8, fy + 30 - i * 20, 56 * sc, RED, "front"))
        return out[::-1]

    def flank_enf(cx, fy):
        out = []
        for i in range(5):
            sc = 1 - i * .13
            out.append(person(cx + (i % 2) * 18 - 9, fy + 30 - i * 20, 56 * sc, RED, "side", 1))
        return out[::-1]
    b.append(_view_panel(20, 70, 260, 280, "OBLIQUE", "a file walking away at an angle", oblique, 50))
    b.append(_view_panel(300, 70, 260, 280, "FRONTAL ENFILADE", "a column walking at you", frontal_enf))
    b.append(_view_panel(580, 70, 260, 280, "FLANKING ENFILADE", "a line crossing, seen end-on", flank_enf))
    return svg(W, H, "\n".join(b), "Oblique, frontal enfilade and flanking enfilade fire as the gunner sees them")


def fire_manipulation():
    W, H = 900, 640
    b = [title(W, "FIRE AND THE GUN  -  how the gunner moves his fire",
               "Dot: the gun.  Grey: where each burst lands.  Hollow ring: a burst with no beaten zone")]

    def gun(x, y):
        return f"<circle cx='{x}' cy='{y}' r='6' fill='{INK}'/>"

    def burst(x0, y0, x1, y1, rx=12, ry=26, ang=0, fill="#cfcfcf"):
        return (line(x0, y0, x1, y1 + ry, MUTE, 2, "6 5")
                + ellipse(x1, y1, rx, ry, fill, INK, 1.5, rot=ang))

    cells = [
        ("FIXED", ["one aim point,", "a point target"]),
        ("TRAVERSE", ["change direction only:", "wide, shallow target"]),
        ("SEARCH", ["change elevation only:", "deep, narrow target"]),
        ("TRAVERSE AND SEARCH", ["direction and elevation:", "target at an angle"]),
        ("SWINGING TRAVERSE", ["big swings, cyclic rate,", "crossing targets"]),
        ("FREE GUN", ["fast changes both ways,", "cyclic rate, fast movers"]),
    ]
    for k, (name, rows) in enumerate(cells):
        cx = 150 + (k % 3) * 300
        top = 90 + (k // 3) * 280
        gy = top + 170
        b.append(gun(cx, gy))
        if name == "FIXED":
            b.append(burst(cx, gy, cx, top + 40))
        elif name == "TRAVERSE":
            for i in range(-3, 4):
                b.append(burst(cx, gy, cx + i * 22, top + 40))
        elif name == "SEARCH":
            for i in range(3):
                b.append(burst(cx, gy, cx, top + 26 + i * 44, 12, 22))
        elif name == "TRAVERSE AND SEARCH":
            for i in range(-3, 4):
                b.append(burst(cx, gy, cx + i * 20, top + 50 - i * 12, 11, 22))
        else:
            spread = 8 if name == "SWINGING TRAVERSE" else 6
            pts = []
            for i in range(spread):
                f = i / (spread - 1)
                if name == "SWINGING TRAVERSE":
                    pts.append((cx - 115 + 230 * f, top + 30))
                else:
                    pts.append((cx - 100 + 200 * f, top + (30 if i % 2 == 0 else 70)))
            for x, y in pts:
                b.append(line(cx, gy, x, y + 11, MUTE, 2, "6 5"))
                b.append(f"<circle cx='{x:.0f}' cy='{y}' r='11' fill='#fff' stroke='{INK}' stroke-width='1.5'/>")
        b.append(text(cx, gy + 34, name, 14, INK, weight="bold"))
        b.append(lines(cx, gy + 54, rows, 12, MUTE))
    return svg(W, H, "\n".join(b), "Fixed, traversing, searching, traverse-and-search, swinging traverse and free gun fire")


def speed_estimation():
    W, H = 880, 620
    b = [title(W, "SPEED ESTIMATION  -  count one second against a fixed object",
               "Start counting \"one thousand one\" as the front passes the object (about one second)")]
    # top: the start
    post, gy = 520, 250
    b.append(ground(60, 820, gy, 14))
    b.append(tree(post, gy, 120))
    b.append(ifv(post, gy, TAN))
    b.append(arrow(f"M{post - 170},{gy - 90} L{post - 90},{gy - 90}", RED, 3))
    b.append(text(post + 70, gy - 70, "Front passes the tree:", 14, INK, "start", "bold"))
    b.append(text(post + 70, gy - 50, "start counting", 14, INK, "start", "bold"))
    # bottom: after one second
    for k, (name, sub, frac, col) in enumerate((("FAST", "more than half has passed: 10 mph (16 km/h) or more", .66, RED),
                                                ("SLOW", "less than half has passed: under 10 mph", .3, BLUE))):
        ox = 40 + k * 410
        pgy = 520
        b.append(box(ox, 300, 390, 280, "none", GRID, 1.5, 8))
        b.append(ground(ox + 10, ox + 380, pgy, 12))
        p = ox + 222
        b.append(ifv(p, pgy, "none", dash="1"))
        b.append(tree(p, pgy, 80))
        b.append(ifv(p + 200 * frac, pgy, TAN))
        b.append(text(ox + 195, 328, f"{name}  -  after \"one thousand one\"", 14, col, weight="bold"))
        b.append(text(ox + 195, 556, sub, 12, INK))
    b.append(text(W / 2, 606, "Dashed outline: where the vehicle was when you started counting.", 12, MUTE))
    return svg(W, H, "\n".join(b), "Speed estimation: if more than half the vehicle passes a fixed object in one second it is fast, less than half it is slow")


def _merge_table(cols, rows, merged, size=13, pad=8):
    """table() with the last column merged over row groups. merged = [(first_row, last_row, text)]."""
    t, h = table(20, 20, cols, [r + [""] for r in rows], size=size, pad=pad)
    hh = size * 2.4
    heights = [max(len(str(c).split("\n")) for c in r) * size * 1.3 + pad * 1.4 for r in rows]
    x = 20 + sum(w for _, w in cols[:-1])
    cw = cols[-1][1]
    out = [t]
    for a, z, body in merged:
        y = 20 + hh + sum(heights[:a])
        rh = sum(heights[a:z + 1])
        out.append(box(x, y, cw, rh, "#fff", INK, 1))
        for i, p in enumerate(body.split("\n")):
            out.append(text(x + pad, y + pad + size + i * size * 1.3, p, size, INK, "start"))
    return "".join(out), h


def kill_types():
    cols = [("Kill", 170), ("What is hit", 300), ("What the vehicle can still do", 300)]
    rows = [["Mobility kill", "Tracks, wheels, suspension,\nengine or gearbox", "Cannot move, CAN still shoot.\nStay out of its arc."],
            ["Firepower kill", "Main gun or its controls", "Cannot fight, CAN still drive\naway. Finish it or let it go."],
            ["Catastrophic kill", "Ammunition or fuel stowage,\nusually by more than one hit", "Nothing: the vehicle\nis destroyed."]]
    t, h = table(20, 20, cols, rows, size=14, pad=10)
    return svg(810, int(h) + 40, t, "Types of vehicle kill: mobility, firepower and catastrophic, and what the vehicle can still do after each")


def aimpoints():
    cols = [("Aim at", 150), ("What the rocket does", 380), ("How to fire", 300)]
    rows = [["Firing port or\nloophole", "Bursts at the back of the position: little\ndamage to it, the gear or the people inside\nunless they take a direct hit. Wasted.", ""],
            ["Berm", "Bursts outside or inside the berm: a small\nhole and dust, nobody hurt unless hit\ndirectly.", ""],
            ["Window", "May fly right through before it goes off;\nif not, dust and minor damage to the back\nwall. Few casualties.", ""],
            ["Wall", "Goes off on contact: dust, a small hole,\nlittle harm to anyone inside.", ""],
            ["Corner", "Corners are reinforced, so the rocket goes\noff sooner. It should burst in the room you\nwant: dust and overpressure can stun the\npeople near it.", ""]]
    merged = [(0, 1, "Fire the rocket 15 to 30 cm\n(6 to 12 in) in front of the\nfiring port, into the berm.\nKeep small arms on the\nposition so nobody inside can\nfire back with their own AT."),
              (2, 4, "Aim 15 to 30 cm (6 to 12 in)\nin from the side or bottom of\nthe window. The rocket bursts\non brick or concrete and\nblows a hole; the warhead\ndecides how big.")]
    t, h = _merge_table(cols, [r[:2] for r in rows], merged, size=13, pad=9)
    return svg(870, int(h) + 40, t, "Light anti-armour aim points on buildings and bunkers, what each does and how to fire")


# ---------------------------------------------------------------- sniper

def work_in_progress():
    W, H = 320, 320
    c = 160
    b = [f"<path d='M{c},12 L{W - 12},{c} L{c},{H - 12} L12,{c} z' fill='{TAN}' stroke='{OLIVE}' stroke-width='10' stroke-linejoin='round'/>",
         f"<path d='M{c},34 L{W - 34},{c} L{c},{H - 34} L34,{c} z' fill='none' stroke='{INK}' stroke-width='2'/>"]
    # a little barrier
    b.append("<clipPath id='bar'><rect x='104' y='150' width='112' height='24'/></clipPath>")
    b.append(f"<rect x='104' y='150' width='112' height='24' fill='#fff'/>")
    b.append("<g clip-path='url(#bar)'>" + "".join(
        f"<path d='M{100 + i * 24},174 L{112 + i * 24},150 L{124 + i * 24},150 L{112 + i * 24},174 z' fill='{OLIVE}'/>"
        for i in range(6)) + "</g>")
    b.append(f"<rect x='104' y='150' width='112' height='24' fill='none' stroke='{INK}' stroke-width='2'/>")
    b.append(line(116, 174, 116, 200, INK, 4) + line(204, 174, 204, 200, INK, 4))
    b.append(text(c, 120, "WORK IN", 22, INK, weight="bold"))
    b.append(text(c, 228, "PROGRESS", 19, INK, weight="bold"))
    return svg(W, H, "\n".join(b), "Work in progress")


def bullet_path():
    W, H = 880, 440
    sx, los = 150, 200        # scope / line of sight
    mx, my = 150, 232         # muzzle
    ppm = 1.15                # px per metre
    d1, z = 45, 300           # first crossing, zero range
    # height below the line of sight: zero at d1 and z, sight height at the muzzle, falling away past zero
    a = (my - los) / (d1 * z)
    bb = -0.001

    def ty(d):
        return los + a * (d - d1) * (d - z) * (1 + bb * d)
    slope = a * (-(d1 + z) + d1 * z * bb)   # px per metre at the muzzle (negative = up)
    b = [title(W, "BULLET PATH  -  zeroed at 300 m", "Side view, heights exaggerated")]
    # rifle
    b.append(f"<path d='M40,{my + 34} L60,{my + 6} L110,{my - 2} L{mx},{my - 4} L{mx},{my + 4} L112,{my + 10} L74,{my + 44} z' fill='{INK}'/>")
    b.append(f"<rect x='70' y='{los - 7}' width='{sx - 70}' height='12' rx='5' fill='{INK}'/>")
    b.append(line(96, los + 5, 96, my - 2, INK, 4) + line(126, los + 5, 126, my - 3, INK, 4))
    # line of sight with range ticks
    b.append(line(sx, los, 840, los, "#c99a00", 2.5, "7 5"))
    for m in range(100, 601, 100):
        x = mx + m * ppm
        if x > 800:
            break
        b.append(line(x, los - 6, x, los + 6, INK, 2))
        b.append(text(x, los - 12, f"{m} m", 12, INK, weight="bold"))
    b.append(text(842, los - 12, "Line of sight", 13, "#a07800", "end", "bold"))
    # line of departure
    dmax = (my - 84) / -slope
    xe, ye = mx + dmax * ppm, my + slope * dmax
    b.append(arrow(f"M{mx},{my} L{xe:.0f},{ye:.0f}", BLUE, 2.5))
    b.append(text(xe - 4, ye - 10, "Line of departure (where the barrel points)", 13, BLUE, "end", "bold"))
    # trajectory
    dend = 560
    pts = [(mx + d * ppm, ty(d)) for d in range(0, dend + 1, 5)]
    b.append(arrow("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), GREEN, 3))
    b.append(text(mx + dend * ppm - 20, ty(dend) + 24, "Bullet path", 13, GREEN, "end", "bold"))
    # sight height
    b.append(f"<path d='M{mx - 30},{los + 8} L{mx - 30},{my}' stroke='{RED}' stroke-width='1.5' marker-start='url(#ahr)' marker-end='url(#ahr)'/>")
    b.append(text(mx - 30, my + 64, "sight height", 12, RED, weight="bold"))
    b.append(line(mx - 30, my + 4, mx - 30, my + 50, RED, 1, "3 3"))
    # crossings
    x1, xz = mx + d1 * ppm, mx + z * ppm
    b.append(f"<circle cx='{x1:.0f}' cy='{los}' r='5' fill='{GREEN}'/>")
    b.append(line(x1, los + 6, x1 + 30, 300, MUTE, 1.2))
    b.append(lines(x1 + 34, 314, ["First crossing: the round", "rises through the line of sight"], 12, INK, "start"))
    b.append(f"<circle cx='{xz:.0f}' cy='{los}' r='6' fill='{RED}'/>")
    b.append(line(xz, los + 6, xz - 10, 300, MUTE, 1.2))
    b.append(lines(xz - 14, 314, ["ZERO RANGE: the round comes", "back down onto the line of sight.", "Aim dead on."], 12, INK, "start", "bold"))
    # bullet drop
    dd = 150
    xd = mx + dd * ppm
    b.append(f"<path d='M{xd:.0f},{my + slope * dd + 4:.0f} L{xd:.0f},{ty(dd) - 4:.0f}' stroke='{RED}' stroke-width='2' marker-start='url(#ahr)' marker-end='url(#ahr)'/>")
    b.append(text(xd + 8, (my + slope * dd + ty(dd)) / 2 + 4, "Bullet drop", 13, RED, "start", "bold"))
    b.append(text(xd + 8, (my + slope * dd + ty(dd)) / 2 + 20, "(gravity pulls it off the barrel line)", 12, MUTE, "start"))
    # holdover
    dh = 480
    xh = mx + dh * ppm
    b.append(f"<path d='M{xh:.0f},{los + 6} L{xh:.0f},{ty(dh) - 6:.0f}' stroke='{INK}' stroke-width='1.5' marker-start='url(#ah)' marker-end='url(#ah)'/>")
    b.append(lines(xh + 8, (los + ty(dh)) / 2 + 4, ["Past zero:", "hold over"], 12, INK, "start", "bold"))
    b.append(text(W / 2, 420, "The round never rises above the barrel line: it crosses the sight line twice because the barrel points up.", 13, MUTE))
    return svg(W, H, "\n".join(b), "Bullet path: line of sight, line of departure, the bullet's path crossing the line of sight twice, zero range and bullet drop")


def terrain_hand():
    W, H = 880, 700
    b = [title(W, "YOUR FIST IS A MAP  -  the terrain features on one hand",
               "Make a fist, knuckles up: picture each part as ground")]
    skin, edge = "#e9d3b0", "#8a6d45"
    # ---- fist, seen from the front with the knuckles on top
    fx, fy, fw = 290, 150, 46
    b.append(f"<rect x='{fx - 6}' y='{fy + 160}' width='{4 * fw + 12}' height='90' fill='{skin}' stroke='{edge}' stroke-width='2'/>")  # wrist
    for i in range(4):
        x = fx + i * fw
        top = fy + (6 if i in (0, 3) else 0) + (10 if i == 3 else 0)
        b.append(f"<rect x='{x}' y='{top}' width='{fw}' height='{fy + 175 - top}' rx='22' fill='{skin}' stroke='{edge}' stroke-width='2'/>")
        b.append(f"<path d='M{x + 8},{top + 62} Q{x + fw / 2},{top + 70} {x + fw - 8},{top + 62}' fill='none' stroke='{edge}' stroke-width='1.5'/>")
    b.append(f"<rect x='{fx - 14}' y='{fy + 112}' width='{3 * fw + 10}' height='44' rx='22' fill='{skin}' stroke='{edge}' stroke-width='2'/>")  # thumb
    b.append(f"<path d='M{fx + 4 * fw},{fy + 22} L{fx + 4 * fw + 22},{fy + 40} L{fx + 4 * fw + 22},{fy + 230} L{fx + 4 * fw + 6},{fy + 250}' "
             f"fill='#d8bd95' stroke='{edge}' stroke-width='2'/>")  # flat side
    # labels
    kx = [fx + fw / 2 + i * fw for i in range(4)]
    b.append(f"<path d='M{fx},{fy - 14} L{fx},{fy - 26} L{fx + 4 * fw},{fy - 26} L{fx + 4 * fw},{fy - 14}' fill='none' stroke='{INK}' stroke-width='2'/>")
    b.append(text(fx + 2 * fw, fy - 36, "RIDGE  -  the row of knuckles: a line of high ground", 13, INK, weight="bold"))
    b.append(arrow(f"M{fx + 4 * fw + 120},{fy + 4} L{kx[3] + 6},{fy + 12}", INK, 1.8))
    b.append(text(fx + 4 * fw + 126, fy + 8, "HILL  -  one knuckle top", 13, INK, "start", "bold"))
    b.append(arrow(f"M{fx + 4 * fw + 120},{fy + 44} L{fx + 2 * fw + 2},{fy + 6}", INK, 1.8))
    b.append(text(fx + 4 * fw + 126, fy + 48, "SADDLE  -  the dip between two knuckles", 13, INK, "start", "bold"))
    b.append(arrow(f"M{fx + 4 * fw + 120},{fy + 124} L{fx + 4 * fw + 24},{fy + 130}", INK, 1.8))
    b.append(lines(fx + 4 * fw + 126, fy + 120, ["CLIFF  -  the flat side of the fist:", "near-vertical ground"], 13, INK, "start"))
    b.append(arrow(f"M{fx - 104},{fy + 46} L{kx[0] - 4},{fy + 70}", INK, 1.8))
    b.append(lines(fx - 110, fy + 40, ["SPUR  -  a finger running", "down from a knuckle"], 13, INK, "end"))
    b.append(arrow(f"M{fx - 104},{fy + 112} L{fx + fw},{fy + 92}", INK, 1.8))
    b.append(lines(fx - 110, fy + 106, ["DRAW  -  the groove", "between two fingers,", "down from a saddle"], 13, INK, "end"))
    # ---- open hands: valley and depression
    def open_hand(cx, cy, cupped):
        s = []
        lens = (74, 86, 82, 66)
        for i, ln in enumerate(lens):
            x = cx - 60 + i * 34
            s.append(f"<rect x='{x}' y='{cy - 70 - ln}' width='30' height='{ln + 30}' rx='15' fill='{skin}' stroke='{edge}' stroke-width='2'"
                     + (f" transform='rotate({(i - 1.5) * 6} {x + 15} {cy - 40})'" if not cupped else "") + "/>")
        s.append(f"<rect x='{cx - 66}' y='{cy - 60}' width='140' height='120' rx='34' fill='{skin}' stroke='{edge}' stroke-width='2'/>")
        s.append(f"<rect x='{cx + 50}' y='{cy - 20}' width='66' height='28' rx='14' fill='{skin}' stroke='{edge}' stroke-width='2' "
                 f"transform='rotate(-35 {cx + 56} {cy - 6})'/>")
        if cupped:
            s.append(ellipse(cx + 4, cy, 42, 32, "#c9a97e", edge, 1.5))
            s.append(ellipse(cx + 4, cy, 24, 16, "#b38f62", "none", 0))
        else:
            s.append(f"<path d='M{cx + 4},{cy + 50} C{cx - 6},{cy + 10} {cx + 14},{cy - 20} {cx + 4},{cy - 70}' fill='none' stroke='{BLUE}' stroke-width='3'/>")
            s.append(arrow(f"M{cx + 4},{cy + 30} L{cx + 4},{cy + 72}", BLUE, 2.5))
        return "".join(s)
    b.append(line(40, 440, W - 40, 440, GRID, 2))
    b.append(text(W / 2, 470, "Now open the hand", 14, INK, weight="bold"))
    b.append(open_hand(150, 600, False))
    b.append(lines(290, 556, ["VALLEY  -  hand flat,", "fingers spread. High", "ground on three sides;", "water runs out the", "open end."], 13, INK, "start"))
    b.append(open_hand(580, 600, True))
    b.append(lines(720, 556, ["DEPRESSION  -", "hand cupped. Low", "ground with high", "ground all round:", "water stays in."], 13, INK, "start"))
    return svg(W, H, "\n".join(b), "Terrain features on a hand: knuckles are hills on a ridge, the dips saddles, fingers spurs, grooves draws, the flat side a cliff; an open hand a valley and a cupped hand a depression")


# ---------------------------------------------------------------- tactical movement

def crossing_large_open_area():
    W, H = 880, 700
    b = [title(W, "CROSSING A LARGE OPEN AREA", "Too big to go round in the time you have")]
    b.append(wood(20, 70, 840, 130, 3))
    b.append(wood(20, 520, 360, 160, 5))
    b.append(wood(500, 520, 360, 160, 7))
    b.append(f"<rect x='20' y='200' width='840' height='320' fill='{FIELD}' opacity='.55'/>")
    # road through the near part of the open area
    b.append(f"<path d='M20,470 C220,456 640,476 860,456' fill='none' stroke='{INK}' stroke-width='14'/>")
    b.append(f"<path d='M20,470 C220,456 640,476 860,456' fill='none' stroke='#fff' stroke-width='9'/>")
    b.append(text(60, 498, "ROAD", 13, INK, "start", "bold"))
    b.append(text(690, 270, "LARGE OPEN AREA", 15, MUTE, weight="bold"))
    sx = 440
    b.append(unit_box(sx, 600, 48, 30))
    b.append(text(sx + 40, 606, "SQUAD", 13, INK, "start", "bold"))
    b.append(rally(sx, 660, "Near-side rally point"))
    # traveling overwatch
    b.append(f"<rect x='{sx - 22}' y='330' width='44' height='250' fill='{GREEN}' opacity='.18'/>")
    b.append(arrow(f"M{sx},580 L{sx},336", GREEN, 4))
    b.append(text(sx - 32, 548, "TRAVELING OVERWATCH", 13, GREEN, "end", "bold"))
    # 250 m line
    b.append(line(60, 330, 820, 330, RED, 1.5, "8 6"))
    b.append(text(816, 322, "about 250 m from the far side: small-arms range", 12, RED, "end", "bold"))
    # bounding
    for side in (-1, 1):
        pts = [(sx + side * 30, 324), (sx + side * 70, 284), (sx + side * 80, 238), (sx + side * 70, 190)]
        for i, (x, y) in enumerate(pts[1:]):
            b.append(arrow(f"M{pts[i][0]},{pts[i][1]} L{x},{y + (14 if i < 2 else 12)}", BLUE, 3, "7 4"))
            b.append(man(x, y, BLUE, -90))
    b.append(text(sx, 214, "BOUNDING", 13, BLUE, weight="bold"))
    b.append(text(sx, 230, "OVERWATCH", 13, BLUE, weight="bold"))
    b.append(rally(sx, 120, "Far-side rally point", "top"))
    # notes
    b.append(lines(40, 236, ["Teams bound into the wood line", "and clear room for the", "whole squad, then re-form."], 13, INK, "start"))
    b.append(lines(560, 390, ["Open the gaps between", "teams and between men."], 13, INK, "start"))
    b.append(arrow(f"M556,386 L{sx + 28},400", INK, 1.5))
    b.append(lines(40, 352, ["The road is a danger area inside", "a danger area: cross it in", "traveling overwatch, do NOT", "clear it as a separate", "linear danger area."], 13, INK, "start"))
    return svg(W, H, "\n".join(b), "Crossing a large open area: traveling overwatch across, bounding overwatch inside 250 metres of the far side")


def detour_bypass():
    W, H = 880, 640
    b = [title(W, "SMALL OPEN AREAS  -  go round, don't cross",
               "Both routes start at a near-side rally point and pick the azimuth up again at the far side")]
    for k, (name, seed) in enumerate((("CONTOUR AROUND IT", 11), ("DETOUR BYPASS", 13))):
        ox = 30 + k * 430
        b.append(wood(ox, 100, 390, 420, seed))
        b.append(f"<path d='M{ox + 130},{180} C{ox + 90},{260} {ox + 110},{380} {ox + 150},{440} "
                 f"C{ox + 200},{470} {ox + 260},{430} {ox + 270},{360} C{ox + 290},{280} {ox + 260},{190} {ox + 200},{170} "
                 f"C{ox + 170},{162} {ox + 145},{166} {ox + 130},{180} z' fill='{FIELD}' stroke='{WOOD_EDGE}' stroke-width='2'/>")
        b.append(text(ox + 195, 310, "SMALL", 13, MUTE, weight="bold"))
        b.append(text(ox + 195, 326, "OPEN AREA", 13, MUTE, weight="bold"))
        az = ox + 195
        b.append(line(az, 140, az, 260, MUTE, 2, "8 6"))
        b.append(line(az, 340, az, 540, MUTE, 2, "8 6"))
        b.append(unit_box(az, 570, 40, 26))
        b.append(rally(az - 56, 570, "Near side", "left"))
        b.append(rally(az, 122, "Far-side rally point", "right" if k == 0 else "left"))
        if k == 0:
            b.append(arrow(f"M{az},556 C{az - 40},500 {ox + 64},420 {ox + 66},320 C{ox + 66},220 {az - 70},150 {az - 14},126", GREEN, 3.5))
            b.append(lines(ox + 195, 610, ["Stay inside the wood line on the side with", "the better distance, cover and concealment"], 12, INK))
        else:
            r = ox + 335
            b.append(arrow(f"M{az},556 L{az},500 L{r},500 L{r},150 L{az + 14},150 L{az},132", GREEN, 3.5))
            b.append(text(az + 70, 490, "1  turn 90°", 12, INK, "middle", "bold"))
            b.append(f"<text x='{r + 20}' y='330' transform='rotate(90 {r + 20} 330)' text-anchor='middle' {FONT} font-size='12' font-weight='bold' fill='{INK}'>2  back on the direction of travel</text>")
            b.append(text(az + 70, 142, "3  turn 90° back", 12, INK, "middle", "bold"))
            b.append(lines(ox + 195, 610, ["Only leg 2 counts toward the pace count:", "the offset legs 1 and 3 cancel out"], 12, INK))
        b.append(text(ox + 195, 86, name, 15, INK, weight="bold"))
    b.append(arrow("M455,560 L455,470", MUTE, 6))
    b.append(lines(455, 586, ["direction", "of travel"], 12, MUTE))
    return svg(W, H, "\n".join(b), "Small open areas: contour around inside the wood line, or detour bypass with two 90-degree turns")


def build():
    for sub, name, fn in (
            ("fires", "clock-method", clock_method),
            ("fires", "maximum-ordinate", maximum_ordinate),
            ("fires", "cone-beaten-zone-danger-space", cone_beaten_zone),
            ("fires", "grazing-plunging-fire", grazing_plunging),
            ("fires", "fire-target-classes", target_classes),
            ("fires", "gunner-view-frontal-flanking", gunner_view_frontal_flanking),
            ("fires", "gunner-view-oblique-enfilade", gunner_view_oblique_enfilade),
            ("fires", "fire-manipulation", fire_manipulation),
            ("fires", "speed-estimation", speed_estimation),
            ("fires", "vehicle-kill-types", kill_types),
            ("fires", "light-anti-armor-aimpoints", aimpoints),
            ("fires", "work-in-progress", work_in_progress),
            ("fires", "bullet-path", bullet_path),
            ("landnav", "terrain-features-hand", terrain_hand),
            ("movement", "crossing-large-open-area", crossing_large_open_area),
            ("movement", "detour-bypass", detour_bypass)):
        write(sub, name, fn())


if __name__ == "__main__":
    build()
