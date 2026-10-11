"""Draws the Combat skills page's pictures from enfilade down to the formations, plus the danger-area crossing."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiver_draw import *  # noqa: E402,F401,F403

SUB = "combat"
FIRE, SHADE, COVER = "#fde68a", "#a5d6a7", "#9e9e94"


# ---------------------------------------------------------------- helpers

def move_dir(x, y1, y2, label="Direction of movement"):
    """Thick arrow pointing up with its label written along it."""
    mid = (y1 + y2) / 2
    return (line(x, y2, x, y1 + 14, INK, 5)
            + f"<path d='M{x - 10},{y1 + 18} L{x},{y1} L{x + 10},{y1 + 18} z' fill='{INK}'/>"
            + f"<text x='{x - 18}' y='{mid}' transform='rotate(-90 {x - 18} {mid})' text-anchor='middle' dominant-baseline='middle' "
              f"{FONT} font-size='13' fill='{INK}'>{esc(label)}</text>")


def cover(x, y, w=74, h=18):
    """A piece of cover seen from above, centred on x,y."""
    return (box(x - w / 2, y - h / 2, w, h, COVER, INK, 1, 3)
            + text(x, y + 4.5, "cover", 12, "#fff", weight="bold"))


def call(x, y, t, colour=INK, anchor="start"):
    """What a man shouts, in bold."""
    return text(x, y, t, 14, colour, anchor, "bold")


def enemy_line(w, y=66):
    return (text(w / 2, y - 8, "ENEMY", 13, RED, weight="bold")
            + line(30, y, w - 30, y, RED, 2, "8 6"))


def ring(x, y, n, colour=INK):
    """A small numbered circle for steps."""
    return (f"<circle cx='{x}' cy='{y}' r='10' fill='#fff' stroke='{colour}' stroke-width='2'/>"
            + text(x, y + 4.5, n, 12, colour, weight="bold"))


def team(points, colour, labels=None):
    labels = labels or {}
    return "".join(man(x, y, colour, -90, labels.get(i, "")) for i, (x, y) in enumerate(points))


def wedge_pts(cx, cy, s=34, strong=1):
    """Four men: point, two back to either side, the extra man further back on the strong side."""
    return [(cx, cy), (cx - s, cy + s), (cx + s, cy + s), (cx + 2 * s * strong, cy + 2 * s)]


def file_pts(cx, cy, s=40, n=4):
    return [(cx, cy + i * s) for i in range(n)]


def line_pts(cx, cy, s=48, n=4):
    x0 = cx - s * (n - 1) / 2
    return [(x0 + i * s, cy) for i in range(n)]


def side_shooter(x, g, colour=GREEN):
    """A kneeling rifleman seen from the side, facing right, knee on the ground line g. Returns (svg, muzzle)."""
    s = (f"<g fill='none' stroke='{colour}' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'>"
         f"<path d='M{x - 14},{g} L{x - 2},{g - 2} L{x},{g - 20}'/>"            # rear leg, knee down
         f"<path d='M{x},{g - 20} L{x + 14},{g - 18} L{x + 14},{g}'/>"          # front leg, foot planted
         f"<path d='M{x},{g - 20} L{x - 2},{g - 44}'/>"                          # back
         f"<path d='M{x - 2},{g - 40} L{x + 14},{g - 38}'/></g>"                 # arms to the rifle
         f"<circle cx='{x}' cy='{g - 52}' r='7' fill='{colour}'/>"
         + line(x - 6, g - 42, x + 30, g - 44, INK, 3))
    return s, (x + 30, g - 44)


# ---------------------------------------------------------------- enfilade / defilade

def enfilade_defilade():
    W, H = 860, 680
    b = [title(W, "ENFILADE AND DEFILADE",
               "Enfilade: ground your fire can sweep.  Defilade: ground the fire cannot reach.")]
    defs = []

    # panel A: a hill casts a fire shadow
    g, x0, x1 = 270, 20, 420
    hx, hrx, hry = 270, 70, 80
    terrain = f"M{x0},{g} L{hx - hrx},{g} A{hrx},{hry} 0 0 1 {hx + hrx},{g} L{x1},{g} L{x1},{g + 40} L{x0},{g + 40} z"
    sh, (mx, my) = side_shooter(55, g)
    # tangent from the muzzle to the hill top (sampled)
    best = None
    for i in range(0, 181):
        t = math.radians(180 - i)
        px, py = hx + hrx * math.cos(t), g - hry * math.sin(t)
        sl = (py - my) / (px - mx)
        if best is None or sl < best[0]:
            best = (sl, px, py)
    sl, tx, ty = best
    yr = my + sl * (x1 - mx)
    defs.append(f"<clipPath id='airA'><path d='M{x0},60 L{x1},60 L{x1},{g} L{hx + hrx},{g} A{hrx},{hry} 0 0 0 {hx - hrx},{g} L{x0},{g} z'/></clipPath>")
    b.append(f"<g clip-path='url(#airA)'>"
             f"<path d='M{mx},{my} L{x1},{yr:.0f} L{x1},{g} L{mx + 40},{g} z' fill='{FIRE}'/>"
             f"<path d='M{tx:.0f},{ty:.0f} L{x1},{yr:.0f} L{x1},{g} L{tx:.0f},{g} z' fill='{SHADE}'/></g>")
    b.append(line(mx, my, x1, yr, INK, 1.2, "5 4"))
    b.append(f"<path d='{terrain}' fill='{OLIVE}'/>")
    b.append(sh)
    b.append(text(hx, g - 22, "HILL", 15, "#fff", weight="bold"))
    b.append(text(170, g - 22, "swept", 14, INK, weight="bold"))
    b.append(text(375, g - 14, "defilade", 14, GREEN, weight="bold"))
    b.append(lines(220, g + 106, ["A rise hides the ground behind it.", "Fight from there and you are in defilade."], 13, MUTE))

    # panel B: a dip in the ground
    ox = 440
    g2, d1, d2, dry = 270, ox + 150, ox + 360, 70
    sh2, (mx2, my2) = side_shooter(ox + 35, g2)
    dc, drx = (d1 + d2) / 2, (d2 - d1) / 2
    defs.append(f"<clipPath id='airB'><path d='M{ox},60 L{ox + 400},60 L{ox + 400},{g2} L{d2},{g2} A{drx},{dry} 0 0 1 {d1},{g2} L{ox},{g2} z'/></clipPath>")
    sl2 = (g2 - my2) / (d1 - mx2)
    yfar = g2 + sl2 * (ox + 400 - d1)
    b.append(f"<g clip-path='url(#airB)'>"
             f"<path d='M{mx2},{my2} L{ox + 400},{my2 - 70} L{ox + 400},{g2 + 200} L{d1},{g2} z' fill='{FIRE}'/>"
             f"<path d='M{d1},{g2} L{ox + 400},{yfar:.0f} L{ox + 400},{g2 + 200} L{d1},{g2 + 200} z' fill='{SHADE}'/></g>")
    b.append(line(mx2, my2, d1 + 140, g2 + sl2 * 140, INK, 1.2, "5 4"))
    b.append(f"<path d='M{ox},{g2} L{d1},{g2} A{drx},{dry} 0 0 0 {d2},{g2} L{ox + 400},{g2} L{ox + 400},{g2 + 80} L{ox},{g2 + 80} z' fill='{OLIVE}'/>")
    b.append(sh2)
    b.append(text(ox + 330, 180, "swept", 14, INK, weight="bold"))
    b.append(text(d1 + 42, g2 + 50, "defilade", 13, GREEN, weight="bold"))
    b.append(lines(ox + 200, g2 + 106, ["A ditch or a dip: the fire passes over", "the near part of the bottom."], 13, MUTE))
    b.append(line(430, 80, 430, 380, GRID, 1.5))

    # panel C: enfilade, fire down the length of a position (from above)
    top = 420
    b.append(line(30, top, W - 30, top, GRID, 1.5))
    b.append(text(W / 2, top + 28, "Enfilade fire hits a line from its end, so one burst runs down the whole of it", 14, weight="bold"))
    ty0 = top + 100
    b.append(box(260, ty0 - 14, 420, 28, GROUND, INK, 1, 4))
    for i in range(6):
        b.append(man(290 + i * 72, ty0, RED, 90))
    b.append(text(470, ty0 - 34, "Enemy position", 13, RED, weight="bold"))
    # frontal shooter
    b.append(man(470, ty0 + 100, GREEN, -90))
    b.append(arrow(f"M470,{ty0 + 82} L470,{ty0 + 22}", GREEN, 2, "6 5"))
    b.append(lines(470, ty0 + 128, ["Frontal: the burst hits one man"], 13, MUTE))
    # enfilade shooter
    b.append(man(140, ty0, GREEN, 0))
    b.append(f"<ellipse cx='470' cy='{ty0}' rx='225' ry='22' fill='none' stroke='{GREEN}' stroke-width='2' stroke-dasharray='6 4'/>")
    b.append(arrow(f"M158,{ty0} L238,{ty0}", GREEN, 2.5))
    b.append(lines(140, ty0 + 40, ["Enfilade: the beaten", "zone lies along the line"], 13, GREEN, weight="bold"))

    body = "<defs>" + "".join(defs) + "</defs>" + "\n".join(b)
    return svg(W, H, body, "Enfilade and defilade: the ground behind a rise or in a dip is hidden from fire, and fire from the end of a line runs along it")


# ---------------------------------------------------------------- bounding

def bounding_leapfrog():
    W, H = 520, 660
    b = [title(W, "BOUNDING - cover to cover, one moves, one shoots"), enemy_line(W, 70)]
    pos = {1: (330, 560, RED), 2: (190, 580, GREEN), 3: (360, 450, RED),
           4: (180, 350, GREEN), 5: (350, 250, RED), 6: (200, 150, GREEN)}
    for n in (3, 4, 5, 6):
        x, y, c = pos[n]
        b.append(cover(x, y - 26))
    for a, z in ((1, 3), (2, 4), (3, 5), (4, 6)):
        x1, y1, c = pos[a]
        x2, y2, _ = pos[z]
        bend = 50 if c == RED else -50
        b.append(arrow(f"M{x1},{y1 - 14} C{x1 + bend},{y1 - 60} {x2 + bend},{y2 + 70} {x2},{y2 + 16}", c, 2))
    for n, (x, y, c) in pos.items():
        b.append(man(x, y, c, -90, str(n)))
    b.append(text(420, 590, "start", 13, MUTE))
    b.append(lines(W / 2, 616, ["Red and green leapfrog. Each bound ends behind cover,",
                                "and nobody moves until his buddy is set and firing."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Bounding: two men leapfrog forward from cover to cover, one moving while the other covers")


def bounding_first():
    W, H = 520, 660
    b = [title(W, "BOUNDING - the first two bounds"), enemy_line(W, 70)]
    b.append(wedge(360, 426, -90, 140, 16, RED, .12))
    b.append(cover(360, 400)); b.append(cover(170, 280)); b.append(cover(330, 170, 74)); b.append(cover(150, 130))
    b.append(arrow("M320,548 C390,520 380,470 362,444", RED, 2.2))
    b.append(arrow("M200,556 C150,480 160,360 170,322", GREEN, 2.2))
    b.append(man(310, 560, RED, -90)); b.append(man(205, 572, GREEN, -90))
    b.append(man(360, 426, RED, -90)); b.append(man(170, 306, GREEN, -90))
    b.append(call(380, 432, "SET!", RED)); b.append(call(190, 312, "SET!", GREEN))
    b.append(ring(410, 500, "1", RED)); b.append(ring(135, 440, "2", GREEN))
    b.append(text(40, 600, "1", 13, RED, "start", "bold"))
    b.append(lines(56, 600, ["Front man bounds to cover, starts covering fire, calls SET."], 13, INK, "start"))
    b.append(text(40, 628, "2", 13, GREEN, "start", "bold"))
    b.append(lines(56, 628, ["Only then does the next man bound to the next cover - SET."], 13, INK, "start"))
    return svg(W, H, "\n".join(b), "Bounding: the front man takes cover and starts covering fire, calls set, then the next man bounds")


def bounding_behind():
    W, H = 520, 660
    b = [title(W, "BOUNDING - cross BEHIND the man who is firing"), enemy_line(W, 70)]
    b.append(wedge(300, 400, -90, 300, 14, GREEN, .14))
    b.append(cover(300, 374)); b.append(cover(160, 274)); b.append(cover(410, 474)); b.append(cover(420, 170))
    b.append(text(300, 120, "his fire", 12, GREEN, weight="bold"))
    b.append(man(300, 400, GREEN, -90)); b.append(call(318, 418, "covering", GREEN))
    b.append(arrow("M402,512 C350,600 200,590 180,470 S165,340 162,318", RED, 2.4))
    b.append(man(410, 500, RED, -90)); b.append(call(428, 506, "MOVING!", RED))
    b.append(man(160, 300, RED, -90)); b.append(call(100, 336, "SET!", RED, "start"))
    b.append(lines(W / 2, 612, ["Call MOVING, then go round the back of the shooter -",
                                "never through his line of fire. In cover, firing: SET."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Bounding: the man moving calls moving and crosses behind the man covering, then calls set")


def bounding_crossing():
    W, H = 520, 620
    b = [title(W, "CROSSING - when you cannot get behind him"), enemy_line(W, 70)]
    b.append(wedge(215, 380, -90, 290, 14, RED, .14))
    b.append(cover(150, 216)); b.append(cover(215, 354)); b.append(cover(300, 450)); b.append(cover(420, 300))
    b.append(man(215, 380, RED, -90)); b.append(call(110, 410, "stops firing", RED, "start"))
    b.append(arrow("M296,462 C280,380 230,330 228,290 S195,256 172,248", GREEN, 2.4))
    b.append(man(300, 476, GREEN, -90)); b.append(call(320, 482, "CROSSING!", GREEN))
    b.append(man(150, 242, GREEN, -90))
    b.append(lines(W / 2, 560, ["Rock or wall in the way behind him? Call CROSSING first.",
                                "He holds fire until you are clear of his muzzle."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Crossing: if you cannot pass behind a shooter, call crossing so he holds fire while you pass in front")


# ---------------------------------------------------------------- movement techniques

def _march(W, gaps, sub, note, name):
    """Elements in a column moving right; gaps[i] = (pixels, label, broken)."""
    els = [("g", ["Trail Group"]), ("h", ["Medic, weapons", "(optional)"]), ("g", ["Group"]),
           ("h", ["Detachment", "leader"]), ("g", ["Lead Group"])]
    b = [title(W, name, sub)]
    y = 150
    x = 70
    xs = []
    for i, (kind, lab) in enumerate(els):
        xs.append(x)
        if i < len(gaps):
            x += gaps[i][0]
    for i, ((kind, lab), x) in enumerate(zip(els, xs)):
        if kind == "g":
            b.append(unit_box(x, y))
        else:
            b.append(unit_box(x, y, 28, 20))
        b.append(lines(x, y + 44, lab, 13, INK, weight="bold"))
    for i, (px, lab, broken) in enumerate(gaps):
        a, z = xs[i] + 30, xs[i + 1] - 30
        yy = y - 40
        if broken:
            m = (a + z) / 2
            b.append(arrow(f"M{m - 10},{yy} L{a},{yy}", INK, 1.5)); b.append(arrow(f"M{m + 10},{yy} L{z},{yy}", INK, 1.5))
            b.append(f"<path d='M{m - 10},{yy} L{m - 4},{yy - 8} L{m + 4},{yy + 8} L{m + 10},{yy}' fill='none' stroke='{INK}' stroke-width='1.5'/>")
        else:
            b.append(arrow(f"M{(a + z) / 2},{yy} L{a},{yy}", INK, 1.5)); b.append(arrow(f"M{(a + z) / 2},{yy} L{z},{yy}", INK, 1.5))
        b.append(text((a + z) / 2, yy - 10, lab, 13, INK, weight="bold"))
    b.append(arrow(f"M{xs[-1] + 40},{y} L{W - 20},{y}", INK, 4))
    b.append(lines(W / 2, 250, note, 13, MUTE))
    return b


def traveling():
    W = 820
    b = _march(W, [(150, "~20 m", False)] * 4, "Contact not likely - speed matters more than security",
               ["Men about 10 m apart inside each Group, about 20 m between elements.",
                "Fastest and least dispersed of the three techniques - and the least secure."], "TRAVELING")
    return svg(W, 300, "\n".join(b), "Traveling: the Detachment's elements in column, about 20 metres apart")


def traveling_overwatch():
    W = 820
    b = _march(W, [(130, "~20 m", False)] * 3 + [(260, "50 - 100 m", True)],
               "Contact possible - the basic technique",
               ["The lead Group is far enough out to find the enemy before he sees the main body,",
                "and close enough that the rest can still support it with fire."], "TRAVELING OVERWATCH")
    return svg(W, 300, "\n".join(b), "Traveling overwatch: the lead Group 50 to 100 metres ahead, the rest about 20 metres apart behind it")


def bounding_overwatch():
    W, H = 860, 600
    b = [title(W, "BOUNDING OVERWATCH", "Contact likely - one Group moves while another covers it from a set position")]
    # terrain: contour rings and a tree line
    for cx, cy, rx, ry in ((430, 440, 120, 60), (430, 440, 75, 34), (250, 180, 110, 60), (250, 180, 60, 30),
                           (690, 190, 110, 55), (690, 190, 60, 28)):
        b.append(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='none' stroke='{GRID}' stroke-width='2'/>")
    for i in range(8):
        tx, ty = 60 + (i % 2) * 26, 110 + i * 40
        b.append(f"<circle cx='{tx}' cy='{ty}' r='16' fill='#a5c88a' opacity='.8'/>")
    b.append(text(72, 455, "trees", 12, MUTE))
    # overwatch fields of fire
    b.append(wedge(430, 430, -90, 330, 42, BLUE, .10))
    b.append(unit_box(430, 430, label=""))
    b.append(lines(430, 470, ["OVERWATCH Group", "set, covering both routes"], 13, BLUE, weight="bold"))
    b.append(unit_box(500, 420, 28, 20))
    b.append(text(536, 425, "DL", 12, INK, weight="bold"))
    # bounding group, left
    b.append(unit_box(170, 420, label="", ))
    b.append(arrow("M175,400 C190,320 205,260 240,214", GREEN, 2.5))
    b.append(unit_box(250, 190))
    b.append(lines(170, 456, ["BOUNDING Group", "uses the trees"], 13, GREEN, weight="bold"))
    b.append(text(250, 150, "next overwatch position", 13, GREEN, weight="bold"))
    # waiting group, right
    b.append(unit_box(700, 440))
    b.append(lines(700, 476, ["Third Group", "waits for orders"], 13, INK, weight="bold"))
    b.append(arrow("M690,420 C670,340 680,260 690,222", INK, 1.8, "6 5"))
    b.append(text(700, 140, "its bound, when ordered", 13, MUTE))
    b.append(unit_box(690, 190, ))
    b.append(lines(W / 2, 545, ["Every bound ends inside the overwatch's range. The Detachment leader stays with the overwatch.",
                                "When the bounding Group is set, the roles swap and the next bound begins."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Bounding overwatch: one Group bounds to the next position while another covers it from a set position and the third waits")


# ---------------------------------------------------------------- formation tables

def team_table():
    cols = [("Formation", 120), ("Used most", 170), ("Control", 90), ("Flexibility", 140), ("Fire", 210), ("Security", 120)]
    rows = [["Team wedge", "The basic team\nformation", "Easy", "Good", "Can fire at once in\nany direction", "All-round"],
            ["Team file", "Close terrain, poor\nvisibility, thick\nvegetation", "Easiest", "Less than the\nwedge", "Fires to the flanks;\nmasks most fire to\nfront and rear", "Weak front\nand rear"],
            ["Team line", "Assaulting", "Easy", "None", "To the front only", "Least"]]
    t, h = table(20, 52, cols, rows, 13)
    W = 890
    return svg(W, 52 + h + 20, title(W, "TEAM FORMATIONS COMPARED") + t,
               "Team formations compared: when each is used, and its control, flexibility, fire and security")


def detachment_table():
    cols = [("Formation", 130), ("Used most", 160), ("Control", 100), ("Flexibility", 160), ("Fire", 200), ("Security", 120)]
    rows = [["Group column", "Main formation\nfor moving", "Good", "Good for maneuver;\nspread wide and\ndeep", "Heavy fire to the\nflanks, light to\nthe front", "All-round"],
            ["Group file", "Close terrain, thick\nvegetation, poor\nvisibility", "Easiest", "Hardest to\nmaneuver from", "Fires to the flanks;\nmasks front and rear", "Least"],
            ["Group wedge", "Open ground with\nlittle cover", "Easy", "Good", "Can fire at once in\nany direction", "All-round"],
            ["Group line", "Most firepower to\nthe front (assault)", "Less than\nthe column", "Little - every team\nis committed", "Most fire to the\nfront", "Good to front,\nlittle to flanks\nand rear"],
            ["Staggered\ncolumn", "Roads, built-up\nareas", "Good", "Good for maneuver;\nspread wide and\ndeep", "Heavy fire to the\nflanks, light to\nthe front", "All-round"]]
    t, h = table(20, 52, cols, rows, 13)
    W = 910
    return svg(W, 52 + h + 20, title(W, "DETACHMENT FORMATIONS COMPARED") + t,
               "Detachment formations compared: when each is used, and its control, flexibility, fire and security")


# ---------------------------------------------------------------- team formations

def team_file():
    W, H = 360, 330
    b = [title(W, "TEAM FILE"), move_dir(50, 60, 300)]
    b.append(team(file_pts(210, 80, 48), RED, {0: "TL"}))
    b.append(lines(210, 290, ["One behind the other.", "Close terrain, buildings, dark."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Team file: the team one behind the other along the direction of movement")


def team_wedge():
    W, H = 400, 330
    b = [title(W, "TEAM WEDGE"), move_dir(50, 60, 300)]
    pts = wedge_pts(210, 90, 48)
    b.append(team(pts, RED, {0: "TL"}))
    b.append(line(pts[0][0] + 10, pts[0][1] - 4, pts[2][0] + 10, pts[2][1] - 4, MUTE, 1, "3 3"))
    b.append(text(278, 100, "~10 m", 12, MUTE, "start"))
    b.append(text(pts[3][0], pts[3][1] + 32, "strong side", 12, INK, weight="bold"))
    b.append(lines(220, 270, ["Leader at the point, the others staggered", "back. The extra man marks the strong side."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Team wedge: the team leader at the point, the others staggered back, the extra man on the strong side")


def team_line():
    W, H = 400, 260
    b = [title(W, "TEAM LINE"), move_dir(50, 60, 230)]
    b.append(team(line_pts(230, 110, 56), RED))
    b.append(lines(230, 170, ["Abreast, facing the way you move.", "All fire to the front: the assault."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Team line: the team abreast, facing the direction of movement")


# ---------------------------------------------------------------- group (detachment) formations

TEAMS = (RED, GREEN, BLUE)


def group_column():
    W, H = 400, 640
    b = [title(W, "GROUP COLUMN"), move_dir(50, 160, 560)]
    for i, c in enumerate(TEAMS):
        b.append(team(wedge_pts(220, 70 + i * 180, 42), c))
    b.append(lines(220, 600, ["Three teams in wedge, one behind the other."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Group column: three teams in wedge, one behind the other")


def group_file():
    W, H = 320, 720
    b = [title(W, "GROUP FILE"), move_dir(50, 90, 640)]
    for i, c in enumerate(TEAMS):
        b.append(team(file_pts(190, 70 + i * 200, 42), c))
    b.append(lines(190, 680, ["Every team in file."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Group file: every team in file, one behind the other")


def group_wedge():
    W, H = 520, 470
    b = [title(W, "GROUP WEDGE"), move_dir(W / 2, 220, 430)]
    b.append(team(wedge_pts(250, 70, 36), RED))
    b.append(team(wedge_pts(110, 250, 36), GREEN))
    b.append(team(wedge_pts(390, 250, 36), BLUE))
    b.append(lines(W / 2, 460, ["Lead team at the point, the other two back to either side."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Group wedge: the lead team at the point, the other two back to either side")


def group_line():
    W, H = 860, 300
    b = [title(W, "GROUP LINE", "The three teams abreast. The centre team is the base."), move_dir(50, 80, 280)]
    for i, c in enumerate(TEAMS):
        b.append(team(wedge_pts(220 + i * 250, 100, 40), c))
    b.append(text(470, 215, "base team", 13, GREEN, weight="bold"))
    b.append(lines(470, 262, ["The assault formation: once ready, each team shakes out into a team line."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Group line: the three teams abreast, the centre team the base")


def group_staggered():
    W, H = 400, 720
    b = [title(W, "GROUP STAGGERED COLUMN"), move_dir(50, 90, 640)]
    xs = (170, 300, 170)
    for i, c in enumerate(TEAMS):
        b.append(team(file_pts(xs[i], 70 + i * 200, 42), c))
    b.append(lines(220, 680, ["Teams in file, zig-zag to either side", "of the road."], 13, MUTE))
    return svg(W, H, "\n".join(b), "Group staggered column: the teams in file, offset to either side")


# ---------------------------------------------------------------- danger area

def danger_area():
    W, H = 900, 620
    PW = 300
    b = [title(W, "CROSSING A DANGER AREA")]
    steps = [("1. Halt, post near-side security", ["Flank security out on the near side.", "The far-side team crosses and clears."]),
             ("2. Far side clear - cross", ["Far-side team watches the flanks.", "The unit crosses fast and quiet."]),
             ("3. Collect security, move on", ["Near-side security crosses last.", "Head count, then on the azimuth."])]
    band_y, band_h = 300, 70
    for p, (head, sub) in enumerate(steps):
        ox = p * PW
        cx = ox + PW / 2
        if p:
            b.append(line(ox, 50, ox, H - 10, GRID, 2))
        b.append(text(cx, 70, head, 14, INK, weight="bold"))
        b.append(lines(cx, 92, sub, 13, MUTE))
        b.append(f"<rect x='{ox + 6}' y='{band_y}' width='{PW - 12}' height='{band_h}' fill='{GROUND}' opacity='.6'/>")
        b.append(line(ox + 6, band_y, ox + PW - 6, band_y, INK, 1.5, "7 5"))
        b.append(line(ox + 6, band_y + band_h, ox + PW - 6, band_y + band_h, INK, 1.5, "7 5"))
        b.append(text(ox + 60, band_y + band_h / 2 + 5, "DANGER AREA", 12, OLIVE, weight="bold"))
    # panel 1: halt, near-side security out, far-side team crosses
    for i in range(5):
        b.append(man(150, 470 + i * 30, GREEN, -90))
    b.append(man(50, 400, BLUE, 180)); b.append(man(76, 420, BLUE, 180))
    b.append(man(250, 400, BLUE, 0)); b.append(man(224, 420, BLUE, 0))
    b.append(text(62, 452, "near-side", 12, BLUE, weight="bold"))
    b.append(text(238, 452, "near-side", 12, BLUE, weight="bold"))
    b.append(arrow("M180,440 L180,272", RED, 2.2))
    b.append(man(160, 262, RED, -90)); b.append(man(200, 248, RED, -90))
    b.append(text(180, 218, "far-side team", 12, RED, weight="bold"))
    # panel 2: far side held, the unit crosses
    ox = PW
    b.append(man(ox + 60, 250, RED, 180)); b.append(man(ox + 90, 270, RED, 180))
    b.append(man(ox + 240, 250, RED, 0)); b.append(man(ox + 210, 270, RED, 0))
    b.append(text(ox + 150, 230, "far side clear", 12, RED, weight="bold"))
    b.append(man(ox + 50, 400, BLUE, 180)); b.append(man(ox + 76, 420, BLUE, 180))
    b.append(man(ox + 250, 400, BLUE, 0)); b.append(man(ox + 224, 420, BLUE, 0))
    for i in range(4):
        b.append(man(ox + 150, 480 + i * 30, GREEN, -90))
    b.append(arrow(f"M{ox + 150},462 L{ox + 150},282", GREEN, 2.5))
    b.append(text(ox + 150, 600, "shortest way across", 12, GREEN, weight="bold"))
    # panel 3: security collected, the unit moves on
    ox = 2 * PW
    b.append(man(ox + 135, 150, RED, -90)); b.append(man(ox + 165, 150, RED, -90))
    for i in range(4):
        b.append(man(ox + 150, 185 + i * 28, GREEN, -90))
    b.append(arrow(f"M{ox + 250},260 L{ox + 250},160", INK, 2.5))
    b.append(text(ox + 250, 280, "on", 12, INK, weight="bold"))
    b.append(arrow(f"M{ox + 70},398 C{ox + 70},340 {ox + 110},320 {ox + 128},290", BLUE, 2))
    b.append(arrow(f"M{ox + 230},398 C{ox + 230},340 {ox + 190},320 {ox + 172},290", BLUE, 2))
    b.append(man(ox + 70, 415, BLUE, -90)); b.append(man(ox + 230, 415, BLUE, -90))
    b.append(lines(ox + 150, 470, ["near-side security", "falls in behind"], 12, BLUE, weight="bold"))
    return svg(W, H, "\n".join(x for x in b if x), "Crossing a danger area: near-side security, the far-side team clears, the unit crosses, security collected")


# ---------------------------------------------------------------- build

def build():
    for name, fn in (("enfilade-defilade", enfilade_defilade),
                     ("bounding-leapfrog", bounding_leapfrog), ("bounding-first-bounds", bounding_first),
                     ("bounding-cross-behind", bounding_behind), ("bounding-crossing", bounding_crossing),
                     ("technique-traveling", traveling), ("technique-traveling-overwatch", traveling_overwatch),
                     ("technique-bounding-overwatch", bounding_overwatch),
                     ("team-formations-table", team_table), ("team-file", team_file), ("team-wedge", team_wedge),
                     ("team-line", team_line), ("detachment-formations-table", detachment_table),
                     ("group-column", group_column), ("group-file", group_file), ("group-wedge", group_wedge),
                     ("group-line", group_line), ("group-staggered-column", group_staggered),
                     ("danger-area-crossing", danger_area)):
        write(SUB, name, fn())
