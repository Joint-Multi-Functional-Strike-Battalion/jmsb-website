"""Draws the pictures for the Quiver's medical-cls, medical-medic, acre and tfar pages."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiver_draw import *  # noqa: E402,F401,F403

NODE = "#dce7f3"     # flowchart step fill
NOTE = "#f6ecd9"     # side-note fill
SCREEN = "#0b120b"   # monitor background
SCREEN_GRID = "#1d3320"
TRACE = "#39ff5a"


# ---------------------------------------------------------------- flowchart

def node(cx, cy, w, h, label, fill=NODE, bold=False):
    return (box(cx - w / 2, cy - h / 2, w, h, fill, INK, 1.5, 8)
            + text(cx, cy + 5, label, 14, INK, weight="bold" if bold else "normal"))


def cardiac_arrest_flow():
    w, h = 900, 860
    b = [title(w, "CARDIAC ARREST  -  the loop", "Run it until the pulse comes back")]
    bh = 40
    # start / analyse
    b.append(node(450, 95, 140, bh, "START", bold=True))
    b.append(arrow("M450,115 L450,145"))
    b.append(node(450, 168, 250, bh, "Check rhythm and pulse"))
    # split pulse / no pulse
    b.append(line(450, 188, 450, 212))
    b.append(line(300, 212, 620, 212))
    b.append(arrow("M300,212 L300,250")); b.append(arrow("M620,212 L620,250"))
    b.append(text(370, 232, "no pulse", 13, RED, weight="bold"))
    b.append(text(540, 232, "pulse", 13, GREEN, weight="bold"))
    b.append(node(300, 275, 170, bh, "Shockable rhythm?"))
    b.append(node(620, 275, 230, bh, "Pulse back (ROSC): stop", "#dcefdc", True))
    # shockable split
    b.append(line(300, 295, 300, 322))
    b.append(line(170, 322, 450, 322))
    b.append(arrow("M170,322 L170,400")); b.append(arrow("M450,322 L450,360"))
    b.append(text(160, 345, "VT / VF", 13, RED, "end", "bold"))
    b.append(text(385, 314, "asystole / PEA", 13, MUTE, "start"))
    b.append(node(450, 383, 210, bh, "Reversible cause?"))
    b.append(node(170, 423, 150, bh, "SHOCK", "#f6d6d6", True))
    # reversible split
    b.append(line(450, 403, 450, 430))
    b.append(line(390, 430, 620, 430))
    b.append(arrow("M620,430 L620,480"))
    b.append(text(640, 458, "yes", 13, INK, "start", "bold"))
    b.append(text(372, 455, "no", 13, INK, "end", "bold"))
    b.append(node(620, 503, 200, bh, "Fix the cause"))
    # converge on CPR
    b.append(arrow("M390,430 L390,575"))
    b.append(arrow("M170,443 L170,598 L300,598"))
    b.append(text(160, 525, "then", 13, MUTE, "end"))
    b.append(arrow("M620,523 L620,598 L480,598"))
    b.append(text(630, 565, "then", 13, MUTE, "start"))
    b.append(node(390, 598, 180, bh, "CPR", "#f6d6d6", True))
    b.append(arrow("M390,618 L390,700"))
    b.append(text(400, 665, "after 2 minutes of CPR", 13, MUTE, "start"))
    b.append(node(390, 723, 220, bh, "Back to START", bold=True))
    b.append(arrow("M280,723 L40,723 L40,95 L375,95", MUTE, 1.5, "6 5", "ah"))
    # medication note (Medic)
    b.append(box(690, 300, 190, 120, NOTE, INK, 1.2, 6))
    b.append(text(785, 324, "Drugs (Medic, IV)", 14, INK, weight="bold"))
    b.append(lines(704, 350, ["Epinephrine", "Amiodarone - VT/VF only", "Lidocaine - VT/VF only"],
                   13, INK, "start", gap=22))
    # reversible causes note
    b.append(box(690, 600, 190, 170, NOTE, INK, 1.2, 6))
    b.append(text(785, 624, "Reversible causes", 14, INK, weight="bold"))
    b.append(lines(704, 650, ["Hypovolaemia", "Hypoxia", "Tension pneumothorax", "Haemothorax", "Opioids on board"],
                   13, INK, "start", gap=22))
    b.append(text(450, 820, "Medic: one of amiodarone or lidocaine, never both inside 5 to 10 minutes.", 13, MUTE))
    return svg(w, h, "\n".join(b), "Cardiac arrest flow: check pulse, shock if shockable, fix reversible causes, CPR for two minutes, repeat")


# ---------------------------------------------------------------- auscultation

def auscultation_sites():
    w, h = 640, 580
    b = [title(w, "WHERE TO LISTEN", "Casualty facing you: his left is on your right")]
    sk = "#e9e4d8"
    # torso outline: head, neck, shoulders, trunk
    b.append(f"<circle cx='320' cy='118' r='40' fill='{sk}' stroke='{INK}' stroke-width='2'/>")
    b.append(f"<path d='M302,150 L302,184 L338,184 L338,150' fill='{sk}' stroke='{INK}' stroke-width='2'/>")
    b.append(f"<path d='M302,180 C270,188 225,190 200,205 C178,218 172,250 176,300 L190,300 "
             f"C196,380 205,440 212,560 L428,560 C435,440 444,380 450,300 L464,300 "
             f"C468,250 462,218 440,205 C415,190 370,188 338,180 z' fill='{sk}' stroke='{INK}' stroke-width='2'/>")
    # collarbones, breastbone
    b.append(f"<path d='M318,202 C290,207 255,203 222,214 M322,202 C350,207 385,203 418,214' fill='none' stroke='{MUTE}' stroke-width='1.5'/>")
    b.append(line(320, 207, 320, 360, MUTE, 1.5))

    def p(x, y):  # map original site positions onto this torso
        return 320 + (x - 450) * 1.0, 200 + (y - 330) * 1.05

    lungs = [(400, 345), (502, 345), (398, 420), (502, 420), (370, 494), (537, 494), (360, 573), (549, 573)]
    heart = [(425, 420), (478, 420), (478, 447), (478, 475)]
    for x, y in lungs:
        X, Y = p(x, y)
        b.append(f"<circle cx='{X:.0f}' cy='{Y:.0f}' r='10' fill='{BLUE}' stroke='#fff' stroke-width='2.5'/>")
    for x, y in heart:
        X, Y = p(x, y)
        b.append(f"<circle cx='{X:.0f}' cy='{Y:.0f}' r='10' fill='{RED}' stroke='#fff' stroke-width='2.5'/>")
    lx, ly = p(370, 494)
    hx, hy = p(478, 475)
    b.append(line(110, 150, lx - 7, ly - 7, BLUE, 3))
    b.append(text(30, 118, "Lungs", 15, BLUE, "start", "bold"))
    b.append(text(30, 138, "both sides, compare", 12, MUTE, "start"))
    b.append(line(hx + 7, hy + 7, 520, 500, RED, 3))
    b.append(text(610, 522, "Heart", 15, RED, "end", "bold"))
    b.append(text(610, 542, "along the breastbone", 12, MUTE, "end"))
    b.append(text(120, 260, "his right", 13, MUTE, "middle", "bold"))
    b.append(text(520, 260, "his left", 13, MUTE, "middle", "bold"))
    return svg(w, h, "\n".join(b), "Listening sites: eight lung sites in pairs on both sides of the chest, four heart sites along the breastbone")


# ---------------------------------------------------------------- EKG strips

def strip(name, label, ys, note):
    """A monitor strip: dark screen, faint grid, green trace. ys = samples in -1..1 across the width."""
    w, h = 720, 170
    top, bot = 34, h - 10
    mid = (top + bot) / 2
    amp = (bot - top) / 2 - 6
    b = [f"<rect width='{w}' height='{h}' rx='6' fill='{SCREEN}'/>"]
    for x in range(20, w, 25):
        b.append(f"<line x1='{x}' y1='{top}' x2='{x}' y2='{bot}' stroke='{SCREEN_GRID}' stroke-width='1'/>")
    for y in range(int(top), int(bot) + 1, 25):
        b.append(f"<line x1='10' y1='{y}' x2='{w - 10}' y2='{y}' stroke='{SCREEN_GRID}' stroke-width='1'/>")
    n = len(ys)
    pts = " ".join(f"{10 + i * (w - 20) / (n - 1):.1f},{mid - v * amp:.1f}" for i, v in enumerate(ys))
    b.append(f"<polyline points='{pts}' fill='none' stroke='{TRACE}' stroke-width='2' stroke-linejoin='round'/>")
    b.append(text(14, 22, label, 14, TRACE, "start", "bold"))
    b.append(text(w - 14, 22, note, 13, "#9fd6a6", "end"))
    write("medical", name, svg(w, h, "\n".join(b), label))


def gauss(t, c, wd, a):
    return a * math.exp(-((t - c) / wd) ** 2)


def sinus(t):
    """One beat per unit of t: P, QRS, T."""
    f = t % 1.0
    return (gauss(f, .18, .035, .14) + gauss(f, .30, .010, -.15) + gauss(f, .33, .012, .95)
            + gauss(f, .36, .012, -.30) + gauss(f, .58, .06, .25))


def ekgs():
    N = 900
    rnd = random.Random(7)
    # sinus: about six beats across
    strip("ekg-sinus", "SINUS", [sinus(i / N * 5.6 + .2) for i in range(N)], "P - QRS - T, regular. Has a pulse (or PEA)")
    # pulseless VT: fast, wide, regular, no P or T
    strip("ekg-pulseless-vt", "PULSELESS VT", [
        .85 * math.sin(2 * math.pi * i / N * 16) ** 3 * (1 if math.sin(2 * math.pi * i / N * 16) > 0 else .7)
        for i in range(N)], "wide, fast, regular. Shockable")
    # VF: chaotic sum of drifting sines plus noise
    ph = [rnd.random() * 6 for _ in range(4)]
    strip("ekg-vf", "VF", [
        (.28 * math.sin(i * .21 + ph[0]) + .18 * math.sin(i * .37 + ph[1]) + .12 * math.sin(i * .61 + ph[2])
         + .08 * math.sin(i * .05 + ph[3])) * (.7 + .3 * math.sin(i * .013)) + rnd.uniform(-.06, .06)
        for i in range(N)], "chaotic, no complexes. Shockable")
    # asystole: almost flat, slow wander
    strip("ekg-asystole", "ASYSTOLE", [.03 * math.sin(i * .02) + rnd.uniform(-.012, .012) for i in range(N)],
          "flat line. Not shockable")


# ---------------------------------------------------------------- radio key tables

def acre_keys():
    rows = [["Radio PTT", "Caps Lock"],
            ["Alternate PTT 1", "Shift + Caps Lock"],
            ["Alternate PTT 2", "Ctrl + Caps Lock"],
            ["Alternate PTT 3", "Alt + Caps Lock"],
            ["Open / close radio", "Alt + Ctrl + Caps Lock"],
            ["Cycle radio", "Alt + Shift + Caps Lock"],
            ["Radio in left ear", "Ctrl + Shift + Left Arrow"],
            ["Radio in right ear", "Ctrl + Shift + Right Arrow"],
            ["Radio in both ears", "Ctrl + Shift + Up Arrow"]]
    w = 600
    t, th = table(20, 50, [("Action", 260), ("Keys", 300)], rows, 14)
    b = [title(w, "ACRE KEYS"), t]
    write("radio", "acre-keys", svg(w, 50 + th + 20, "\n".join(b), "ACRE default keys: push-to-talk, alternate PTTs, open, cycle and ear selection"))


def tfar_keys():
    rows = [["Push-to-talk in TeamSpeak", "Direct speech (talking out loud)."],
            ["Caps Lock", "Talk on the radio."],
            ["Ctrl + P", "Open the personal radio (it must be in the radio slot). With several\n"
                         "radios you pick one, set it as active (the one you transmit on),\n"
                         "or copy settings from another radio with the same encryption code."],
            ["Ctrl + + [/]", "Cycle through the shortwave radios you carry."],
            ["Ctrl + Up / Left / Right Arrow", "Quick-switch the shortwave radio's stereo (ear)."],
            ["Num 1 - 8", "Quick-switch shortwave channels."],
            ["Ctrl + Tab", "Change your voice volume: whisper, normal or yell.\n"
                           "Does not change how loud you are on the radio."],
            ["Ctrl + ]", "Next personal radio."],
            ["Ctrl + [", "Previous personal radio."],
            ["Ctrl + Left / Up / Right", "Change the personal radio's stereo (ear)."],
            ["Esc", "Close the radio interface."]]
    w = 820
    t, th = table(20, 50, [("Keys", 250), ("Action", 530)], rows, 14)
    b = [title(w, "TFAR KEYS"), t]
    write("radio", "tfar-keys", svg(w, 50 + th + 20, "\n".join(b), "TFAR default keys and what they do"))


def build():
    write("medical", "cardiac-arrest-flow", cardiac_arrest_flow())
    write("medical", "auscultation-sites", auscultation_sites())
    ekgs()
    acre_keys()
    tfar_keys()


if __name__ == "__main__":
    build()
