"""Diagrams for the Quiver's Combat skills page (user, 2026-10-09: "combat
skills in the quiver needs pictures").

Writes plain SVG to public/quiver/img/combat/. Same look as the page's older
pictures: white ground, red / green / blue team markers, black arrows, so a
new one and an old one sit side by side without looking like two books.
Fonts are generic sans-serif because an <img> cannot use the page's fonts.

Page modules live in scripts/quiver_pages/ and share scripts/quiver_draw.py.

Run from the site root:  python scripts/quiver-diagrams.py
"""
import glob
import importlib.util
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiver_draw import BLUE, FONT, GREEN, INK, MUTE, RED, arrow, man, svg, text  # noqa: E402

OUT = os.path.join("public", "quiver", "img", "combat")


def cover_concealment():
    b = []
    b.append(text(380, 30, "COVER stops the round.  CONCEALMENT only hides you.", 16, weight="bold"))
    # enemy on the right
    b.append(man(700, 120, RED, 180)); b.append(man(700, 300, RED, 180)); b.append(text(700, 80, "Enemy", 13, RED))
    # cover: a wall
    b.append(f"<rect x='300' y='80' width='26' height='90' fill='#8d8d8d' stroke='{INK}'/>")
    b.append(text(313, 192, "Wall, rubble, berm", 12, MUTE))
    b.append(man(250, 125, GREEN, 0)); b.append(text(250, 160, "Covered", 13, GREEN, weight="bold"))
    b.append(arrow("M685,122 L332,124", RED, 2, "6 5", "ahr"))
    b.append(text(510, 112, "round stops at the wall", 12, RED))
    # concealment: a bush
    for cx, cy, r in ((333, 300, 34), (313, 285, 22), (353, 285, 24), (333, 278, 22)):
        b.append(f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='#7cb342' opacity='.85'/>")
    b.append(text(333, 358, "Bush, tall grass, smoke", 12, MUTE))
    b.append(man(250, 300, GREEN, 0)); b.append(text(190, 340, "Hidden, NOT covered", 13, RED, weight="bold"))
    b.append(arrow("M685,302 L265,302", RED, 2, "6 5", "ahr"))
    b.append(text(510, 292, "round goes straight through", 12, RED))
    return svg(760, 380, "\n".join(b), "Cover stops rounds, concealment only hides you")


def center_peel():
    b = []
    b.append(text(380, 28, "CENTER PEEL  -  the line falls back through its own middle", 16, weight="bold"))
    b.append(text(380, 62, "ENEMY", 14, RED, weight="bold"))
    b.append(f"<line x1='120' y1='72' x2='640' y2='72' stroke='{RED}' stroke-width='2' stroke-dasharray='8 6'/>")
    xs = [200, 300, 460, 560]
    for i, x in enumerate(xs):
        b.append(man(x, 170, GREEN, -90, str(i + 1)))
    b.append(text(380, 205, "1. The line fires to the front", 13, MUTE))
    # outer men turn in and run back through the centre
    b.append(arrow("M200,182 C220,260 340,250 370,300 L370,372", GREEN))
    b.append(arrow("M560,182 C540,260 420,250 390,300 L390,372", GREEN))
    b.append(man(370, 390, GREEN, -90, "1")); b.append(man(390, 420, GREEN, -90, "4"))
    b.append(text(380, 462, "2. Outside men peel in, run behind the line and set up at the rear", 13, MUTE))
    b.append(text(380, 484, "3. The next outside men follow. Repeat until the order to stop", 13, MUTE))
    return svg(760, 500, "\n".join(b), "Center peel: the outside men peel in and fall back through the middle of the line")


def cone_of_fire():
    b = []
    b.append(text(380, 28, "CONE OF FIRE  -  a burst spreads on its way to the target", 16, weight="bold"))
    b.append(man(80, 200, GREEN, 0))
    b.append(f"<path d='M98,200 L640,140 L640,260 z' fill='{RED}' opacity='.15' stroke='{RED}' stroke-dasharray='5 4'/>")
    for k, dy in enumerate((-50, -25, 0, 22, 48)):
        b.append(f"<path d='M98,200 Q370,{200 + dy * 0.4 - 30} 640,{200 + dy}' fill='none' stroke='{RED}' stroke-width='1.5'/>")
    b.append(f"<ellipse cx='650' cy='200' rx='18' ry='66' fill='none' stroke='{INK}' stroke-width='2'/>")
    b.append(text(650, 290, "Beaten zone", 13, INK, weight="bold"))
    b.append(text(380, 330, "Each round takes a slightly different path. The further the target, the wider the spread.", 13, MUTE))
    return svg(760, 350, "\n".join(b), "Cone of fire: the rounds of a burst spread out on the way to the target")


def grazing_fire():
    b = []
    b.append(text(380, 28, "GRAZING FIRE  -  the cone stays below 1 m over the ground", 16, weight="bold"))
    # ground
    b.append(f"<path d='M40,250 L720,250' stroke='{INK}' stroke-width='3'/>")
    b.append(f"<rect x='40' y='250' width='680' height='30' fill='#c8b98f'/>")
    b.append(man(70, 238, GREEN, 0))
    b.append(f"<path d='M86,236 C300,205 520,205 700,246' fill='none' stroke='{RED}' stroke-width='3'/>")
    b.append(f"<line x1='40' y1='190' x2='720' y2='190' stroke='{MUTE}' stroke-dasharray='4 4'/>")
    b.append(text(690, 184, "1 m", 12, MUTE, "end"))
    b.append(f"<rect x='86' y='190' width='610' height='60' fill='{RED}' opacity='.10'/>")
    b.append(text(380, 238, "danger space - anyone standing here is hit", 13, RED, weight="bold"))
    b.append(text(380, 310, "Best on flat or evenly sloping ground, with a machine gun low and on a bipod.", 13, MUTE))
    b.append(text(380, 332, "A dip or a fold in the ground is dead space - the rounds pass over it.", 13, MUTE))
    return svg(760, 350, "\n".join(b), "Grazing fire: the centre of the cone stays under one metre above the ground")


def sector_of_fire():
    b = []
    b.append(text(380, 28, "SECTORS OF FIRE  -  each man owns a slice, and the slices overlap", 16, weight="bold"))
    men = [(230, 380, GREEN, -62), (380, 390, RED, -90), (530, 380, BLUE, -118)]
    for x, y, c, f in men:
        a1, a2 = math.radians(f - 26), math.radians(f + 26)
        r = 320
        p1 = (x + r * math.cos(a1), y + r * math.sin(a1)); p2 = (x + r * math.cos(a2), y + r * math.sin(a2))
        b.append(f"<path d='M{x},{y} L{p1[0]:.0f},{p1[1]:.0f} A{r},{r} 0 0 1 {p2[0]:.0f},{p2[1]:.0f} z' fill='{c}' opacity='.16' stroke='{c}' stroke-width='1.5'/>")
    for x, y, c, f in men:
        b.append(man(x, y, c, f))
    b.append(text(380, 64, "The sectors cross in front of the team: no gap for the enemy to use", 13, INK))
    
    b.append(text(380, 420, "Give each man a left and right limit on something he can see. Overlap them so there is no gap.", 13, MUTE))
    return svg(760, 440, "\n".join(b), "Sectors of fire: each man covers a slice between a left and right limit, and the slices overlap")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("cover-concealment", cover_concealment), ("center-peel", center_peel),
                     ("cone-of-fire", cone_of_fire), ("grazing-fire", grazing_fire),
                     ("sector-of-fire", sector_of_fire)):
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(fn())
        print("wrote", name)
    # one module per Quiver page, each with a build() that writes its own pictures
    here = os.path.dirname(os.path.abspath(__file__))
    for path in sorted(glob.glob(os.path.join(here, "quiver_pages", "*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build()
