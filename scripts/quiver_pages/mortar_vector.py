"""Pictures for the Mortar and Vector 21 pages: MOA / mil explainers, ballistics diagrams, range-table key, Vector 21 button strips."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiver_draw import *  # noqa: E401,F401,F403,E402

MONO = "font-family='Consolas, \"Courier New\", monospace'"
SKY = "#7fb3d5"


# --------------------------------------------------------------- helpers

def poly(pts, fill, stroke="none", width=1):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f"<polygon points='{p}' fill='{fill}' stroke='{stroke}' stroke-width='{width}'/>"


def path(d, stroke=INK, width=2, fill="none", dash=""):
    da = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<path d='{d}' fill='{fill}' stroke='{stroke}' stroke-width='{width}'{da}/>"


def arc(cx, cy, r, a1, a2, colour=INK, width=1.8, head=False):
    """Arc from angle a1 to a2 (degrees, SVG sense: 0 = right, 90 = down)."""
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    p2 = (cx + r * math.cos(math.radians(a2)), cy + r * math.sin(math.radians(a2)))
    sweep = 1 if a2 > a1 else 0
    large = 1 if abs(a2 - a1) > 180 else 0
    d = f"M{p1[0]:.1f},{p1[1]:.1f} A{r},{r} 0 {large} {sweep} {p2[0]:.1f},{p2[1]:.1f}"
    if head:
        return arrow(d, colour, width)
    return path(d, colour, width)


def dbl(x, y1, y2, colour=MUTE, width=1.8, dash="6 4"):
    """A dashed measuring line with a head at both ends."""
    head = HEAD.get(colour, "ah")
    return (f"<line x1='{x}' y1='{y1}' x2='{x}' y2='{y2}' stroke='{colour}' stroke-width='{width}' "
            f"stroke-dasharray='{dash}' marker-start='url(#{head})' marker-end='url(#{head})'/>")


def burst(x, y, r=22, fill="#f2a33a"):
    pts = []
    for i in range(16):
        rr = r if i % 2 == 0 else r * .45
        a = math.radians(i * 22.5 - 90)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return poly(pts, fill, INK, 1.5)


def mortar(x, y, angle=60, s=1.0):
    """A mortar on its baseplate, barrel raised `angle` degrees, muzzle up-right. (x, y) = baseplate."""
    a = math.radians(angle)
    L = 44 * s
    mx, my = x + L * math.cos(a), y - 6 * s - L * math.sin(a)
    out = [box(x - 14 * s, y - 6 * s, 28 * s, 6 * s, OLIVE, INK, 1.2, 1),
           line(x, y - 6 * s, mx, my, INK, 8 * s),
           line(x + 20 * s, y, x + 20 * s * .55 + L * .55 * math.cos(a), y - L * .55 * math.sin(a) - 4 * s, INK, 2.5 * s),
           line(x + 26 * s, y, x + 20 * s * .55 + L * .55 * math.cos(a), y - L * .55 * math.sin(a) - 4 * s, INK, 2.5 * s)]
    return "".join(out), (mx, my)


# --------------------------------------------------------------- MOA / mil

def angle_unit(kind):
    moa = kind == "moa"
    W = 820
    b = []
    if moa:
        b.append(title(W, "MINUTE OF ANGLE (MOA)",
                       "One MOA opens up by about 1 inch for every 100 yards of range"))
        cols = [("MOA", 90), ("Range", 170), ("Inches", 170), ("Centimetres", 170)]
        rows = [["1", f"{r} yards", f"{r // 100} inch" + ("" if r == 100 else "es"), f"{r // 100 * 2.5:g} cm"]
                for r in (100, 200, 300, 400)]
        unit, rng = "1 MOA", "yards"
        labs = [(f"{r} yd", f"= {r // 100} in", f"~ {r // 100 * 2.5:g} cm") for r in (100, 200, 300, 400)]
    else:
        b.append(title(W, "THE MIL",
                       "One mil opens up by 10 cm for every 100 metres of range"))
        cols = [("Mil", 90), ("Range", 170), ("Centimetres", 170), ("Inches", 170)]
        rows = [["1", f"{r} metres", f"{r // 10} cm", f"{r // 25} inches"] for r in (100, 200, 300, 400)]
        unit, rng = "1 mil", "metres"
        labs = [(f"{r} m", f"= {r // 10} cm", f"~ {r // 25} in") for r in (100, 200, 300, 400)]
    t, th = table(110, 70, cols, rows, 14)
    b.append(t)
    # the opening angle
    y0 = 70 + th + 40
    ox, oy, x1 = 70, y0 + 230, 760
    slope = 200 / (x1 - ox)
    b.append(arrow(f"M{ox},{oy} L{x1 + 20},{oy}", INK, 2.5))
    b.append(arrow(f"M{ox},{oy} L{x1 + 20},{oy - slope * (x1 + 20 - ox):.0f}", INK, 2.5))
    b.append(arc(ox, oy, 190, -math.degrees(math.atan(slope)) - .5, -1, BLUE, 2))
    b.append(text(ox + 102, oy - 7, unit, 14, BLUE, "start", "bold"))
    for i, xx in enumerate((270, 430, 590, 750)):
        h = slope * (xx - ox)
        b.append(dbl(xx, oy - 4, oy - h + 4, RED, 2))
        b.append(lines(xx, oy + 26, labs[i], 14, INK, weight="bold"))
    b.append(text(W / 2, oy + 100, "The angle is drawn far wider than it really is so the gaps can be seen.", 13, MUTE))
    # summary
    sy = oy + 125
    if moa:
        facts = [["360 degrees in a circle", "60 MOA in a degree"],
                 ["21,600 MOA in a circle", "1 MOA at 100 yards = about 1 inch"],
                 ["", "Smaller than 1 MOA: fractions (1/2 MOA), not seconds"]]
    else:
        facts = [["360 degrees in a circle", "17.78 mils in a degree"],
                 ["6400 mils in a circle", "1 mil at 100 metres = 10 cm"]]
    t, fh = table(70, sy, [("The circle", 280), ("Handy figures", 400)], facts, 14)
    b.append(t)
    H = sy + fh + 30
    if not moa:
        # compass rose: mils inside, degrees outside
        cx, cy = W / 2, H + 255
        b.append(text(W / 2, H + 10, "Around the compass: mils inside, degrees outside", 14, INK, weight="bold"))
        b.append(f"<circle cx='{cx}' cy='{cy}' r='185' fill='none' stroke='{MUTE}' stroke-width='1.5'/>")
        b.append(f"<circle cx='{cx}' cy='{cy}' r='120' fill='{LIGHT}' stroke='{INK}' stroke-width='2'/>")
        b.append(f"<circle cx='{cx}' cy='{cy}' r='60' fill='none' stroke='{GRID}' stroke-width='1.5'/>")
        for k in range(16):
            mils = k * 400
            a = math.radians(k * 22.5 - 90)
            major = k % 2 == 0
            b.append(line(cx, cy, cx + 120 * math.cos(a), cy + 120 * math.sin(a),
                          INK if major else MUTE, 3 if k % 4 == 0 else (2 if major else 1)))
            lx, ly = cx + 145 * math.cos(a), cy + 145 * math.sin(a) + 5
            b.append(text(f"{lx:.0f}", f"{ly:.0f}", str(mils or 6400), 13, BLUE, weight="bold" if k % 4 == 0 else "normal"))
            if major:
                deg = k * 22.5
                dx, dy = cx + 205 * math.cos(a), cy + 205 * math.sin(a) + 5
                b.append(text(f"{dx:.0f}", f"{dy:.0f}", f"{deg:g}°" if deg else "360°", 13, INK, weight="bold"))
        H = cy + 235
    return svg(W, H, "\n".join(b),
               "Minute of angle: 1 MOA is about 1 inch per 100 yards" if moa
               else "The mil: 1 mil is 10 cm per 100 metres, 6400 mils in a circle")


# --------------------------------------------------------------- fires diagrams

BEAUFORT = [
    (0, "Calm", "< 2 km/h", "< 0.5 m/s", "#ffffff"),
    (1, "Light air", "2-5 km/h", "0.5-1.5 m/s", "#b3ecf5"),
    (2, "Light breeze", "6-11 km/h", "1.6-3.3 m/s", "#9ef0dc"),
    (3, "Gentle breeze", "12-19 km/h", "3.4-5.5 m/s", "#98f2b0"),
    (4, "Moderate breeze", "20-28 km/h", "5.5-7.9 m/s", "#72ed72"),
    (5, "Fresh breeze", "29-38 km/h", "8-10.7 m/s", "#7ae81e"),
    (6, "Strong breeze", "39-49 km/h", "10.8-13.8 m/s", "#aaeb16"),
    (7, "High wind", "50-61 km/h", "13.9-17.1 m/s", "#dcec14"),
    (8, "Gale", "62-74 km/h", "17.2-20.7 m/s", "#eec41c"),
    (9, "Strong / severe gale", "75-88 km/h", "20.8-24.4 m/s", "#ee9420"),
    (10, "Storm", "89-102 km/h", "24.5-28.4 m/s", "#ec6620"),
    (11, "Violent storm", "103-117 km/h", "28.5-32.6 m/s", "#e8321c"),
    (12, "Hurricane force", ">= 118 km/h", ">= 32.7 m/s", "#d0143a"),
]


def beaufort():
    W = 640
    b = [title(W, "BEAUFORT SCALE", "The wind arrow's colour climbs the scale as the wind gets stronger")]
    x, y, rh = 40, 70, 30
    cols = [("Force", 90), ("Description", 230), ("km/h", 140), ("m/s", 100)]
    cx = x
    for h, w in cols:
        b.append(box(cx, y, w, 34, OLIVE, INK, 1))
        b.append(text(cx + w / 2, y + 22, h, 14, "#fff", weight="bold"))
        cx += w
    y += 34
    for i, (n, d, kmh, ms, c) in enumerate(BEAUFORT):
        ry = y + i * rh
        b.append(box(x, ry, 90, rh, c, INK, 1))
        b.append(text(x + 45, ry + 20, str(n), 14, "#fff" if n >= 9 else INK, weight="bold"))
        b.append(box(x + 90, ry, 470, rh, LIGHT if i % 2 else "#fff", INK, 1))
        b.append(text(x + 100, ry + 20, d, 14, INK, "start"))
        b.append(text(x + 330, ry + 20, kmh.replace(">=", "≥"), 14, INK, "start"))
        b.append(text(x + 470, ry + 20, ms.replace(">=", "≥"), 14, INK, "start"))
    H = y + len(BEAUFORT) * rh + 24
    return svg(W, H, "\n".join(b).replace("&amp;#8805;", "&#8805;"), "Beaufort wind scale 0 to 12 with colour bands and wind speeds")


def flight_curve(x0, y0, x1, top, n=80, skew=1.6, y1=None):
    """An air-drag shaped path: rises gently, peaks past the middle, falls steeply. Returns points."""
    pts = []
    for i in range(n + 1):
        u = i / n
        # bend time so the peak sits about 60 % of the way along
        x = x0 + (x1 - x0) * (1 - (1 - u) ** skew) / (1 - 0 ** skew)
        y = y0 + ((y0 if y1 is None else y1) - y0) * u - top * 4 * u * (1 - u)
        pts.append((x, y))
    return pts


def pts_d(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def trajectory_parts():
    W, H = 820, 420
    b = [title(W, "PARTS OF THE TRAJECTORY", "With air drag the summit sits past the middle and the round comes down steeper than it went up")]
    gy = 360
    b.append(line(30, gy, 790, gy, INK, 2.5))
    m, (mx, my) = mortar(90, gy, 58)
    pts = flight_curve(mx, my, 660, 230, skew=1.8, y1=gy)
    peak = min(pts, key=lambda p: p[1])
    b.append(path(pts_d(pts), RED, 3))
    b.append(m)
    b.append(burst(660, gy - 14, 26))
    b.append(line(peak[0], peak[1] + 4, peak[0], gy, MUTE, 1.5, "8 6"))
    b.append(dbl(peak[0], peak[1] + 4, gy - 2, BLUE, 2, ""))
    b.append(lines(peak[0] - 12, (peak[1] + gy) / 2 - 6, ["MAXIMUM ORDINATE", "height of the summit", "above the gun"], 13, BLUE, "end", "bold"))
    b.append(text(peak[0], peak[1] - 12, "SUMMIT", 14, INK, weight="bold"))
    b.append(arrow("M200,190 L250,160", INK, 3))
    b.append(lines(150, 214, ["ASCENDING", "BRANCH"], 14, INK, weight="bold"))
    b.append(arrow("M690,170 L708,212", INK, 3))
    b.append(lines(740, 140, ["DESCENDING", "BRANCH"], 14, INK, weight="bold"))
    b.append(text(90, gy + 28, "ORIGIN", 14, INK, weight="bold"))
    b.append(text(400, gy + 28, "ground level", 13, MUTE))
    b.append(text(660, gy + 28, "POINT OF IMPACT", 14, INK, weight="bold"))
    return svg(W, H, "\n".join(b), "Parts of a trajectory: origin, ascending branch, summit, maximum ordinate, descending branch, point of impact")


def trajectory_angles():
    W, H = 820, 420
    b = [title(W, "ANGLES OF THE TRAJECTORY", "Measured from the gun to a target that sits higher than the gun")]
    gx, gy = 110, 360
    tx, ty = 650, 300
    b.append(arrow(f"M{gx - 60},{gy} L790,{gy}", GREEN, 2.5))
    b.append(arrow(f"M{gx},{gy} L{gx - 60},{gy}", GREEN, 2.5))
    b.append(text(720, gy + 24, "Horizontal plane", 13, GREEN, weight="bold"))
    # line of sight
    b.append(line(gx, gy, tx, ty, INK, 2))
    sight = math.degrees(math.atan2(gy - ty, tx - gx))
    b.append(text(420, 350, "Line of sight", 13, INK, weight="bold"))
    # trajectory: a parabola-ish oval through gun and target
    pts = []
    n = 90
    for i in range(n + 1):
        u = i / n
        x = gx + (tx - gx) * (1 - (1 - u) ** 1.5)
        y = gy + (ty - gy) * u - 190 * 4 * u * (1 - u)
        pts.append((x, y))
    b.append(path(pts_d(pts), RED, 3))
    peak = min(pts, key=lambda p: p[1])
    b.append(arrow(f"M{peak[0]},{peak[1] - 40} L{peak[0]},{peak[1] - 6}", INK, 2))
    b.append(text(peak[0], peak[1] - 46, "Vertex (summit)", 13, INK, weight="bold"))
    b.append(text(250, 150, "Trajectory", 14, RED, weight="bold"))
    # line of fire: tangent at the muzzle
    dx, dy = pts[2][0] - pts[0][0], pts[2][1] - pts[0][1]
    fire = math.degrees(math.atan2(-dy, dx))
    L = 210
    fx, fy = gx + L * math.cos(math.radians(fire)), gy - L * math.sin(math.radians(fire))
    b.append(line(gx, gy, fx, fy, BLUE, 2, "8 5"))
    b.append(text(fx - 8, fy - 8, "Line of fire (bore)", 13, BLUE, "end", "bold"))
    # angles at the gun
    b.append(arc(gx, gy, 140, -sight, -0.5, GREEN, 2))
    b.append(text(gx + 150, gy - 5, "Angle of sight", 13, GREEN, "start", "bold"))
    b.append(arc(gx, gy, 80, -fire, -sight, BLUE, 2))
    b.append(lines(gx + 92, gy - 52, ["Angle of", "projection"], 13, BLUE, "start", "bold"))
    # angle of descent at the target
    near = min(pts, key=lambda p: abs(math.hypot(p[0] - tx, p[1] - ty) - 55))
    ex, ey = near[0] - tx, near[1] - ty
    desc = math.degrees(math.atan2(ey, ex)) % 360
    b.append(arc(tx, ty, 55, 180 - sight, desc, RED, 2))
    mid = math.radians((180 - sight + desc) / 2)
    b.append(lines(tx - 90, ty - 80, ["Angle of", "descent"], 13, RED, "end", "bold"))
    b.append(line(tx - 86, ty - 78, tx + 55 * math.cos(mid), ty + 55 * math.sin(mid), MUTE, 1))
    # gun and target
    b.append(f"<circle cx='{gx}' cy='{gy}' r='6' fill='{INK}'/>")
    b.append(text(gx, gy + 26, "Gun", 14, INK, weight="bold"))
    b.append(box(tx - 4, ty, 70, gy - ty, GROUND, INK, 1))
    b.append(burst(tx, ty - 6, 14))
    b.append(text(tx + 40, ty - 20, "Target", 14, INK, "start", "bold"))
    return svg(W, H, "\n".join(b), "Angle of sight, angle of projection, line of fire, vertex and angle of descent of a trajectory")


def simulate(v, ang=45, k=0.004, g=9.81, dt=0.01):
    a = math.radians(ang)
    x, y, vx, vy = 0.0, 0.0, v * math.cos(a), v * math.sin(a)
    out = [(x, y)]
    while y >= 0:
        s = math.hypot(vx, vy)
        vx += -k * s * vx * dt
        vy += (-g - k * s * vy) * dt
        x += vx * dt
        y += vy * dt
        out.append((x, max(y, 0)))
    return out


def launch_speeds():
    W, H = 820, 470
    b = [title(W, "MORE SPEED, MORE RANGE  -  BUT DRAG BENDS THE FALL",
               "Five shells fired at 45 degrees with the same drag; only the muzzle speed changes")]
    px, py, pw, ph = 80, 80, 560, 320
    speeds = [(60, BLUE), (90, "#c2185b"), (120, "#9e9d24"), (150, GREEN), (180, "#00838f")]
    runs = [simulate(v) for v, _ in speeds]
    xmax = 500
    ymax = 250
    sx, sy = pw / xmax, ph / ymax
    # grid
    for gxv in range(0, xmax + 1, 100):
        X = px + gxv * sx
        b.append(line(X, py, X, py + ph, GRID, 1))
        b.append(text(X, py + ph + 20, str(gxv), 12, MUTE))
    for gyv in range(0, ymax + 1, 50):
        Y = py + ph - gyv * sy
        b.append(line(px, Y, px + pw, Y, GRID, 1))
        b.append(text(px - 8, Y + 4, str(gyv), 12, MUTE, "end"))
    b.append(box(px, py, pw, ph, "none", INK, 1.5))
    b.append(text(px + pw / 2, py + ph + 42, "Range (m)", 13, INK, weight="bold"))
    b.append(f"<text x='{px - 46}' y='{py + ph / 2}' text-anchor='middle' {FONT} font-size='13' font-weight='bold' fill='{INK}' "
             f"transform='rotate(-90 {px - 46} {py + ph / 2})'>Height (m)</text>")
    for (v, c), run in zip(speeds, runs):
        d = "M" + " L".join(f"{px + x * sx:.1f},{py + ph - y * sy:.1f}" for x, y in run[::4] + [run[-1]])
        b.append(path(d, c, 3))
    # legend
    lx, ly = px + pw + 30, py + 10
    b.append(text(lx, ly + 4, "Muzzle speed", 13, INK, "start", "bold"))
    for i, ((v, c), run) in enumerate(zip(speeds, runs)):
        yy = ly + 30 + i * 28
        b.append(line(lx, yy, lx + 30, yy, c, 4))
        b.append(text(lx + 40, yy + 5, f"{v} m/s  -  {run[-1][0]:.0f} m", 13, INK, "start"))
    b.append(lines(lx, ly + 200, ["Faster shells go further,", "but each extra 30 m/s buys", "less range than the last.", "",
                                  "Every curve peaks past", "its middle and falls", "steeper than it rose."], 13, MUTE, "start"))
    return svg(W, H, "\n".join(b), "Trajectories at 45 degrees for five muzzle speeds, with air drag")


def coriolis():
    W, H = 820, 520
    b = [title(W, "CORIOLIS: THE EARTH TURNS UNDER THE SHELL",
               "Anything moving north or south is pushed off its line by the spin")]
    cx, cy, R = 300, 300, 180
    b.append(arrow(f"M{cx - 130},{cy - 196} Q{cx},{cy - 232} {cx + 130},{cy - 196}", INK, 2.2))
    b.append(text(cx + 150, cy - 200, "Earth spins west to east", 13, INK, "start"))
    b.append(f"<circle cx='{cx}' cy='{cy}' r='{R}' fill='#e8f1f8' stroke='{INK}' stroke-width='2.5'/>")
    b.append(f"<path d='M{cx - R},{cy} A{R},{38} 0 0 0 {cx + R},{cy}' fill='none' stroke='{INK}' stroke-width='2'/>")
    b.append(f"<path d='M{cx - R},{cy} A{R},{38} 0 0 1 {cx + R},{cy}' fill='none' stroke='{MUTE}' stroke-width='1.2' stroke-dasharray='5 4'/>")
    b.append(text(cx, cy + 62, "Equator", 14, INK, weight="bold"))
    b.append(text(cx, cy - 140, "NORTHERN HEMISPHERE", 13, MUTE, weight="bold"))
    b.append(text(cx, cy + 162, "SOUTHERN HEMISPHERE", 13, MUTE, weight="bold"))

    def pair(x, y, dy, side):
        # where it is aimed (solid), and where it goes (dashed, curving off)
        s = arrow(f"M{x},{y} L{x},{y + dy}", INK, 2.5)
        s += arrow(f"M{x},{y} Q{x},{y + dy * .8} {x + 40 * side},{y + dy}", RED, 2.5, "6 4")
        return s
    # north of the equator a shell drifts to its own right, south of it to its own left
    b.append(pair(cx - 100, cy - 120, 65, -1))   # going south, its right is west (page left)
    b.append(pair(cx + 100, cy - 30, -65, 1))    # going north, its right is east (page right)
    b.append(pair(cx - 100, cy + 55, 65, 1))     # going south, its left is east
    b.append(pair(cx + 100, cy + 140, -65, -1))  # going north, its left is west
    lx, ly = 540, 150
    b.append(box(lx, ly, 260, 210, "#fff", INK, 1.5, 4))
    b.append(text(lx + 16, ly + 28, "Key", 14, INK, "start", "bold"))
    b.append(arrow(f"M{lx + 16},{ly + 58} L{lx + 60},{ly + 58}", INK, 2.5))
    b.append(text(lx + 72, ly + 63, "where the shell is aimed", 13, INK, "start"))
    b.append(arrow(f"M{lx + 16},{ly + 92} L{lx + 60},{ly + 92}", RED, 2.5, "6 4"))
    b.append(text(lx + 72, ly + 97, "where it actually goes", 13, INK, "start"))
    b.append(lines(lx + 16, ly + 132, ["North of the equator:", "drifts to the RIGHT", "South of the equator:", "drifts to the LEFT"],
                   13, INK, "start", "bold"))
    return svg(W, H, "\n".join(b), "Coriolis effect: shells drift right in the northern hemisphere and left in the southern")


def eotvos():
    W, H = 820, 480
    b = [title(W, "EÖTVÖS AND CORIOLIS: ONE PUSH, TWO PARTS",
               "A shell fired east is pushed straight out from the Earth's axis; split that push along the ground and straight up")]
    cx, cy, R = 120, 520, 400
    lat = math.radians(40)
    # Earth: a slice seen side on, axis straight up
    b.append(f"<path d='M{cx},{cy} L{cx},{cy - R} A{R},{R} 0 0 1 {cx + R},{cy} z' fill='#e8f1f8' stroke='{SKY}' stroke-width='6'/>")
    b.append(arrow(f"M{cx},{cy - R + 10} L{cx},{cy - R - 50}", INK, 2.5))
    b.append(line(cx, cy, cx, cy - R, INK, 1.5, "6 5"))
    b.append(text(cx + 10, cy - R - 34, "Earth's axis", 13, INK, "start", "bold"))
    b.append(text(cx + 60, cy - 30, "Earth", 14, BLUE, "start", "bold"))
    # the gun's spot at 40 degrees north
    up = (math.cos(lat), -math.sin(lat))          # local vertical, out from the centre
    along = (math.sin(lat), math.cos(lat))        # local horizontal, along the ground towards the equator
    px, py = cx + R * up[0], cy + R * up[1]
    b.append(line(px - 120 * along[0], py - 120 * along[1], px + 150 * along[0], py + 150 * along[1], MUTE, 1.2, "4 4"))
    b.append(line(px, py, px + 200 * up[0], py + 200 * up[1], MUTE, 1.2, "4 4"))
    b.append(text(px + 200 * up[0] + 6, py + 200 * up[1] + 4, "straight up", 12, MUTE, "start"))
    b.append(text(px - 120 * along[0] - 6, py - 120 * along[1] + 4, "along the ground", 12, MUTE, "end"))
    # the full push (out from the axis) and its two parts
    L = 190
    ex, ey = px + L, py
    vu = L * up[0]
    va = L * along[0]
    ux, uy = px + vu * up[0], py + vu * up[1]
    ax, ay = px + va * along[0], py + va * along[1]
    b.append(line(ux, uy, ex, ey, MUTE, 1, "3 3"))
    b.append(line(ax, ay, ex, ey, MUTE, 1, "3 3"))
    b.append(arrow(f"M{px:.0f},{py:.0f} L{ex:.0f},{ey:.0f}", RED, 3.5))
    b.append(lines(ex + 12, ey + 5, ["Full push from the spin", "(straight out from the axis)"], 13, RED, "start", "bold"))
    b.append(arrow(f"M{px:.0f},{py:.0f} L{ux:.0f},{uy:.0f}", GREEN, 3.5))
    b.append(lines(ux + 24, uy - 4, ["EÖTVÖS EFFECT", "the upward part: the shell", "stays up longer and lands LONG"], 13, GREEN, "start", "bold"))
    b.append(arrow(f"M{px:.0f},{py:.0f} L{ax:.0f},{ay:.0f}", INK, 3.5))
    b.append(lines(ax + 12, ay + 10, ["CORIOLIS EFFECT", "the part along the ground:", "sideways drift"], 13, INK, "start", "bold"))
    b.append(f"<circle cx='{px:.0f}' cy='{py:.0f}' r='6' fill='{INK}'/>")
    b.append(lines(px - 18, py - 34, ["Gun, firing east", "(into the page)"], 13, INK, "end", "bold"))
    b.append(lines(W - 20, H - 40, ["Fire east: the push lifts the shell, it lands long.",
                                    "Fire west: the push is reversed, it lands short."], 13, MUTE, "end"))
    return svg(W, H, "\n".join(b), "Eötvös effect is the upward part of the spin's push on a shell, Coriolis drift the part along the ground")


def range_table_key():
    W = 820
    b = [title(W, "READING THE 82 mm RANGE TABLE", "What the numbered columns tell you")]
    rows = [
        ["1", "Charge", ""],
        ["2", "Range from the mortar to the target", ""],
        ["3", "Tube elevation for that range (mils)", ""],
        ["4", "Elevation change per 100 m of height\ndifference. Add if the target is lower,\nsubtract if it is higher",
         "Example: target at 1 m, mortar at 101 m\n(target 100 m lower) - add 112 to\nthe tube elevation"],
        ["5", "Change in flight time per 100 m", ""],
        ["6", "Time of flight (seconds)", ""],
        ["7", "Crosswind correction per 1 mph, in mils.\nWind to the right: add. To the left: subtract",
         "Example: 5 mph wind blowing left to\nright - add 3 mils"],
        ["8", "Head wind / tail wind correction per 1 mph", ""],
    ]
    t, th = table(30, 70, [("#", 50), ("Column", 380), ("Worked example", 330)], rows, 14)
    b.append(t)
    return svg(W, 70 + th + 24, "\n".join(b), "Key to the 82 mm mortar range table columns 1 to 8")


# --------------------------------------------------------------- Vector 21 strips

PW, PH, GAP, M0 = 176, 200, 12, 14
AIM = {"jeep": (0, -6), "tower": (0, -20), "light": (0, -22), "boat": (0, -14), "arch": (-22, -30),
       "house": (0, -12), "burst": (0, -8)}


def v_jeep(x, y, s=1.0):
    return (box(x - 22 * s, y - 10 * s, 44 * s, 12 * s, TAN, INK, 1.2, 2)
            + poly([(x - 8 * s, y - 10 * s), (x - 2 * s, y - 20 * s), (x + 1 * s, y - 20 * s), (x - 4 * s, y - 10 * s)], OLIVE)
            + f"<circle cx='{x - 13 * s:.1f}' cy='{y + 3 * s:.1f}' r='{6 * s:.1f}' fill='{INK}'/>"
            + f"<circle cx='{x + 13 * s:.1f}' cy='{y + 3 * s:.1f}' r='{6 * s:.1f}' fill='{INK}'/>")


def v_tower(x, y, s=1.0, hill=True):
    out = ""
    if hill:
        out += path(f"M{x - 34 * s:.1f},{y + 8 * s:.1f} Q{x:.1f},{y - 6 * s:.1f} {x + 34 * s:.1f},{y + 8 * s:.1f} z", MUTE, 1, GROUND)
    out += (box(x - 7 * s, y - 34 * s, 14 * s, 34 * s, "#b0aa98", INK, 1.2)
            + poly([(x - 9 * s, y - 34 * s), (x + 9 * s, y - 34 * s), (x + 9 * s, y - 40 * s), (x + 5 * s, y - 40 * s),
                    (x + 5 * s, y - 37 * s), (x + 2 * s, y - 37 * s), (x + 2 * s, y - 40 * s), (x - 2 * s, y - 40 * s),
                    (x - 2 * s, y - 37 * s), (x - 5 * s, y - 37 * s), (x - 5 * s, y - 40 * s), (x - 9 * s, y - 40 * s)],
                   "#b0aa98", INK, 1.2))
    return out


def v_light(x, y, s=1.0):
    return (poly([(x - 7 * s, y), (x + 7 * s, y), (x + 4 * s, y - 34 * s), (x - 4 * s, y - 34 * s)], "#fff", INK, 1.2)
            + poly([(x - 6 * s, y - 10 * s), (x + 6 * s, y - 10 * s), (x + 5.2 * s, y - 18 * s), (x - 5.2 * s, y - 18 * s)], RED)
            + box(x - 5 * s, y - 41 * s, 10 * s, 7 * s, "#ffe082", INK, 1)
            + poly([(x - 6 * s, y - 41 * s), (x + 6 * s, y - 41 * s), (x, y - 46 * s)], INK))


def v_boat(x, y, s=1.0):
    return (poly([(x - 16 * s, y - 6 * s), (x + 16 * s, y - 6 * s), (x + 11 * s, y), (x - 11 * s, y)], OLIVE, INK, 1)
            + poly([(x, y - 8 * s), (x, y - 32 * s), (x + 13 * s, y - 8 * s)], "#fff", INK, 1.2)
            + poly([(x - 2 * s, y - 8 * s), (x - 2 * s, y - 26 * s), (x - 12 * s, y - 8 * s)], "#fff", INK, 1.2))


def v_arch(x, y, s=1.0):
    w, h = 60 * s, 40 * s
    return path(f"M{x - w / 2:.1f},{y:.1f} L{x - w / 2:.1f},{y - h:.1f} L{x + w / 2:.1f},{y - h:.1f} L{x + w / 2:.1f},{y:.1f} "
                f"L{x + 16 * s:.1f},{y:.1f} L{x + 16 * s:.1f},{y - 18 * s:.1f} A{16 * s:.1f},{16 * s:.1f} 0 0 0 {x - 16 * s:.1f},{y - 18 * s:.1f} "
                f"L{x - 16 * s:.1f},{y:.1f} z", INK, 1.4, "#d9d2bf")


def v_house(x, y, s=1.0, tree=True):
    return (poly([(x - 16 * s, y), (x + 16 * s, y), (x + 16 * s, y - 18 * s), (x, y - 30 * s), (x - 16 * s, y - 18 * s)], "#d9d2bf", INK, 1.2)
            + ((line(x - 46 * s, y, x - 46 * s, y - 12 * s, INK, 2.5 * s)
                + f"<ellipse cx='{x - 46 * s:.1f}' cy='{y - 24 * s:.1f}' rx='{9 * s:.1f}' ry='{16 * s:.1f}' fill='{OLIVE}'/>") if tree else ""))


ICONS = {"jeep": v_jeep, "tower": v_tower, "light": v_light, "boat": v_boat, "arch": v_arch,
         "house": lambda x, y, s=1.0: v_house(x, y, s, tree=False),
         "burst": lambda x, y, s=1.0: burst(x, y - 8 * s, 12 * s)}


def binocular(ox, oy, tab=None, r=None):
    """Binocular seen from behind and above, set in a panel at (ox, oy). tab / r = what to do with that key:
    'hold' (press and hold), 'release', 'tap', 'taphold' (tap once, then press and hold)."""
    bx, by = ox + (PW - 110) / 2, oy + PH - 58
    out = [box(bx, by, 110, 38, "#c9c6b8", INK, 1.6, 12),
           box(bx + 14, by + 36, 30, 16, "#555", INK, 1.4, 4),
           box(bx + 66, by + 36, 30, 16, "#555", INK, 1.4, 4)]
    keys = {"tab": (bx + 29, tab), "r": (bx + 81, r)}
    for name, (kx, act) in keys.items():
        lit = act is not None
        out.append(box(kx - 16, by + 8, 32, 18, "#ffffff" if lit else "#e6e3d8", INK, 1.4 if lit else 1, 4))
        out.append(text(kx, by + 22, "Tab" if name == "tab" else "R", 12, INK if lit else MUTE, weight="bold"))
        if act:
            out.append(key_arrow(kx, by + 4, act))
    return "".join(out)


def key_arrow(x, ytip, act):
    """A fat arrow over a key. Red down = press / hold, green up = release, blue double = tap."""
    def fat(cx, y1, y2, colour):  # from y1 to y2, head at y2
        d = 1 if y2 > y1 else -1
        hw, sw, hl = 9, 3.5, 10
        return poly([(cx - sw, y1), (cx + sw, y1), (cx + sw, y2 - d * hl), (cx + hw, y2 - d * hl), (cx, y2),
                     (cx - hw, y2 - d * hl), (cx - sw, y2 - d * hl)], colour)

    def tap(cx):
        top, bot = ytip - 34, ytip
        return (poly([(cx, top), (cx + 8, top + 10), (cx - 8, top + 10)], BLUE)
                + poly([(cx, bot), (cx + 8, bot - 10), (cx - 8, bot - 10)], BLUE)
                + box(cx - 2.5, top + 9, 5, bot - top - 18, BLUE, "none", 0))
    if act == "hold":
        return fat(x, ytip - 34, ytip, RED)
    if act == "release":
        return fat(x, ytip, ytip - 34, GREEN)
    if act == "tap":
        return tap(x)
    if act == "taphold":
        return tap(x - 9) + fat(x + 9, ytip - 34, ytip, RED)
    return ""


def eyepiece(cx, cy, rr, icon=None, readout=(), pointer=True):
    """The view in the eyepiece: target under the red aiming circle, readout below it."""
    cid = f"c{int(cx)}{int(cy)}{abs(hash((icon, tuple(readout)))) % 100000}"
    out = [f"<clipPath id='{cid}'><circle cx='{cx}' cy='{cy}' r='{rr}'/></clipPath>",
           f"<circle cx='{cx}' cy='{cy}' r='{rr}' fill='#f7f6f0' stroke='{INK}' stroke-width='2'/>",
           f"<g clip-path='url(#{cid})'>"]
    py = cy - 12
    if icon:
        ax, ay = AIM[icon]
        out.append(ICONS[icon](cx - ax, py - ay, 1.0))
    out.append("</g>")
    if pointer:
        out.append(f"<circle cx='{cx}' cy='{py}' r='7' fill='none' stroke='{RED}' stroke-width='2.5'/>")
    for t in readout:
        out.append(f"<text x='{cx}' y='{cy + 28}' text-anchor='middle' {MONO} font-size='14' font-weight='bold' "
                   f"fill='{RED}' stroke='#f7f6f0' stroke-width='4' paint-order='stroke'>{esc(t)}</text>")
    return "".join(out)


def panel(i, keys=(None, None), view=None, scene="", caption=(), sight=None, bino=True):
    """One step. view = (icon, readout lines, pointer). scene(ox, oy) draws the outside world in panel coords."""
    ox, oy = M0 + i * (PW + GAP), 66
    out = [box(ox, oy, PW, PH, "#fff", INK, 1.5, 6)]
    if sight:
        out.append(line(ox + PW / 2, oy + PH - 60, ox + sight[0], oy + sight[1], MUTE, 1.5, "5 4"))
    if scene:
        out.append(scene(ox, oy))
    if view:
        icon, readout, pointer = view
        out.append(eyepiece(ox + 52, oy + 52, 46, icon, readout, pointer))
    if bino:
        out.append(binocular(ox, oy, *keys))
    out.append(lines(ox + PW / 2, oy + PH + 22, caption, 12, INK, weight="bold", gap=16))
    return "".join(out)


def strip(name, head, sub, panels, alt):
    W = M0 * 2 + PW * 3 + GAP * 2
    b = [title(W, head, sub)]
    b.extend(panels)
    ly = 66 + PH + 74
    b.append(f"<g transform='translate({W / 2 - 230},{ly})'>")
    b.append(key_arrow(10, 14, "hold") + text(26, 4, "press / hold", 12, INK, "start"))
    b.append(key_arrow(140, 14, "release") + text(156, 4, "release", 12, INK, "start"))
    b.append(key_arrow(250, 14, "tap") + text(266, 4, "tap", 12, INK, "start"))
    b.append(f"<circle cx='346' cy='0' r='7' fill='none' stroke='{RED}' stroke-width='2.5'/>" + text(360, 4, "aiming circle", 12, INK, "start"))
    b.append("</g>")
    write("vector", name, svg(W, ly + 26, "\n".join(b), alt))


def at(icon, dx, dy, s=1.0):
    return lambda ox, oy: ICONS[icon](ox + dx, oy + dy, s)


def both(*fs):
    return lambda ox, oy: "".join(f(ox, oy) for f in fs)


def compass(dx, dy, deg, r=34, to=None, label=None):
    """North arrow at (dx, dy) and the angle `deg` swept clockwise to a line."""
    def f(ox, oy):
        x, y = ox + dx, oy + dy
        a = math.radians(deg - 90)
        L = to or 70
        s = arrow(f"M{x},{y} L{x},{y - 46}", INK, 2) + text(x - 14, y - 40, "N", 13, INK, weight="bold")
        s += line(x, y, x + L * math.cos(a), y + L * math.sin(a), INK, 1.8)
        s += arc(x, y, r, -90, deg - 90, BLUE, 2)
        mid = math.radians((deg - 180) / 2)
        s += text(x + (r + 16) * math.cos(mid) + 4, y + (r + 16) * math.sin(mid) + 4, label or f"{deg}°", 13, BLUE, weight="bold")
        return s
    return f


def vector_strips():
    jeep = at("jeep", 136, 44, .8)
    tower = at("tower", 134, 62, .8)
    strip("distance", "DISTANCE", "Range to one target",
          [panel(0, (None, "hold"), None, at("jeep", 120, 60), ["Hold R until the", "red circle appears"]),
           panel(1, (None, "hold"), ("jeep", (), True), jeep, ["Put the circle", "on the target"], (136, 42)),
           panel(2, (None, "release"), ("jeep", ("106",), True), jeep, ["Release R:", "106 m to the target"], (136, 42))],
          "Vector 21 distance: hold R, put the red circle on the target, release R to read 106 m")
    strip("azimuth", "AZIMUTH", "Bearing to one target",
          [panel(0, ("hold", None), None, at("tower", 120, 70, .9), ["Hold Tab"]),
           panel(1, ("hold", None), ("tower", ("87°",), True), tower, ["Hold until the", "azimuth shows: 87°"], (134, 50)),
           panel(2, bino=False, scene=both(compass(40, 150, 87, 40, 100), at("tower", 142, 150, .8)),
                 caption=["87° from north", "to the target"])],
          "Vector 21 azimuth: hold Tab until the azimuth shows, 87 degrees from north")
    strip("distance-azimuth", "DISTANCE AND AZIMUTH", "Both at once",
          [panel(0, ("hold", "hold"), None, at("jeep", 120, 60), ["Hold R and Tab until", "the red circle appears"]),
           panel(1, ("hold", "hold"), ("jeep", (), True), jeep, ["Put the circle", "on the target"], (136, 42)),
           panel(2, ("release", "release"), ("jeep", ("120° 106",), True), jeep,
                 ["Release both:", "bearing 120°, 106 m"], (136, 42))],
          "Vector 21 distance and azimuth: hold both keys, aim, release both to read 120 degrees and 106 m")

    def height_scene(ox, oy):
        x0, y0, x1, y1 = ox + 98, oy + 100, ox + 150, oy + 46
        return (line(x0, y0, x1, y0, BLUE, 2) + line(x1, y0, x1, y1, BLUE, 2) + line(x0, y0, x1, y1, MUTE, 1.5, "5 4")
                + text(x1 - 4, y0 - 5, "1200", 12, BLUE, "end", "bold")
                + text(x1 + 3, (y0 + y1) / 2 + 4, "180", 12, BLUE, "start", "bold")
                + v_tower(x1, y1, .5, hill=False))
    strip("horizontal-height", "HORIZONTAL DISTANCE AND HEIGHT DIFFERENCE", "Flat distance, and how much higher the target is",
          [panel(0, (None, "taphold"), None, at("tower", 120, 70, .9), ["Tap R once, then hold", "until the red circle appears"]),
           panel(1, (None, "hold"), ("tower", (), True), tower, ["Put the circle", "on the target"], (134, 50)),
           panel(2, (None, "release"), ("tower", ("1200 180",), True), height_scene,
                 ["Release R: 1200 m flat,", "180 m higher"])],
          "Vector 21 horizontal distance and height difference: tap then hold R, aim, release to read 1200 m and 180 m")

    def incl_scene(ox, oy):
        x, y = ox + 22, oy + 170
        a = math.radians(25)
        return (line(x, y, x + 136, y, INK, 1.5) + line(x, y, x + 124 * math.cos(a), y - 124 * math.sin(a), INK, 1.8)
                + arc(x, y, 64, -25, 0, BLUE, 2) + text(x + 84, y - 11, "25°", 13, BLUE, "start", "bold")
                + v_tower(x + 124 * math.cos(a) + 4, y - 124 * math.sin(a) + 2, .5, hill=False)
                + text(ox + PW / 2, oy + 30, "seen from the side", 12, MUTE))
    strip("azimuth-inclination", "AZIMUTH AND INCLINATION", "Bearing, and how steeply you look up or down",
          [panel(0, ("taphold", None), None, at("tower", 120, 70, .9), ["Tap Tab once, then", "hold it"]),
           panel(1, ("hold", None), ("tower", ("87° 25°",), True), tower, ["Bearing 87°,", "25° up"], (134, 50)),
           panel(2, bino=False, scene=incl_scene, caption=["The 25° is the angle", "above level"])],
          "Vector 21 azimuth and inclination: tap then hold Tab to read 87 degrees bearing and 25 degrees up")

    def two_pts(ox, oy, label=""):
        s = v_light(ox + 120, oy + 72, .8) + v_boat(ox + 156, oy + 112, .8)
        if label:
            s += (line(ox + 120, oy + 74, ox + 152, oy + 106, BLUE, 1.8, "4 3")
                  + text(ox + 132, oy + 108, label, 12, BLUE, "end", "bold"))
        return s
    strip("two-point-distance", "DISTANCE BETWEEN TWO POINTS", "How far apart two things are",
          [panel(0, (None, "hold"), None, two_pts, ["Hold R until the", "red circle appears"]),
           panel(1, ("tap", "hold"), ("light", ("1-P",), True), two_pts,
                 ["Circle on point 1, tap Tab", "(still holding R): 1-P"], (120, 52)),
           panel(2, (None, "release"), ("boat", ("1200",), True), lambda ox, oy: two_pts(ox, oy, "1200"),
                 ["Circle on point 2,", "release R: 1200 m apart"], (156, 100))],
          "Vector 21 distance between two points: hold R, tap Tab on the first point (1-P), release R on the second to read 1200 m")

    def arch_scene(ox, oy, dims=False):
        s = v_arch(ox + 130, oy + 92, .7)
        if dims:
            s += (dbl(ox + 160, oy + 64, oy + 92, BLUE, 1.5, "") + text(ox + 156, oy + 110, "63", 12, BLUE, "start", "bold")
                  + f"<line x1='{ox + 109}' y1='{oy + 56}' x2='{ox + 151}' y2='{oy + 56}' stroke='{BLUE}' stroke-width='1.5' "
                  f"marker-start='url(#ahb)' marker-end='url(#ahb)'/>" + text(ox + 130, oy + 49, "120", 12, BLUE, weight="bold"))
        return s
    strip("two-point-horizontal-vertical", "HORIZONTAL AND VERTICAL DISTANCE BETWEEN TWO POINTS",
          "How far apart sideways, and how far apart in height",
          [panel(0, (None, "taphold"), ("arch", (), True), arch_scene,
                 ["Tap R, then hold it;", "circle on point 1"], (112, 66)),
           panel(1, ("tap", "hold"), ("arch", ("1-P",), True), arch_scene,
                 ["Tap Tab once:", "1-P (first point)"], (112, 66)),
           panel(2, (None, "release"), ("arch", ("120 63",), True), lambda ox, oy: arch_scene(ox, oy, True),
                 ["Circle on point 2, release R:", "120 across, 63 up/down"], (150, 92))],
          "Vector 21 horizontal and vertical distance between two points: tap then hold R, tap Tab on point 1, release R on point 2 to read 120 and 63")

    def bear_scene(ox, oy, done=False):
        s = v_light(ox + 122, oy + 128, .7) + v_boat(ox + 140, oy + 38, .7)
        if done:
            s += (line(ox + 122, oy + 96, ox + 138, oy + 40, BLUE, 1.8, "4 3") + text(ox + 124, oy + 70, "1200", 12, BLUE, "end", "bold")
                  + arrow(f"M{ox + 156},{oy + 128} L{ox + 156},{oy + 84}", INK, 1.8) + text(ox + 166, oy + 96, "N", 12, INK, weight="bold")
                  + text(ox + 146, oy + 144, "350°", 12, BLUE, "start", "bold"))
        return s
    strip("two-point-bearing", "HORIZONTAL DISTANCE AND AZIMUTH BETWEEN TWO POINTS",
          "How far, and which way, from point 1 to point 2",
          [panel(0, ("hold", None), None, bear_scene, ["Hold Tab until the", "azimuth appears"]),
           panel(1, ("hold", "tap"), ("light", ("1-P",), True), bear_scene,
                 ["Circle on point 1, tap R", "(still holding Tab): 1-P"], (122, 112)),
           panel(2, ("release", None), ("boat", ("350° 1200",), True), lambda ox, oy: bear_scene(ox, oy, True),
                 ["Circle on point 2, release", "Tab: 350°, 1200 m"], (140, 30))],
          "Vector 21 horizontal distance and azimuth between two points: hold Tab, tap R on point 1, release on point 2 to read 350 degrees and 1200 m")

    def fos_scene(ox, oy, done=False):
        s = v_house(ox + 148, oy + 92, .8) + burst(ox + 120, oy + 30, 13)
        if done:
            s += line(ox + 122, oy + 36, ox + 146, oy + 80, BLUE, 1.8, "4 3")
        return s
    strip("fall-of-shot", "FALL OF SHOT", "The correction from where the round landed to the target",
          [panel(0, ("taphold", None), (None, ("138° 5°",), True), None, ["Tap Tab once, then hold", "until the azimuth shows"]),
           panel(1, ("hold", "tap"), ("house", ("1-P",), True), fos_scene,
                 ["Circle on the target, tap R", "(still holding Tab): 1-P"], (148, 82)),
           panel(2, ("release", None), ("burst", ("r 20 A 5",), True), lambda ox, oy: fos_scene(ox, oy, True),
                 ["Circle on the burst, release", "Tab: right 20, add 5 m"], (120, 34))],
          "Vector 21 fall of shot: tap then hold Tab, tap R on the target (1-P), release Tab on the burst to read the correction r 20 A 5")


# --------------------------------------------------------------- build

def build():
    write("fires", "moa", angle_unit("moa"))
    write("fires", "mil", angle_unit("mil"))
    write("fires", "beaufort-scale", beaufort())
    write("fires", "trajectory-parts", trajectory_parts())
    write("fires", "trajectory-angles", trajectory_angles())
    write("fires", "launch-speeds", launch_speeds())
    write("fires", "coriolis-hemispheres", coriolis())
    write("fires", "eotvos-coriolis", eotvos())
    write("fires", "range-table-key", range_table_key())
    vector_strips()


if __name__ == "__main__":
    build()
