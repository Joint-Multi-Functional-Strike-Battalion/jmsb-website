"""Combat skills page, second half: ambushes, urban street patterns and terrain matrix, room clearing, vehicle formations and dismounts."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiver_draw import *  # noqa: E402,F401,F403

SUB = "combat"
ORANGE = "#ef6c00"
WALL = 4


# ---------------------------------------------------------------- helpers

def zone(x, y, w, h, label="KILL ZONE"):
    """The kill zone: a dashed red box with its name in the middle."""
    return (box(x, y, w, h, "none", RED, 3, 6, "10 7")
            + text(x + w / 2, y + h / 2 + 5, label, 14, RED, weight="bold"))


def fan(x, y, facing, r, half, colour=GREEN):
    return wedge(x, y, facing, r, half, colour, .13)


def team(x, y, facing, label="Team"):
    """A fire team on the ambush line: an infantry symbol with the way it fires."""
    return unit_box(x, y, 48, 32) + text(x, y - 24 if facing > 0 else y + 34, label, 12, INK, weight="bold")


def sector(x, y, pts, colour, op=.18):
    """A sector of fire as a polygon from the man out to points on the walls."""
    d = f"M{x},{y} " + " ".join(f"L{px:.0f},{py:.0f}" for px, py in pts) + " z"
    return f"<path d='{d}' fill='{colour}' opacity='{op}' stroke='{colour}' stroke-width='1.5'/>"


def room(x, y, w, h, door_x, door_w=36):
    """Four walls seen from above with a gap for the door in the bottom wall."""
    s = [f"<path d='M{door_x - door_w / 2},{y + h} L{x},{y + h} L{x},{y} L{x + w},{y} L{x + w},{y + h} L{door_x + door_w / 2},{y + h}' "
         f"fill='#fafaf7' stroke='{INK}' stroke-width='{WALL}' stroke-linejoin='miter'/>"]
    return "".join(s)


def angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


# ---------------------------------------------------------------- ambushes

def ambush_linear():
    W, H = 820, 470
    b = [title(W, "LINEAR AMBUSH  -  the teams in one line, all firing into the kill zone",
               "Simple to set and to control. The enemy is hit from one side.")]
    b.append(f"<rect x='40' y='300' width='740' height='70' fill='{GROUND}' opacity='.45'/>")
    b.append(text(60, 390, "road / trail", 12, MUTE, "start"))
    for x in (210, 410, 610):
        b.append(fan(x, 120, 90, 270, 25))
    b.append(zone(120, 285, 580, 100))
    for x in (210, 410, 610):
        b.append(team(x, 110, -90))
    b.append(arrow("M60,338 L150,338", RED, 3))
    b.append(text(60, 326, "enemy", 12, RED, "start", "bold"))
    b.append(lines(W / 2, 425, ["Each team has its own slice of the kill zone; the slices touch so nothing gets through.",
                                "Ground on the far side that offers the enemy shelter is mined or covered by mortars."], 13, MUTE))
    return svg(W, H, "".join(b), "Linear ambush: three teams in one line, each firing straight into the kill zone in front")


def ambush_l():
    W, H = 820, 500
    b = [title(W, "L AMBUSH  -  a long leg fires across the kill zone, a short leg fires along it",
               "The short leg rakes the column from end to end.")]
    zx, zy, zw, zh = 300, 190, 380, 110
    for x in (400, 580):
        b.append(fan(x, 110, 90, 240, 22))
    b.append(fan(130, 245, 0, 600, 9))
    b.append(zone(zx, zy, zw, zh))
    for x in (400, 580):
        b.append(team(x, 100, -90))
    b.append(unit_box(105, 245, 48, 32) + text(105, 285, "Team", 12, INK, weight="bold"))
    b.append(text(490, 145, "LONG LEG fires across", 12, GREEN, weight="bold"))
    b.append(text(210, 232, "SHORT LEG fires along", 12, GREEN, weight="bold"))
    # enemy approaches
    b.append(arrow("M800,245 L700,245", RED, 4))
    b.append(text(800, 230, "enemy", 12, RED, "end", "bold"))
    b.append(arrow("M490,440 L490,320", RED, 4))
    b.append(text(500, 430, "enemy", 12, RED, "start", "bold"))
    b.append(text(W / 2, 480, "Arrows: the ways the enemy can come into the kill zone.", 13, MUTE))
    return svg(W, H, "".join(b), "L ambush: two teams fire across the kill zone and a third team at the end fires along it")


def ambush_lazy_v():
    W, H = 820, 560
    b = [title(W, "LAZY V AMBUSH  -  teams on the arms of a wide V, fire meeting in the middle",
               "Whichever way the enemy comes in, he is under fire from more than one side.")]
    cx, cy = 410, 280
    teams = [(410, 100), (170, 440), (650, 440)]
    for x, y in teams:
        f = angle(x, y, cx, cy)
        b.append(fan(x, y, f, math.hypot(cx - x, cy - y) + 110, 16))
    b.append(zone(cx - 160, cy - 55, 320, 110))
    for x, y in teams:
        b.append(unit_box(x, y, 48, 32))
    b.append(text(410, 76, "Team", 12, INK, weight="bold"))
    b.append(text(170, 480, "Team", 12, INK, weight="bold"))
    b.append(text(650, 480, "Team", 12, INK, weight="bold"))
    b.append(arrow("M40,280 L230,280", RED, 4))
    b.append(arrow("M780,280 L590,280", RED, 4))
    b.append(arrow("M410,540 L410,355", RED, 4))
    b.append(text(40, 266, "enemy", 12, RED, "start", "bold"))
    b.append(text(780, 266, "enemy", 12, RED, "end", "bold"))
    b.append(text(420, 530, "enemy", 12, RED, "start", "bold"))
    return svg(W, H, "".join(b), "Lazy V ambush: three teams on a wide V, all firing into the kill zone between them")


# ---------------------------------------------------------------- urban

def _pict(kind, cx, cy):
    """A small street-pattern pictogram: built-up blocks in olive, streets in white."""
    o = []
    st = "stroke='#fff' stroke-width='3' fill='none' stroke-linecap='round'"
    if kind == "grid":
        for i in range(4):
            for j in range(4):
                o.append(f"<rect x='{cx - 34 + i * 17.5}' y='{cy - 34 + j * 17.5}' width='15' height='15' fill='{OLIVE}'/>")
    elif kind == "rayed":
        fx, fy = cx - 26, cy
        pts = [(fx + 54 * math.cos(math.radians(a)), fy + 54 * math.sin(math.radians(a))) for a in range(-50, 51, 10)]
        o.append(f"<path d='M{fx},{fy} " + " ".join(f"L{x:.0f},{y:.0f}" for x, y in pts) + f" z' fill='{OLIVE}'/>")
        for a in range(-40, 41, 20):
            r = math.radians(a)
            o.append(f"<path d='M{fx},{fy} L{fx + 56 * math.cos(r):.0f},{fy + 56 * math.sin(r):.0f}' {st}/>")
    elif kind in ("radial", "ring", "combined"):
        n = 8 if kind != "combined" else 6
        rr = 36
        pts = [(cx + rr * math.cos(math.radians(22.5 + i * 360 / n)), cy + rr * math.sin(math.radians(22.5 + i * 360 / n)))
               for i in range(n)]
        if kind == "combined":
            pts = [(cx + rr * math.cos(math.radians(i * 60)), cy + rr * math.sin(math.radians(i * 60))) for i in range(6)]
        o.append("<path d='M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + f" z' fill='{OLIVE}'/>")
        if kind in ("radial", "ring"):
            for i in range(8):
                r = math.radians(i * 45)
                o.append(f"<path d='M{cx},{cy} L{cx + 36 * math.cos(r):.0f},{cy + 36 * math.sin(r):.0f}' {st}/>")
        if kind == "ring":
            for rad in (11, 22):
                o.append(f"<circle cx='{cx}' cy='{cy}' r='{rad}' {st}/>")
        if kind == "combined":
            # grid on the left half, rays on the right half
            for x in (cx - 24, cx - 12):
                o.append(f"<path d='M{x},{cy - 30} L{x},{cy + 30}' {st}/>")
            for y in (cy - 14, cy, cy + 14):
                o.append(f"<path d='M{cx - 30},{y} L{cx},{y}' {st}/>")
            for a in (-60, -20, 20, 60):
                r = math.radians(a)
                o.append(f"<path d='M{cx},{cy} L{cx + 34 * math.cos(r):.0f},{cy + 34 * math.sin(r):.0f}' {st}/>")
            o.append(f"<path d='M{cx},{cy - 31} L{cx},{cy + 31}' {st}/>")
    elif kind == "contour":
        o.append(f"<rect x='{cx - 34}' y='{cy - 34}' width='68' height='68' fill='{OLIVE}'/>")
        o.append(f"<path d='M{cx - 34},{cy - 34} L{cx + 10},{cy - 34} C{cx - 2},{cy - 16} {cx - 22},{cy - 6} {cx - 34},{cy + 2} z' fill='#a89a72'/>")
        for k in (0, 12, 24):
            o.append(f"<path d='M{cx - 34},{cy + 12 + k} C{cx - 14},{cy - 4 + k} {cx + 6},{cy - 22 + k} {cx + 34},{cy - 30 + k}' {st}/>")
        o.append(f"<path d='M{cx - 4},{cy + 34} L{cx - 14},{cy + 2}' {st}/>")
        o.append(f"<path d='M{cx + 20},{cy + 34} L{cx + 10},{cy - 14}' {st}/>")
    elif kind == "irregular":
        o.append(f"<path d='M{cx - 30},{cy - 26} C{cx - 10},{cy - 40} {cx + 26},{cy - 38} {cx + 34},{cy - 12} "
                 f"C{cx + 40},{cy + 14} {cx + 22},{cy + 38} {cx - 4},{cy + 34} C{cx - 30},{cy + 34} {cx - 42},{cy + 6} {cx - 30},{cy - 26} z' fill='{OLIVE}'/>")
        o.append(f"<path d='M{cx - 30},{cy - 8} C{cx - 10},{cy - 18} {cx + 6},{cy + 10} {cx + 34},{cy - 2}' {st}/>")
        o.append(f"<path d='M{cx - 8},{cy - 36} C{cx - 2},{cy - 10} {cx - 18},{cy + 10} {cx - 4},{cy + 34}' {st}/>")
        o.append(f"<path d='M{cx + 6},{cy + 4} C{cx + 14},{cy + 14} {cx + 14},{cy + 20} {cx + 8},{cy + 26}' {st}/>")
        o.append(f"<circle cx='{cx + 8}' cy='{cy + 27}' r='4' fill='#fff'/>")
        o.append(f"<path d='M{cx + 12},{cy - 34} C{cx + 14},{cy - 22} {cx + 22},{cy - 18} {cx + 30},{cy - 20}' {st}/>")
    elif kind == "linear":
        o.append(f"<rect x='{cx - 36}' y='{cy - 3}' width='72' height='6' fill='{MUTE}'/>")
        for i, (w, h) in enumerate(((10, 18), (14, 12), (8, 22), (12, 14), (10, 20))):
            x = cx - 36 + i * 15
            o.append(f"<rect x='{x}' y='{cy - 7 - h}' width='{w}' height='{h}' fill='{OLIVE}'/>")
        for i, (w, h) in enumerate(((12, 14), (8, 20), (14, 10), (10, 18), (9, 12))):
            x = cx - 36 + i * 15
            o.append(f"<rect x='{x}' y='{cy + 7}' width='{w}' height='{h}' fill='{OLIVE}'/>")
    return "".join(o)


def street_patterns():
    W = 860
    rows = [
        ("grid", "Rectangular\n(chessboard)", "Straight streets crossing at right angles, making a grid of blocks.\nEasy to navigate; long, straight fields of fire down every street."),
        ("rayed", "Rayed", "Streets fan out from one focal point, but through less than a full circle.\nEvery street leads back to the same place."),
        ("radial", "Radial", "Main roads spread out from a centre like spokes - all the way round,\nor through an arc when a coast or river blocks one side."),
        ("ring", "Radial-ring", "Rings of road, each bigger than the last, crossed by spokes from the centre.\nUsually part of a larger radial layout."),
        ("contour", "Contour-\nfollowing", "Steep ground decides the roads: main streets run along the slope,\nshort steep links connect them."),
        ("irregular", "Irregular", "No geometric plan, by design. Curving streets and dead ends\n(a modern housing estate is a typical example). Easy to get lost."),
        ("combined", "Combined", "A mix of the patterns above - often an old town centre ringed\nby newer high-rise and business districts."),
        ("linear", "Linear", "One main road down the middle with buildings strung along both sides,\nlike a strip mall or a village high street."),
    ]
    cols = [("Shape", 110), ("Pattern", 140), ("What it means", 570)]
    x0, y0, rh = 20, 70, 86
    t, h = table(x0, y0, cols, [["", p, e] for _, p, e in rows], 13, row_h=rh)
    b = [title(W, "STREET PATTERNS", "How a town's streets are laid out shapes how you move and fight through it"), t]
    hh = 13 * 2.4
    for i, (kind, _, _) in enumerate(rows):
        b.append(_pict(kind, x0 + 55, y0 + hh + i * rh + rh / 2))
    return svg(W, y0 + h + 20, "".join(b), "Street patterns: rectangular, rayed, radial, radial-ring, contour-following, irregular, combined and linear, with a pictogram and the effect of each")


def terrain_matrix():
    W = 940
    N = "   "

    def c(*items):
        out = []
        for it in items:
            parts = it.split("|")
            out.append("• " + parts[0])
            out += [N + p for p in parts[1:]]
        return "\n".join(out)

    zones = ["City\ncore", "Core\nperiphery", "Dispersed\nresidential", "High-rise\narea", "Industrial /\ntransport", "Fortified\narea"]
    rows = [
        ["Observation\nand fields\nof fire (O)",
         c("Buildings 15-20|storeys", "Short sightlines|cut weapon range", "Street lights can|spoil NVGs"),
         c("Buildings 5-10|storeys", "Wider view and|longer sightlines", "Building types|easier to tell apart"),
         c("Lighting can|spoil NVGs", "Mostly 1-2|storeys"),
         c("Flats and offices,|10-50 storeys", "Medium to long|sightlines"),
         c("Fires and smoke|can block view", "Many open areas"),
         c("Defender has|the edge", "Observation posts|already in place")],
        ["Cover and\nconcealment\n(C)",
         c("Mixed commercial|buildings and|build types", "Best cover in|the town"),
         c("Tight rows or|joined houses", "Mixed build types", "Cover may run|short"),
         c("Lightly built|houses"),
         c("Big open spaces|next to towers", "Framed heavy and|light-clad builds"),
         c("Stock and cargo|give many positions", "Framed, light-clad,|some brick"),
         c("Little for the|attacker, hardened|for the defender")],
        ["Obstacles\n(O)",
         c("Many civilian|vehicles"),
         c("Many civilian|vehicles"),
         c("Power lines, poles|and masts are a|danger to aircraft", "More civilians"),
         c("Stairwells can be|hard to reach"),
         c("Fuel, explosives|and chemicals can|set off secondary|blasts"),
         c("Altered buildings|limit access", "Obstacles covered|by fire")],
        ["Key terrain\n(K)\n\nCan be found\nin every zone",
         c("Radio, TV and|phone exchanges", "Utilities, subway", "Junctions", "Government|centre"),
         c("Water and sewers", "Bridges, stadiums", "Hospitals, parks"),
         c("Main road network", "Schools, churches,|town halls", "Community centres", "Helipads"),
         c("Banking centre"),
         c("Chemical plants", "Rail control centre", "Truck depots"),
         c("Few or none inside;|look in the area|around it")],
        ["Avenues of\napproach\n(A)",
         c("Streets ~26 m wide", "Heavy traffic", "Grid of streets", "Best for mounted|movement"),
         c("Narrow, winding|streets", "Joined buildings|give rooftop routes", "Tunnels and|basements"),
         c("Streets ~14 m wide", "Houses 6-8 m back|from tree lines", "Grid or curved|streets"),
         c("Tall buildings|limit air routes"),
         c("Along main roads|and highways", "Flat roofs and|yards make LZs"),
         c("Channelled and|covered by fire")],
    ]
    cols = [("Factor", 130)] + [(z, 128) for z in zones]
    t, h = table(20, 70, cols, rows, 12)
    b = [title(W, "URBAN TERRAIN ANALYSIS (OCOKA) BY ZONE", "What each kind of town district gives you - and the enemy"), t]
    return svg(W, 70 + h + 20, "".join(b), "Urban terrain analysis matrix: observation, cover, obstacles, key terrain and avenues of approach for six kinds of urban zone")


# ---------------------------------------------------------------- room clearing

RW, RH = 340, 210
COL = {1: GREEN, 2: BLUE, 3: RED, 4: ORANGE}


def layout(kind, x, y):
    """Door, points of domination and sectors for a room at x, y.
    kind 'centre' = door in the middle of the wall, 'corner' = door near the left corner."""
    if kind == "centre":
        dx = x + RW / 2
        pos = {1: (x + RW - 22, y + RH - 22, -110), 2: (x + 22, y + RH - 22, -70),
               3: (dx + 75, y + RH - 24, -90), 4: (dx - 75, y + RH - 24, -90)}
        sec = {1: [(x + RW - 8, y), (x, y)], 2: [(x + 8, y), (x + RW, y)],
               3: [(x + RW / 2 - 20, y), (x + RW, y), (x + RW, y + RH * .3)],
               4: [(x, y + RH * .3), (x, y), (x + RW / 2 + 20, y)]}
    else:
        dx = x + 44
        pos = {1: (x + RW * .62, y + RH - 22, -60), 2: (x + 22, y + RH * .22, 10),
               3: (x + RW * .34, y + RH - 22, -90), 4: (x + 22, y + RH * .55, -10)}
        sec = {1: [(x + RW * .82, y), (x + RW, y), (x + RW, y + RH)],
               2: [(x + RW, y), (x + RW, y + RH * .6)],
               3: [(x + RW * .12, y), (x + RW * .75, y)],
               4: [(x + RW, y + RH * .45), (x + RW, y + RH)]}
    return dx, pos, sec


def entry_panel(kind, x, y, who, show=None, sectors=None, mute_others=True):
    """One room. `who` = the man moving now (path drawn), `show` = men already in, the rest stack outside."""
    show = show or []
    sectors = sectors if sectors is not None else ([who] if who else [])
    dx, pos, sec = layout(kind, x, y)
    o = [room(x, y, RW, RH, dx)]
    for n in sectors:
        px, py, _ = pos[n]
        o.append(sector(px, py, sec[n], COL[n], .18 if len(sectors) == 1 else .12))
    # men still outside, in a stack along the wall
    outside = [n for n in (1, 2, 3, 4) if n not in show and n != who]
    for i, n in enumerate(outside):
        if kind == "centre":
            o.append(man(dx - 34 - i * 28, y + RH + 24, MUTE, 0, str(n)))
        else:
            o.append(man(dx + 34 + i * 28, y + RH + 24, MUTE, 180, str(n)))
    if who:
        px, py, _ = pos[who]
        inside = y + RH - 34
        o.append(arrow(f"M{dx},{y + RH + 26} L{dx},{inside} Q{dx},{(inside + py) / 2 if abs(py - inside) > 30 else py} "
                       f"{dx + (14 if px > dx else -14)},{py if abs(py - inside) <= 30 else (inside + py) / 2} "
                       f"L{px + (-16 if px > dx else 16) if abs(py - inside) <= 30 else px},{py + (0 if abs(py - inside) <= 30 else 18)}",
                       INK, 2, "6 4"))
    for n in show + ([who] if who else []):
        px, py, f = pos[n]
        c = COL[n] if (n == who or not mute_others or n in sectors) else MUTE
        o.append(man(px, py, c, f, str(n)))
    return "".join(o)


def man_enters(n, what):
    W = 800
    b = [title(W, f"No. {n} ENTERS", what[0])]
    before = list(range(1, n))
    for i, (kind, cap) in enumerate((("centre", "Door in the middle of the wall"), ("corner", "Door near a corner"))):
        x = 40 + i * 380
        b.append(entry_panel(kind, x, 84, n, before))
        b.append(text(x + RW / 2, 84 + RH + 62, cap, 13, INK, weight="bold"))
    b.append(lines(W / 2, 84 + RH + 92, what[1:], 13, MUTE))
    h = 84 + RH + 92 + 20 * len(what[1:]) + 4
    return svg(W, h, "".join(b), f"Number {n} man entering a room: his path and sector of fire, for a door in the middle of the wall and a door near a corner")


def domination(kind):
    W = RW + 80
    sub = "Door in the middle of the wall" if kind == "centre" else "Door near a corner"
    b = [text(W / 2, 30, "POINTS OF DOMINATION", 16, weight="bold"), text(W / 2, 52, sub, 13, MUTE)]
    b.append(entry_panel(kind, 40, 76, None, [1, 2, 3, 4], [1, 2, 3, 4], False))
    b.append(lines(W / 2, 76 + RH + 34, ["Every man in his spot, sectors overlapping.",
                                         "Nobody stands in front of a door or window."], 13, MUTE))
    return svg(W, 76 + RH + 70, "".join(b), f"Points of domination and overlapping sectors of fire for a four-man team, {sub.lower()}")


def two_man(kind):
    """Two-man clearing in three steps."""
    rw, rh = 250, 165
    W = 3 * (rw + 30) + 30
    sub = "door in the middle of the wall" if kind == "centre" else "door near a corner"
    b = [title(W, f"TWO-MAN CLEARING  -  {sub}", "No. 1 goes in and along his wall, No. 2 goes the other way, both end facing in")]
    if kind == "centre":
        p = {1: (rw - 22, rh - 22, -110), 2: (22, rh - 22, -70)}
        s = {1: [(rw * .04, 0), (rw * .97, 0)], 2: [(rw * .03, 0), (rw * .96, 0)]}
        dxr = rw / 2
    else:
        p = {1: (rw * .62, rh - 22, -80), 2: (22, rh * .2, 10)}
        s = {1: [(rw * .3, 0), (rw, 0), (rw, rh * .05)], 2: [(rw, 0), (rw, rh)]}
        dxr = 44
    caps = ["1. No. 1 goes in and along his wall", "2. No. 2 goes the other way", "3. Both in place, sectors crossing"]
    for step in range(3):
        x, y = 30 + step * (rw + 30), 84
        dx = x + dxr
        b.append(room(x, y, rw, rh, dx))
        movers = {0: [1], 1: [2], 2: []}[step]
        placed = {0: [], 1: [1], 2: [1, 2]}[step]
        if step == 2:
            for n in (1, 2):
                b.append(sector(x + p[n][0], y + p[n][1], [(x + a, y + c) for a, c in s[n]], COL[n]))
        for n in movers:
            px, py = x + p[n][0], y + p[n][1]
            if abs(py - (y + rh - 22)) < 5:
                d = f"M{dx},{y + rh + 26} L{dx},{y + rh - 22} L{px + (-16 if px > dx else 16)},{py}"
            else:
                d = f"M{dx},{y + rh + 26} L{dx},{y + rh - 34} Q{px},{y + rh - 34} {px},{y + rh - 60} L{px},{py + 18}"
            b.append(arrow(d, INK, 2, "6 4"))
            b.append(man(px, py, COL[n], p[n][2], str(n)))
        for n in placed:
            b.append(man(x + p[n][0], y + p[n][1], COL[n] if step == 2 else MUTE, p[n][2], str(n)))
        if step == 0:
            b.append(man(dx - 30 if kind == "centre" else dx + 30, y + rh + 24, MUTE, 0 if kind == "centre" else 180, "2"))
        b.append(text(x + rw / 2, y + rh + 62, caps[step], 13, INK, weight="bold"))
    return svg(W, 84 + rh + 80, "".join(b), f"Two-man room clearing, {sub}: number 1 enters and goes one way, number 2 the other, then both cover the room")


# ---------------------------------------------------------------- vehicles

def road(W, y, h=90):
    s = f"<rect x='0' y='{y}' width='{W}' height='{h}' fill='#cfcfcf'/>"
    s += f"<line x1='0' y1='{y + h / 2}' x2='{W}' y2='{y + h / 2}' stroke='#fff' stroke-width='4' stroke-dasharray='30 30'/>"
    return s


def travel(x, y):
    return arrow(f"M{x},{y} L{x + 150},{y}", INK, 5) + text(x, y - 12, "DIRECTION OF TRAVEL", 12, INK, "start", "bold")


def herringbone():
    W, H = 820, 510
    b = [title(W, "HERRINGBONE  -  pull off the road, alternate sides, angled out",
               "Used when the convoy halts in a hurry; the road stays clear and every side is covered")]
    ry = 220
    b.append(road(W, ry))
    b.append(travel(30, 465))
    cols = {1: RED, 2: GREEN, 3: BLUE, 4: INK}
    spots = {1: (690, 380, 40), 2: (530, 135, -40), 3: (330, 380, 40), 4: (170, 135, -40)}
    lane = {1: ry + 58, 2: ry + 32, 3: ry + 58, 4: ry + 32}
    for n, (vx, vy, f) in spots.items():
        a = math.radians(f)
        rx, ry2 = vx - 50 * math.cos(a), vy - 50 * math.sin(a)
        ly = lane[n]
        start = rx - (abs(ry2 - ly)) - 130
        b.append(arrow(f"M{start:.0f},{ly} L{rx - abs(ry2 - ly):.0f},{ly} L{rx:.0f},{ry2:.0f}", cols[n], 4))
        b.append(vehicle(vx, vy, f, TAN, str(n), 74, 40))
    b.append(text(W - 30, 470, "No. 1 (the lead) goes right, No. 2 left, and so on down the column.", 13, MUTE, "end"))
    return svg(W, H, "".join(b), "Herringbone: the vehicles pull off alternately to either side of the road, angled outward")


def coil():
    W, H = 820, 480
    b = [title(W, "COIL  -  the vehicles turn out to face every direction",
               "A tight all-round halt: front, rear and both flanks covered")]
    ry = 200
    b.append(road(W, ry))
    b.append(travel(30, 92))
    cx, cy = 400, ry + 45
    b.append(arrow(f"M{cx + 20},{cy} L{660},{cy}", RED, 4))
    b.append(vehicle(710, cy, 0, TAN, "1", 74, 40))
    b.append(arrow(f"M{cx - 10},{cy} Q{cx + 20},{cy} {cx + 20},{cy - 30} L{cx + 20},{cy - 80}", GREEN, 4))
    b.append(vehicle(cx + 20, cy - 125, -90, TAN, "2", 74, 40))
    b.append(arrow(f"M{cx - 40},{cy} Q{cx - 10},{cy} {cx - 10},{cy + 30} L{cx - 10},{cy + 80}", BLUE, 4))
    b.append(vehicle(cx - 10, cy + 125, 90, TAN, "3", 74, 40))
    b.append(arrow(f"M200,{cy + 22} L290,{cy + 22} C340,{cy + 22} 340,{cy - 20} 290,{cy - 20} L185,{cy - 20}", INK, 4))
    b.append(vehicle(140, cy - 20, 180, TAN, "4", 74, 40))
    b.append(text(W / 2, 466, "No. 1 keeps going and faces the front; 2 and 3 turn to the flanks; 4 turns round to face the rear.", 13, MUTE))
    return svg(W, H, "".join(b), "Coil: the lead vehicle faces forward, two turn to the flanks and the last turns round to face the rear")


def dismount(hard):
    W, H = 820, 470
    if hard:
        b = [title(W, "HARD DISMOUNT  -  everyone gets out", "Crews included: each vehicle's people fan out and cover all round")]
    else:
        b = [title(W, "SOFT DISMOUNT  -  drivers and gunners stay in", "Everyone else gets out and pulls 360 security around the vehicle")]
    ry = 190
    b.append(road(W, ry, 110))
    vs = [(230, GREEN), (590, BLUE)]
    cy = ry + 55
    for i, (vx, c) in enumerate(vs):
        b.append(vehicle(vx, cy, 0, TAN, "", 110, 58))
        if hard:
            angs = (-130, -60, 60, 130)
        else:
            angs = (-130, 130) if i == 0 else (-50, 50)
        for a in angs:
            r = math.radians(a)
            sx, sy = vx + 34 * math.cos(r), cy + 30 * math.sin(r)
            ex, ey = vx + 190 * math.cos(r), cy + 175 * math.sin(r)
            b.append(arrow(f"M{sx:.0f},{sy:.0f} L{ex - 22 * math.cos(r):.0f},{ey - 22 * math.sin(r):.0f}", c, 3))
            b.append(man(round(ex), round(ey), c, a))
        if not hard:
            b.append(lines(vx - 8, cy - 4, ["driver +", "gunner in"], 12, INK, weight="bold", gap=15))
    b.append(text(W / 2, 458, "Each man faces out, away from the vehicle, and covers his own arc.", 13, MUTE))
    alt = ("Hard dismount: everyone leaves both vehicles and takes up all-round security" if hard else
           "Soft dismount: drivers and gunners stay in, the rest get out and take up all-round security")
    return svg(W, H, "".join(b), alt)


# ---------------------------------------------------------------- build

MEN = {
    1: ["Through the door and along the wall to the near corner",
        "He takes the path of least resistance: away from the hinges if the door opens in, towards them if it opens out.",
        "He fires as he moves and stops in the corner, facing into the room."],
    2: ["Goes the opposite way to No. 1",
        "Right behind No. 1, he follows the other wall, stays out of the centre,",
        "clears his corner and stops facing in."],
    3: ["Goes the opposite way to No. 2",
        "He steps at least 1 m in from the door, clear of the funnel,",
        "and takes the spot that covers his sector."],
    4: ["Goes the opposite way to No. 3",
        "He takes the last spot and covers his sector.",
        "Not in front of a door or window - you would show against the light."],
}


def build():
    write(SUB, "ambush-linear", ambush_linear())
    write(SUB, "ambush-l", ambush_l())
    write(SUB, "ambush-lazy-v", ambush_lazy_v())
    write(SUB, "street-patterns", street_patterns())
    write(SUB, "urban-terrain-matrix", terrain_matrix())
    for n, word in ((1, "first"), (2, "second"), (3, "third"), (4, "fourth")):
        write(SUB, f"room-entry-{word}-man", man_enters(n, MEN[n]))
    write(SUB, "room-domination-centre-door", domination("centre"))
    write(SUB, "room-domination-corner-door", domination("corner"))
    write(SUB, "two-man-clearing-centre-door", two_man("centre"))
    write(SUB, "two-man-clearing-corner-door", two_man("corner"))
    write(SUB, "vehicle-herringbone", herringbone())
    write(SUB, "vehicle-coil", coil())
    write(SUB, "dismount-soft", dismount(False))
    write(SUB, "dismount-hard", dismount(True))
