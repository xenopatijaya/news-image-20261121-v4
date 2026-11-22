#!/usr/bin/env python3
"""Draw the Saturday 21 November 2026 front page for news-image-20261121.

One page, no photographs: every panel below is drawn with PIL primitives.
The page carries 54 stories, each dated against its named source.
"""
import random

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
EDGE = 18
SPAN = PAGE_W - 2 * EDGE

PAPER = (247, 241, 227)
PAPER_DIM = (238, 229, 205)
INK = (32, 34, 40)
SOFT = (107, 98, 87)
RED = (179, 35, 27)
RED_DEEP = (142, 26, 20)
NAVY = (26, 46, 78)
NAVY_SOFT = (43, 68, 106)
GOLD = (190, 138, 20)
CREAM = (255, 252, 244)

FONT_DIR = "/usr/share/fonts/truetype/"
SERIF_B = FONT_DIR + "dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = FONT_DIR + "liberation/LiberationSerif-Italic.ttf"
SANS_R = FONT_DIR + "dejavu/DejaVuSans.ttf"
SANS_B = FONT_DIR + "dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def width(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, limit):
    """Greedy word wrap; returns a list of lines no wider than limit."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if width(draw, trial, fnt) <= limit:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def para(draw, xy, text, fnt, fill, limit, leading, max_lines=None):
    """Draw wrapped text; returns the y just past the last line."""
    x, y = xy
    lines = wrap(draw, text, fnt, limit)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


BIG_NUMBERS = [
    ("13", "the day COP31 reached - one past the day it was meant to end"),
    ("3", "Houthi ballistic missiles destroyed above Riyadh"),
    ("6.7", "magnitude of the earthquake in Junin, Peru"),
    ("146", "people aboard the jet that diverted to Davao - all safe"),
    ("67-5", "Scotland's rout of Japan at Murrayfield - eleven tries"),
    ("124*", "K L Rahul's score at tea on day three in Wellington"),
]

REGION_CHIPS = [
    "MIDDLE EAST 12", "EUROPE 9", "N. AMERICA 7", "SOUTH ASIA 6",
    "AFRICA 6", "EAST ASIA 5", "S. AMERICA 4", "OCEANIA 3", "SE ASIA 2",
]

LEADS = [
    {
        "scene": "antalya",
        "place_tag": "ANTALYA - DAY 13",
        "src_tag": "AP - REUTERS - GUARDIAN",
        "kicker": "CLIMATE - ANTALYA, TURKIYE",
        "headline": "COP31 runs past its deadline",
        "body": ("A thirteenth day of talks, with almost 200 nations still "
                 "deadlocked over fossil fuels; the draft text drops any "
                 "mention of them, and the $120bn finance goal besides. "
                 "(AP, Reuters, Guardian)"),
    },
    {
        "scene": "riyadh",
        "place_tag": "RIYADH - BEFORE DAWN",
        "src_tag": "AFP - ARAB NEWS",
        "kicker": "CONFLICT - RIYADH",
        "headline": "Three missiles downed over Riyadh",
        "body": ("Three Houthi ballistic missiles were destroyed above the "
                 "capital before dawn on Saturday; a drone heading south "
                 "was brought down too. (AFP, Arab News)"),
    },
    {
        "scene": "peru",
        "place_tag": "JUNIN - 00:09 UTC",
        "src_tag": "USGS - IGP",
        "kicker": "EARTHQUAKE - JUNIN, PERU",
        "headline": "M6.7 in Peru's high Andes",
        "body": ("Struck at 00:09 UTC, 9 km north-east of Carhuamayo and "
                 "108 km deep. Felt in Lima and along the coast; no deaths, "
                 "and no tsunami risk. (USGS, IGP)"),
    },
]

CARDS_A = [
    {
        "glyph": "bridge", "tint": (214, 226, 238), "tag": "UKRAINE - KYIV",
        "headline": "Crimea bridge 'will not stay'",
        "body": ("Zelensky warns the bridge will fall, and reports more "
                 "double-tap strikes. (NBC)"),
    },
    {
        "glyph": "drone", "tint": (238, 222, 205), "tag": "HORMUZ STRAIT",
        "headline": "Iran says it downed a US drone",
        "body": ("Tehran claims the shoot-down; Washington has not "
                 "confirmed. (IRIB)"),
    },
    {
        "glyph": "atom", "tint": (226, 232, 214), "tag": "NUCLEAR - TEHRAN",
        "headline": "Iran uranium stays in-country",
        "body": ("The stockpile stays put, the minister says, while Tehran "
                 "seeks a 'fair solution'. (ToI)"),
    },
    {
        "glyph": "tag", "tint": (240, 228, 228), "tag": "TECH TAX - WASHINGTON",
        "headline": "Trump vows tax on data centres abroad",
        "body": ("A 'tremendous' penalty vowed for centres built abroad; "
                 "no detail yet. (ABC)"),
    },
    {
        "glyph": "speech", "tint": (222, 230, 240), "tag": "ASIA - BEIJING-TOKYO",
        "headline": "China tells Japan to 'correct' Taiwan words",
        "body": ("Beijing wants a correction; Tokyo says its stance is "
                 "unchanged. (AFP)"),
    },
    {
        "glyph": "plane", "tint": (210, 232, 230), "tag": "AVIATION - DAVAO",
        "headline": "146 safe after jet diverts to Davao",
        "body": ("PX19 lands on an engine-fire indication; everyone aboard "
                 "safe. (Airline, AP)"),
    },
]

CARDS_B = [
    {
        "glyph": "nodes", "tint": (228, 224, 240), "tag": "AI - CANBERRA",
        "headline": "Australia, China agree to AI talks",
        "body": ("Albanese ends an 11-day trip with a deal to talk on AI. "
                 "(ABC)"),
    },
    {
        "glyph": "coin", "tint": (242, 232, 200), "tag": "MARKETS",
        "headline": "Bitcoin slips below $59,000",
        "body": ("$58,983 early Saturday, down 3.9% in a day; ether "
                 "$1,625. (CoinGecko)"),
    },
    {
        "glyph": "flag", "tint": (224, 224, 224), "tag": "F1 - LAS VEGAS",
        "headline": "Russell fastest in damp final practice",
        "body": ("1:34.041 in a messy, wet session under the lights. "
                 "(Formula 1)"),
    },
    {
        "glyph": "cricket", "tint": (216, 236, 216), "tag": "CRICKET - WELLINGTON",
        "headline": "Rahul 124* as India take charge",
        "body": ("A 13th Test hundred, his first in NZ; 344/2 at tea, "
                 "replying to 368. (AFP)"),
    },
    {
        "glyph": "rugby", "tint": (206, 222, 240), "tag": "RUGBY - MURRAYFIELD",
        "headline": "Scotland rout Japan 67-5",
        "body": ("Eleven tries in Edinburgh; hat-tricks for McConnell "
                 "and Graham. (Reuters)"),
    },
]

BRIEFS = [
    "COP31 firms: 123 urge a bold power deal (Reuters)",
    "1.5C overshoot admitted in the draft (Reuters)",
    "Next summit: Addis Ababa, Nov 2027 (AP)",
    "Houthis threaten Jeddah and Shuqaiq (AFP)",
    "Denmark weighs Russian visa curbs (Al Jazeera)",
    "Melania's wish: another ceasefire (Daily Mail)",
    "Trump defends calling Putin a 'friend' (TOI)",
    "Iran war nears its ninth month (One Turn)",
    "Hurricanes beat Thunder by 8 wickets (CricTracker)",
    "India 'takes note' of the ICJ ruling (LogicHub)",
    "Sejong derailment: 5 of 21 cars off rails (Yonhap)",
    "Premier League MD11: Man City v Fulham (EPL)",
    "At lunch: Rahul 93*, Padikkal 53* (Reuters)",
    "Poland seeks more Sentry forces (SOFX)",
    "Hosts blasted: 'worst COP ever' (Guardian)",
    "SpaceX launches the USSF-317 satellite (Space Launch Live)",
    "Loss-and-damage fund to triple (AP)",
    "Education Cannot Wait holds 10% of $52m (ECW)",
    "SCO in Delhi: 10 states and partners (ANI)",
    "Korea 'dangers' discussed at summit (Korea Times)",
    "Double-tap strikes rising, says Zelensky (Kyiv Ind.)",
    "Ebola alert kept: Congo cases 11,613 (Today News Africa)",
    "Angola: $180m for 10% of De Beers (Juba Global)",
    "Ghana-Morocco: first all-African amputee final (Juba Global)",
    "Brazil storm: 3 dead, 5,000 homes wrecked (Reuters)",
    "Bolsonaro in ICU with a bowel obstruction (UPI)",
    "Thailand: Myanmar ties stay despite ICJ (Bangkok Post)",
    "Delhi thanks Bulgaria: seafarers repatriated (IANS)",
    "Blind cricket: India protest the NRR title (Asia Daily)",
    "Seoul: $75k reward for exam-cheat tips (IANS)",
    "Ireland stun the Springboks 20-17 in Dublin (Reuters)",
    "Wallabies edge Wales 29-26 in Cardiff (Reuters)",
    "Barrett's 150th Test: England win 37-12 (allblacks.com)",
    "Mexico captures 'Chapo Isidro'; 11 die after (BBC)",
    "Russian missile kills two in Kryvyi Rih (Al Jazeera)",
    "Somalia expels the UAE ambassador (African Mirror)",
    "Israeli strike on Gaza food vehicle kills 3 (Al Jazeera)",
    "Iran says it hit US bases in Bahrain (Al Jazeera)",
    "Bred mosquitoes cut dengue 69% in Brazil (AP)",
    "Tunisia jails truth chief for five years (African Mirror)",
]

# (lon, lat) for the leads and features, numbered 1-14 on the map.
PINS = [
    (30.7, 36.9), (46.7, 24.6), (-75.2, -11.5), (30.5, 50.4),
    (56.3, 27.1), (51.4, 35.7), (-77.0, 38.9), (116.4, 39.9),
    (125.6, 7.1), (149.1, -35.3), (-74.0, 40.7), (-115.1, 36.2),
    (174.8, -41.3), (-3.2, 55.9),
]


def scene_antalya(draw, x, y, w, h):
    """Dawn sky, a long conference hall, a row of flags."""
    bands = [(250, 214, 165), (248, 190, 140), (243, 166, 118),
             (233, 143, 102)]
    step = h // (len(bands) + 2)
    for i, colour in enumerate(bands):
        draw.rectangle([x, y + i * step, x + w, y + (i + 1) * step],
                       fill=colour)
    draw.rectangle([x, y + 4 * step, x + w, y + h], fill=(226, 128, 92))
    draw.ellipse([x + w - 74, y + 8, x + w - 40, y + 42], fill=(255, 236, 180))
    hall_y = y + h - 26
    draw.rectangle([x + 26, hall_y, x + w - 26, y + h], fill=(38, 44, 58))
    draw.pieslice([x + w // 2 - 30, hall_y - 20, x + w // 2 + 30,
                   hall_y + 14], 180, 360, fill=(38, 44, 58))
    for wx in range(x + 36, x + w - 30, 18):
        draw.rectangle([wx, hall_y + 7, wx + 8, hall_y + 14],
                       fill=(255, 214, 120))
    flag_cols = [(179, 35, 27), (26, 46, 78), (24, 110, 60), (190, 138, 20)]
    for i in range(9):
        fx = x + 14 + i * 13
        draw.line([fx, hall_y - 16, fx, hall_y], fill=(30, 30, 30), width=1)
        draw.rectangle([fx + 1, hall_y - 16, fx + 9, hall_y - 10],
                       fill=flag_cols[i % len(flag_cols)])


def scene_riyadh(draw, x, y, w, h):
    """Night sky, skyline, three interception bursts."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 24, 46))
    rng = random.Random(11)
    for _ in range(46):
        sx = x + rng.randrange(4, w - 4)
        sy = y + rng.randrange(3, h - 26)
        draw.point((sx, sy), fill=(220, 226, 240))
    draw.arc([x + 18, y + 8, x + 44, y + 34], 40, 300, fill=(240, 230, 190),
             width=3)
    base = y + h
    towers = [(0, 26), (26, 38), (58, 30), (88, 46), (124, 34), (156, 52),
              (196, 36), (232, 44), (268, 30), (296, 40)]
    for off, th in towers:
        draw.rectangle([x + off, base - th, x + off + 22, base],
                       fill=(8, 12, 24))
        for wy in range(base - th + 5, base - 5, 8):
            if rng.random() < 0.55:
                draw.rectangle([x + off + 5, wy, x + off + 9, wy + 3],
                               fill=(255, 205, 105))
    for cx, cy in [(x + 78, y + 20), (x + 168, y + 13), (x + 252, y + 24)]:
        for dx, dy in [(0, -7), (5, -5), (7, 0), (5, 5), (0, 7), (-5, 5),
                       (-7, 0), (-5, -5)]:
            draw.line([cx, cy, cx + dx, cy + dy], fill=(255, 240, 200),
                      width=2)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 250, 230))
    draw.arc([x + 30, y + 26, x + 120, y + 62], 200, 320,
             fill=(200, 210, 230), width=1)
    draw.arc([x + 190, y + 30, x + 292, y + 66], 220, 340,
             fill=(200, 210, 230), width=1)


def scene_peru(draw, x, y, w, h):
    """Andean ridges with snow caps over a seismograph trace."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 238))
    draw.ellipse([x + 16, y + 7, x + 42, y + 33], fill=(255, 240, 180))
    far = [(x, y + 44), (x + 52, y + 18), (x + 104, y + 40),
           (x + 158, y + 14), (x + 214, y + 38), (x + 268, y + 20),
           (x + w, y + 42), (x + w, y + h), (x, y + h)]
    draw.polygon(far, fill=(110, 128, 152))
    for px, py in [(x + 52, y + 18), (x + 158, y + 14), (x + 268, y + 20)]:
        draw.polygon([(px - 11, py + 11), (px, py), (px + 11, py + 11),
                      (px + 4, py + 8), (px, py + 12), (px - 4, py + 8)],
                     fill=(250, 250, 246))
    near = [(x, y + 58), (x + 70, y + 34), (x + 140, y + 56),
            (x + 210, y + 32), (x + 280, y + 54), (x + w, y + 40),
            (x + w, y + h), (x, y + h)]
    draw.polygon(near, fill=(70, 84, 104))
    band_y = y + h - 17
    draw.rectangle([x, band_y, x + w, y + h], fill=(24, 28, 38))
    trace = []
    rng = random.Random(5)
    for i in range(41):
        tx = x + 6 + i * (w - 12) / 40
        amp = 2 if i < 15 or i > 30 else rng.choice([5, 8, 11, 7, 10])
        trace.append((tx, band_y + 8 + (amp if i % 2 else -amp)))
    draw.line(trace, fill=(255, 92, 72), width=2)


def glyph(draw, kind, x, y, s):
    """Tiny flat icons for the card header bands; s is the box size."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "bridge":
        draw.line([x + 2, y + s - 4, x + s - 2, y + s - 4], fill=INK, width=2)
        draw.arc([x + 3, y + 6, x + s - 3, y + s + 4], 180, 360, fill=INK,
                 width=2)
        for tx in (x + 7, x + s - 9):
            draw.line([tx, y + 4, tx, y + s - 4], fill=INK, width=2)
    elif kind == "drone":
        for dx, dy in [(4, 4), (s - 6, 4), (4, s - 6), (s - 6, s - 6)]:
            draw.ellipse([x + dx - 3, y + dy - 2, x + dx + 3, y + dy + 2],
                         outline=INK, width=1)
        draw.rectangle([cx - 4, cy - 3, cx + 4, cy + 3], fill=INK)
        draw.line([x + 4, y + 4, cx, cy], fill=INK, width=1)
        draw.line([x + s - 6, y + 4, cx, cy], fill=INK, width=1)
    elif kind == "atom":
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=INK)
        for ang in (0, 60, 120):
            box = [x + 2, y + 6, x + s - 2, y + s - 6]
            draw.ellipse(box, outline=INK, width=1)
            break
        draw.arc([x + 2, y + 6, x + s - 2, y + s - 6], 20, 160, fill=INK,
                 width=1)
        draw.arc([x + 2, y + 6, x + s - 2, y + s - 6], 200, 340, fill=INK,
                 width=1)
    elif kind == "tag":
        draw.polygon([(x + 4, y + 6), (x + s - 8, y + 6), (x + s - 3, y + 11),
                      (x + s - 3, y + s - 5), (x + 4, y + s - 5)],
                     outline=INK, width=2)
        draw.ellipse([x + 7, y + 9, x + 11, y + 13], fill=INK)
    elif kind == "speech":
        draw.rounded_rectangle([x + 3, y + 5, x + s - 8, y + s - 9],
                               radius=4, outline=INK, width=2)
        draw.rounded_rectangle([x + 9, y + 10, x + s - 3, y + s - 4],
                               radius=4, outline=INK, width=2)
    elif kind == "plane":
        draw.polygon([(x + 3, cy), (x + s - 4, cy - 6), (x + s - 8, cy),
                      (x + s - 4, cy + 6)], fill=INK)
        draw.polygon([(cx - 2, cy), (cx - 7, cy - 8), (cx + 1, cy - 8)],
                     fill=INK)
        draw.polygon([(x + 5, cy), (x + 2, cy - 6), (x + 8, cy)],
                     fill=INK)
    elif kind == "nodes":
        pts = [(x + 6, y + 7), (x + s - 7, y + 6), (cx, cy + 3),
               (x + 7, y + s - 6), (x + s - 6, y + s - 7)]
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if (i + j) % 2 == 0:
                    draw.line([pts[i], pts[j]], fill=INK, width=1)
        for px, py in pts:
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=INK)
    elif kind == "coin":
        draw.ellipse([x + 4, y + 3, x + s - 4, y + s - 3], outline=INK,
                     width=2)
        bf = font(SANS_B, s - 12)
        draw.text((cx - 4, y + 5), "B", font=bf, fill=INK)
        draw.line([cx - 1, y + 6, cx - 1, y + s - 6], fill=INK, width=1)
        draw.line([cx + 2, y + 6, cx + 2, y + s - 6], fill=INK, width=1)
    elif kind == "flag":
        for r in range(3):
            for c in range(6):
                if (r + c) % 2 == 0:
                    draw.rectangle([x + 3 + c * 4, y + 6 + r * 4,
                                    x + 7 + c * 4, y + 10 + r * 4],
                                   fill=INK)
        draw.line([x + 3, y + s - 4, x + s - 3, y + s - 4], fill=INK,
                  width=2)
    elif kind == "cricket":
        draw.line([x + 8, y + s - 5, x + s - 9, y + 6], fill=INK, width=4)
        draw.ellipse([x + s - 12, y + s - 12, x + s - 5, y + s - 5],
                     fill=RED)
    elif kind == "rugby":
        draw.ellipse([x + 4, y + 8, x + s - 4, y + s - 8], outline=INK,
                     width=2)
        draw.line([cx - 4, cy, cx + 4, cy], fill=INK, width=1)
        for dx in (-2, 0, 2):
            draw.line([cx + dx, cy - 2, cx + dx, cy + 2], fill=INK, width=1)
        draw.line([x + 6, y + s - 3, x + 6, y + 8], fill=INK, width=1)
        draw.line([x + s - 6, y + s - 3, x + s - 6, y + 8], fill=INK,
                  width=1)


LAND = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 70), (-85, 66),
     (-80, 62), (-75, 45), (-70, 42), (-76, 35), (-80, 32), (-81, 26),
     (-84, 30), (-90, 21), (-97, 16), (-105, 20), (-110, 23), (-114, 29),
     (-120, 34), (-124, 40), (-124, 46), (-130, 55), (-150, 60), (-165, 60)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-55, 5), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-41, -22), (-48, -27), (-52, -33), (-57, -38),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54), (-73, -46),
     (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-79, -8), (-80, -4),
     (-77, 1)],
    # Africa
    [(-17, 15), (-10, 29), (-6, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (48, 11), (51, 10), (44, 0), (40, -8), (39, -18),
     (37, -26), (32, -29), (25, -34), (19, -35), (17, -30), (15, -22),
     (13, -12), (12, -6), (9, -1), (9, 4), (-8, 4), (-13, 8)],
    # Europe
    [(-9, 43), (-2, 44), (0, 46), (-4, 48), (-1, 50), (3, 51), (7, 54),
     (8, 57), (12, 56), (18, 56), (21, 59), (25, 60), (30, 62), (28, 66),
     (35, 65), (42, 62), (46, 58), (44, 50), (40, 46), (34, 45), (30, 41),
     (27, 37), (23, 36), (20, 39), (16, 38), (13, 41), (10, 44), (6, 43),
     (3, 42), (-2, 37), (-6, 36), (-9, 37)],
    # Asia, the Middle East to Siberia and down to India and SE Asia
    [(30, 36), (36, 36), (42, 31), (48, 30), (50, 29), (54, 26), (57, 26),
     (61, 25), (66, 25), (70, 22), (72, 20), (75, 13), (77, 8), (80, 15),
     (85, 19), (88, 22), (92, 16), (95, 16), (98, 10), (100, 6), (103, 5),
     (106, 9), (108, 13), (110, 20), (115, 23), (120, 28), (122, 34),
     (126, 38), (129, 33), (132, 34), (136, 35), (140, 38), (142, 46),
     (150, 50), (158, 52), (168, 60), (178, 65), (168, 66), (150, 70),
     (130, 71), (110, 72), (90, 70), (75, 68), (64, 64), (55, 62),
     (48, 55), (44, 48), (38, 42), (33, 38)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),
     (140, 45), (138, 38), (135, 34), (131, 32)],
    # Indonesia and Papua (coarse)
    [(95, 5), (102, -2), (108, -4), (114, -2), (120, -4), (128, -3),
     (136, -3), (144, -4), (150, -6), (146, -8), (138, -7), (128, -7),
     (118, -8), (108, -7), (100, -3)],
    # Australia
    [(113, -22), (114, -30), (118, -35), (124, -33), (130, -32),
     (135, -35), (138, -35), (141, -38), (146, -38), (150, -37),
     (153, -30), (153, -25), (150, -22), (146, -19), (142, -15),
     (142, -11), (139, -14), (136, -15), (135, -12), (131, -11),
     (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (170, -43), (172, -41), (174, -40), (176, -37),
     (178, -37), (176, -40), (174, -42), (172, -43), (169, -46)],
]


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    title_f = font(SANS_B, 11)
    draw.text((x + 12, y + 7), "THE WORLD ON SATURDAY", font=title_f,
              fill=CREAM)
    sub_f = font(SANS_R, 8.5)
    draw.text((x + 12, y + 22),
              "where the leads and features happened - pins 1-14",
              font=sub_f, fill=(178, 194, 218))
    map_y = y + 36
    map_h = h - 40

    def project(lon, lat):
        px = x + 12 + (lon + 180) / 360 * (w - 24)
        py = map_y + (78 - lat) / 136 * map_h
        return px, py

    for blob in LAND:
        pts = [project(lon, lat) for lon, lat in blob]
        draw.polygon(pts, fill=(96, 118, 148))
    pin_f = font(SANS_B, 8)
    placed = []
    for num, (lon, lat) in enumerate(PINS, start=1):
        px, py = project(lon, lat)
        gx, gy = px, py
        for _ in range(3):
            if all((gx - ox) ** 2 + (gy - oy) ** 2 > 169
                   for ox, oy in placed):
                break
            gx += 11
            gy += 6
        if (gx, gy) != (px, py):
            draw.line([px, py, gx, gy], fill=(200, 208, 224), width=1)
        placed.append((gx, gy))
        draw.ellipse([gx - 6, gy - 6, gx + 6, gy + 6], fill=RED,
                     outline=CREAM, width=1)
        label = str(num)
        draw.text((gx - width(draw, label, pin_f) / 2, gy - 4.5), label,
                  font=pin_f, fill=CREAM)


SCENES = {"antalya": scene_antalya, "riyadh": scene_riyadh, "peru": scene_peru}


def draw_lead(draw, lead, num, x, y, w):
    SCENES[lead["scene"]](draw, x, y, w, 82)
    tag_f = font(SANS_B, 8)
    for tag, tx, anchor_right in ((lead["place_tag"], x + 6, False),
                                  (lead["src_tag"], x + w - 6, True)):
        tw = width(draw, tag, tag_f)
        bx = tx - tw - 6 if anchor_right else tx
        by = y + 5 if not anchor_right else y + 82 - 17
        draw.rectangle([bx, by, bx + tw + 12, by + 13], fill=(20, 22, 30))
        draw.text((bx + 6, by + 2), tag, font=tag_f, fill=CREAM)
    kick_y = y + 90
    draw.ellipse([x, kick_y, x + 15, kick_y + 15], fill=RED)
    num_f = font(SANS_B, 9)
    n = str(num)
    draw.text((x + 7.5 - width(draw, n, num_f) / 2, kick_y + 2.5), n,
              font=num_f, fill=CREAM)
    draw.text((x + 20, kick_y + 2), lead["kicker"], font=font(SANS_B, 9),
              fill=RED_DEEP)
    head_f = font(SERIF_B, 16)
    hy = para(draw, (x, kick_y + 20), lead["headline"], head_f, INK, w, 19,
              max_lines=2)
    para(draw, (x, hy + 2), lead["body"], font(SANS_R, 9.3), (52, 52, 56),
         w, 12, max_lines=4)


def draw_card(draw, card, num, x, y, w):
    draw.rectangle([x, y, x + w, y + 104], outline=(196, 186, 164), width=1)
    draw.rectangle([x, y, x + w, y + 26], fill=card["tint"])
    glyph(draw, card["glyph"], x + 3, y + 2, 22)
    draw.text((x + 29, y + 8), card["tag"], font=font(SANS_B, 7.5),
              fill=(70, 62, 50))
    num_f = font(SANS_B, 10)
    n = str(num)
    draw.text((x + w - 6 - width(draw, n, num_f), y + 6), n, font=num_f,
              fill=RED)
    hy = para(draw, (x + 7, y + 32), card["headline"], font(SANS_B, 10.5),
              INK, w - 14, 13, max_lines=2)
    para(draw, (x + 7, hy + 2), card["body"], font(SANS_R, 8.3),
         (58, 56, 52), w - 14, 10.5, max_lines=3)


def build_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)

    # Kicker bar
    draw.rectangle([0, 0, PAGE_W, 22], fill=RED)
    kick = ("SATURDAY EDITION - 54 DATE-CHECKED STORIES - 9 REGIONS - "
            "ONE PAGE - NO PHOTOS")
    kf = font(SANS_B, 10.5)
    draw.text(((PAGE_W - width(draw, kick, kf)) / 2, 5), kick, font=kf,
              fill=CREAM)

    # Masthead
    draw.text((EDGE, 30), "THE WORLD IN ONE DAY", font=font(SERIF_B, 45),
              fill=INK)
    date_f = font(SERIF_B, 24)
    for line, dy in (("Saturday", 32), ("21 November 2026", 60)):
        draw.text((PAGE_W - EDGE - width(draw, line, date_f), dy), line,
                  font=date_f, fill=RED_DEEP)
    deck = ("Fifty-four verified stories from nine regions - every one of "
            "them Saturday's, every one dated against its source.")
    draw.text((EDGE, 92), deck, font=font(SERIF_I, 14), fill=(70, 62, 50))
    draw.line([EDGE, 114, PAGE_W - EDGE, 114], fill=INK, width=2)

    # Big numbers
    cell = SPAN / 6
    num_f = font(SERIF_B, 27)
    cap_f = font(SANS_R, 8)
    for i, (big, cap) in enumerate(BIG_NUMBERS):
        cx = EDGE + i * cell
        draw.text((cx, 122), big, font=num_f, fill=RED)
        para(draw, (cx, 156), cap, cap_f, SOFT, cell - 12, 10,
             max_lines=2)
    draw.line([EDGE, 180, PAGE_W - EDGE, 180], fill=(196, 186, 164),
              width=1)

    # Region chips
    chip_f = font(SANS_B, 9.5)
    cx = EDGE
    for chip in REGION_CHIPS:
        cw = width(draw, chip, chip_f) + 16
        draw.rounded_rectangle([cx, 188, cx + cw, 210], radius=9,
                               outline=NAVY, width=1)
        draw.text((cx + 8, 194), chip, font=chip_f, fill=NAVY)
        cx += cw + 7

    # Leads
    lead_w = (SPAN - 28) // 3
    for i, lead in enumerate(LEADS):
        draw_lead(draw, lead, i + 1, EDGE + i * (lead_w + 14), 218, lead_w)

    # Cards, row A (six) and row B (five)
    card_w_a = (SPAN - 50) // 6
    for i, card in enumerate(CARDS_A):
        draw_card(draw, card, 4 + i, EDGE + i * (card_w_a + 10), 430,
                  card_w_a)
    card_w_b = (SPAN - 40) // 5
    for i, card in enumerate(CARDS_B):
        draw_card(draw, card, 10 + i, EDGE + i * (card_w_b + 10), 542,
                  card_w_b)

    # Map
    draw_map(draw, EDGE, 654, SPAN, 76)

    # Briefs
    draw.line([EDGE, 740, PAGE_W - EDGE, 740], fill=RED, width=2)
    draw.text((EDGE, 746), "THE DAY IN BRIEF - STORIES 15-54",
              font=font(SANS_B, 11), fill=RED_DEEP)
    brief_f = font(SANS_R, 8.6)
    brief_b = font(SANS_B, 8.6)
    col_w = (SPAN - 28) // 3
    per_col = [14, 13, 13]
    idx = 0
    for col, count in enumerate(per_col):
        bx = EDGE + col * (col_w + 14)
        for row in range(count):
            text = BRIEFS[idx]
            num = 15 + idx
            by = 768 + row * 14.5
            head = "%d " % num
            draw.text((bx, by), head, font=brief_b, fill=RED)
            draw.text((bx + width(draw, head, brief_b), by), text,
                      font=brief_f, fill=INK)
            idx += 1

    # Method strip
    draw.rectangle([EDGE, 978, PAGE_W - EDGE, 1002], fill=PAPER_DIM)
    method = ("HOW THIS PAGE WAS CHECKED - every story was dated against "
              "its own source before it earned its place here; anything "
              "first reported before Saturday 21 November was left out, "
              "however big it was.")
    para(draw, (EDGE + 8, 984), method, font(SANS_R, 8.5), (70, 62, 50),
         SPAN - 16, 10.5, max_lines=1)
    colophon = ("Every story on this page happened, or was first reported, "
                "on Saturday 21 November 2026. - Sources are named beside "
                "each story - All artwork drawn for this page")
    draw.text((EDGE, 1008), colophon, font=font(SERIF_I, 8.5), fill=SOFT)
    return img


if __name__ == "__main__":
    build_page().save("entry.png")
    print("wrote entry.png")
