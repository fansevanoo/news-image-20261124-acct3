#!/usr/bin/env python3
"""news-image-20261124 acct3 (fansevanoo) — REVISI: 6 hero kecil digedein,
halaman padat sampai bawah, tidak ada gambar keluar border.

Semua ilustrasi digambar di layer RGBA terpisah seukuran kotak panelnya lalu
ditempel (paste) — paste terpotong otomatis di batas layer, jadi tidak ada
bentuk/garis/teks yang bisa keluar dari panel atau margin halaman.
Layout dihitung dengan cursor dari atas ke bawah; footer berakhir di y=1012
(margin bawah 12px), tanpa pita kosong di bawahnya.
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
M = 14                      # margin halaman
CW = W - 2 * M              # 996 lebar konten

CREAM = (244, 234, 211)
PAPER = (253, 248, 236)
INK = (26, 26, 26)
NAVY = (30, 58, 95)
RED = (169, 50, 38)
BRICK = (176, 58, 46)
GOLD = (201, 162, 39)
SKY = (178, 214, 235)
SEA = (38, 84, 130)
GREY = (90, 90, 90)
LIGHT = (230, 222, 200)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, path, sizes, width):
    """Font terbesar dari `sizes` yang muat satu baris dalam `width`."""
    for s in sizes:
        f = font(path, s)
        if f.getlength(text) <= width:
            return f
    return font(path, sizes[-1])


def text(draw, xy, s, fnt, fill=INK, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


# ---------------------------------------------------------------- data
# (judul, ringkasan, region, tag, sumber) — semua dari file stories.
LARGE = [
    ("Three tankers hit mines in Hormuz, IRGC claims",
     "IRGC claimed three tankers caught fire on naval mines under US escort; claim unverified.",
     "MIDEAST", "REPORTED", "Trends MENA / TBS News"),
    ("Russian jets trigger air-raid alert on Ulleung",
     "Russian jets entered Seoul's defence zone; residents sheltered at 7:52 a.m. F-15Ks scrambled.",
     "ASIA-PACIFIC", "CONFIRMED", "Reuters / Korea JoongAng Daily"),
    ("Sanofi to buy Insmed in $41 billion deal",
     "Sanofi will acquire US biotech Insmed for $41 billion in cash, its biggest pharma bet in years.",
     "EUROPE", "CONFIRMED", "Reuters"),
]
# 6 hero kecil: judul + ringkasan SATU BARIS, lengkap, tanpa terpotong.
SMALL = [
    ("US blacklists Megaspeed, Alibaba unit",
     "US firms barred from shipping goods.",
     "N. AMERICA", "CONFIRMED", "Reuters / Spyglass", "chip"),
    ("Central European leaders reject new EU budget",
     "Visegrad + Austria reject \u20ac1.582tn plan.",
     "EUROPE", "REPORTED", "Reuters", "eu"),
    ("Russia warns Estonia its actions risk 'open war'",
     "Moscow summons Tallinn's envoy.",
     "EUROPE", "REPORTED", "Reuters", "warn"),
    ("Iran courts demand $290 billion from US",
     "Tehran: US must pay $290bn.",
     "MIDEAST", "REPORTED", "AFP", "gavel"),
    ("Israeli strikes in Gaza kill 3, incl. UNRWA worker",
     "Three killed, incl. UNRWA worker.",
     "MIDEAST", "REPORTED", "Al Jazeera", "blast"),
    ("5.6 quake hits Nepal near Tibet",
     "Felt across Nepal and northern India.",
     "ASIA-PACIFIC", "CONFIRMED", "Reuters", "quake"),
]
NUMBERS = [
    ("$41bn", "Sanofi buys Insmed"),
    ("$290bn", "Iran courts demand from US"),
    ("5.6", "Nepal quake magnitude"),
    ("6 killed", "Hanoi explosion"),
    ("23", "injured in Villavicencio blast"),
    ("10m tons", "wheat at risk, WFP warns"),
    ("5%", "max tech fine, Australia"),
]
ALSO = [
    (5, "HLD Clariane takeover bid", "Reuters"),
    (8, "EU probes Coca-Cola bottler", "T.Briefings"),
    (9, "EU auditors fault oversight", "ECA"),
    (12, "Houthis: Saudi airstrike kills 17", "AFP"),
    (13, "Somalia-Uganda anti-Shabaab", "Shabelle"),
    (14, "WFP: 10m tons wheat at risk", "WFP"),
    (15, "AU maternal health roadmap", "TNA"),
    (16, "1 in 6 pregnancies in Africa to teens", "CDC"),
    (17, "Fighting traps Ebola teams in Ituri", "WHO"),
    (18, "Qatar condemns Khartoum attacks", "MFA"),
    (19, "Hanoi blast kills 6, injures 10", "Reuters"),
    (21, "Japan speeds ICC funding", "Reuters"),
    (22, "Australia fines tech firms 5%", "Reuters"),
    (23, "Hasina plans return home", "Reuters"),
    (24, "China names Shenzhou-24 crew", "Reuters"),
    (25, "Manila court orders Ang arrest", "PNA"),
    (26, "Japan cuts spending view", "Reuters"),
    (27, "Villavicencio car bomb", "El Tiempo"),
    (28, "Mexico to try 'El Chapo Isidro'", "Reuters"),
    (29, "WHO chief visits Cuba", "Al Jazeera"),
    (30, "Man rescued after 11 Amazon days", "AP"),
    (31, "Caravan crosses into Mexico", "Al Jazeera"),
]
# (nomor, lon, lat, region) — dari file stories.
DOTS = [
    (1, 56.3, 26.6, "ME"), (2, 130.9, 37.5, "AP"), (3, 2.35, 48.86, "EU"),
    (4, -77.0, 38.9, "NA"), (5, 2.35, 48.86, "EU"), (6, 17.1, 48.1, "EU"),
    (7, 24.7, 59.4, "EU"), (8, 4.4, 50.8, "EU"), (9, 6.1, 49.6, "EU"),
    (10, 51.4, 35.7, "ME"), (11, 34.5, 31.5, "ME"), (12, 42.9, 14.8, "ME"),
    (13, 32.5, 0.0, "AF"), (14, 12.5, 41.9, "AF"), (15, 38.7, 9.0, "AF"),
    (16, 38.7, 9.0, "AF"), (17, 30.2, 1.6, "AF"), (18, 32.5, 15.6, "AF"),
    (19, 105.9, 21.0, "AP"), (20, 87.9, 27.9, "AP"), (21, 139.7, 35.7, "AP"),
    (22, 149.1, -35.3, "AP"), (23, 90.4, 23.8, "AP"), (24, 100.3, 40.9, "AP"),
    (25, 121.0, 14.6, "AP"), (26, 139.7, 35.7, "AP"), (27, -73.6, 4.1, "LA"),
    (28, -99.1, 19.4, "LA"), (29, -82.4, 23.1, "LA"), (30, -60.0, -3.1, "LA"),
    (31, -92.3, 14.9, "LA"),
]
REGION_COLOR = {"NA": (179, 64, 47), "EU": (32, 80, 126), "ME": (181, 106, 31),
                "AF": (46, 125, 70), "AP": (106, 74, 158), "LA": (14, 125, 116)}
REGION_COUNT = [("N. AMERICA", 1, "NA"), ("EUROPE", 6, "EU"), ("MIDEAST", 4, "ME"),
                ("AFRICA", 6, "AF"), ("ASIA-PACIFIC", 9, "AP"), ("LATIN AM.", 5, "LA")]

CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
           (-80, 73), (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 35),
           (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-95, 19), (-97, 16),
           (-92, 15), (-86, 13), (-83, 9), (-79, 9), (-77, 7), (-80, 8),
           (-85, 11), (-90, 14), (-97, 16), (-105, 20), (-110, 24), (-114, 29),
           (-120, 34), (-125, 40), (-124, 48), (-130, 55), (-140, 60),
           (-155, 58), (-165, 60)],
    "SA": [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
           (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
           (-70, -54), (-66, -55), (-68, -50), (-65, -45), (-62, -40),
           (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-35, -9),
           (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6),
           (-62, 9), (-68, 11), (-72, 12), (-76, 10)],
    "AF": [(-17, 15), (-16, 20), (-10, 30), (-5, 35), (0, 36), (10, 37),
           (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (35, 23),
           (37, 18), (39, 15), (41, 11), (43, 11), (48, 11), (51, 12),
           (44, 5), (41, -2), (40, -10), (36, -18), (33, -26), (28, -33),
           (20, -35), (17, -32), (14, -22), (12, -17), (13, -10), (12, -5),
           (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 12)],
    "EU": [(-10, 36), (-9, 43), (-2, 44), (0, 46), (-4, 48), (-1, 50),
           (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62),
           (10, 64), (12, 66), (18, 69), (25, 71), (30, 70), (35, 68),
           (40, 68), (45, 68), (50, 69), (55, 68), (60, 69), (68, 73),
           (75, 73), (80, 73), (90, 75), (100, 77), (110, 74), (120, 73),
           (130, 72), (140, 72), (150, 70), (158, 69), (162, 66), (170, 66),
           (178, 65), (178, 62), (170, 60), (162, 60), (158, 53), (150, 59),
           (142, 55), (140, 50), (135, 44), (130, 42), (127, 40), (126, 38),
           (122, 38), (120, 32), (121, 28), (118, 25), (110, 21), (108, 18),
           (105, 10), (103, 8), (100, 8), (98, 12), (95, 16), (92, 21),
           (90, 22), (86, 20), (82, 17), (80, 13), (77, 8), (75, 12),
           (72, 20), (68, 23), (66, 25), (61, 25), (58, 26), (56, 27),
           (52, 26), (50, 29), (48, 30), (44, 29), (40, 32), (36, 36),
           (33, 36), (30, 36), (27, 37), (26, 38), (23, 36), (22, 37),
           (19, 40), (16, 38), (12, 44), (8, 44), (3, 43), (0, 40),
           (-2, 37), (-6, 36), (-9, 37)],
    "AU": [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
           (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
           (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
           (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
           (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    "GL": [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76),
           (-35, 77), (-45, 76), (-55, 74), (-58, 70), (-55, 66), (-50, 62)],
}


# ---------------------------------------------------------------- art
def layer(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def starburst(d, cx, cy, r1, r2, n, fill):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = 3.14159 * i / n
        pts.append((cx + r * 0.0 + r * __import__("math").cos(a),
                    cy + r * __import__("math").sin(a)))
    d.polygon(pts, fill=fill)


def art_hormuz(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h * 0.55], fill=SKY + (255,))
    d.ellipse([w - 52, 8, w - 16, 44], fill=(250, 214, 90, 255))
    d.rectangle([0, h * 0.55, w, h], fill=SEA + (255,))
    d.rectangle([0, h * 0.55, w, h * 0.55 + 4], fill=(255, 255, 255, 255))
    # tanker 1 (kiri, berlapis: lambung + garis merah + cerobong)
    d.rectangle([14, h * 0.62, 150, h * 0.80], fill=(30, 30, 34, 255))
    d.rectangle([14, h * 0.62, 150, h * 0.66], fill=RED + (255,))
    d.rectangle([30, h * 0.50, 48, h * 0.62], fill=(30, 30, 34, 255))
    d.rectangle([96, h * 0.54, 118, h * 0.62], fill=(70, 70, 76, 255))
    # tanker 2 (kanan)
    d.rectangle([185, h * 0.68, 305, h * 0.84], fill=(44, 44, 50, 255))
    d.rectangle([185, h * 0.68, 305, h * 0.72], fill=RED + (255,))
    d.rectangle([205, h * 0.57, 222, h * 0.68], fill=(44, 44, 50, 255))
    # ranjau bergerigi
    for cx, cy in ((168, h * 0.86), (262, h * 0.90), (60, h * 0.90)):
        starburst(d, cx, cy, 12, 5, 8, (15, 15, 15, 255))
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(15, 15, 15, 255))
    # ledakan berlapis
    starburst(d, 168, h * 0.42, 26, 12, 10, (255, 140, 0, 255))
    starburst(d, 168, h * 0.42, 15, 7, 10, (255, 220, 60, 255))
    starburst(d, 285, h * 0.36, 20, 9, 10, (255, 140, 0, 255))
    starburst(d, 285, h * 0.36, 11, 5, 10, (255, 220, 60, 255))
    return img


def art_ulleung(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h * 0.62], fill=SKY + (255,))
    d.ellipse([w - 58, 10, w - 20, 48], fill=(250, 214, 90, 255))
    d.rectangle([0, h * 0.62, w, h], fill=SEA + (255,))
    # pulau bergaris pantai melengkung
    d.polygon([(0, h), (0, h * 0.78), (40, h * 0.58), (110, h * 0.48),
               (180, h * 0.55), (230, h * 0.72), (250, h), ], fill=(74, 140, 74, 255))
    d.polygon([(40, h * 0.58), (110, h * 0.48), (180, h * 0.55),
               (150, h * 0.62), (80, h * 0.66)], fill=(110, 175, 110, 255))
    # mercusuar bergaris merah-putih
    d.rectangle([96, h * 0.30, 112, h * 0.58], fill=(255, 255, 255, 255))
    d.rectangle([96, h * 0.36, 112, h * 0.42], fill=RED + (255,))
    d.rectangle([96, h * 0.48, 112, h * 0.54], fill=RED + (255,))
    d.rectangle([92, h * 0.26, 116, h * 0.31], fill=(30, 30, 30, 255))
    # jet + jejak asap
    for jx, jy in ((210, 26), (248, 48)):
        d.line([(jx - 46, jy + 10), (jx - 6, jy + 2)], fill=(255, 255, 255, 220), width=3)
        d.polygon([(jx, jy), (jx - 26, jy - 5), (jx - 20, jy + 2),
                   (jx - 26, jy + 8)], fill=(25, 25, 28, 255))
    # segitiga peringatan besar
    tx, ty = w - 92, h - 78
    d.polygon([(tx, ty + 62), (tx + 34, ty), (tx + 68, ty + 62)],
              fill=(255, 200, 0, 255), outline=(20, 20, 20, 255), width=3)
    d.rectangle([tx + 31, ty + 20, tx + 37, ty + 44], fill=(20, 20, 20, 255))
    d.ellipse([tx + 30, ty + 48, tx + 38, ty + 56], fill=(20, 20, 20, 255))
    return img


def art_sanofi(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h], fill=(232, 240, 246, 255))
    # kapsul raksasa ber-highlight, diagonal
    d.ellipse([20, 12, w - 20, 78], fill=RED + (255,))
    d.ellipse([20, 12, w // 2 + 10, 78], fill=(255, 255, 255, 255))
    d.ellipse([20, 12, w - 20, 78], outline=(120, 20, 10, 255), width=3)
    d.ellipse([48, 26, 190, 46], fill=(255, 255, 255, 180))
    # banner $41 BILLION di bawah kapsul (di dalam layer)
    d.rectangle([0, h - 34, w, h], fill=NAVY + (255,))
    f = font(SANS_B, 22)
    text(d, (w // 2, h - 17), "$41 BILLION", f, fill=(255, 255, 255), anchor="mm")
    return img


def art_chip(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h], fill=(24, 24, 30, 255))
    # chip emas + pin
    cx, cy = w // 2 - 40, h // 2
    for i in range(5):
        x = cx - 34 + i * 17
        d.rectangle([x, cy - 46, x + 6, cy - 32], fill=(212, 175, 55, 255))
        d.rectangle([x, cy + 32, x + 6, cy + 46], fill=(212, 175, 55, 255))
    d.rectangle([cx - 40, cy - 32, cx + 40, cy + 32], fill=(30, 30, 36, 255),
                outline=(212, 175, 55, 255), width=3)
    f = font(SANS_B, 26)
    text(d, (cx, cy), "AI", f, fill=(212, 175, 55), anchor="mm")
    # cincin larangan di pojok kanan atas (tidak menutupi "AI")
    rx, ry, rr = w - 34, 30, 24
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], outline=RED + (255,), width=6)
    d.line([(rx - 17, ry + 17), (rx + 17, ry - 17)], fill=RED + (255,), width=6)
    return img


def art_eu(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h], fill=(32, 80, 126, 255))
    cx, cy = w // 2, h // 2
    for k in range(12):
        a = 3.14159 * 2 * k / 12 - 3.14159 / 2
        sx, sy = cx + 34 * __import__("math").cos(a), cy + 34 * __import__("math").sin(a)
        starburst(d, sx, sy, 7, 3, 5, (255, 210, 0, 255))
    # X merah besar
    d.line([(26, 10), (w - 26, h - 10)], fill=RED + (255,), width=10)
    d.line([(w - 26, 10), (26, h - 10)], fill=RED + (255,), width=10)
    return img


def art_warn(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h], fill=(245, 240, 220, 255))
    # garis hazard di bawah
    for i in range(9):
        x0 = i * 40
        d.polygon([(x0, h), (x0 + 20, h), (x0 + 40, h - 22), (x0 + 20, h - 22)],
                  fill=(20, 20, 20, 255))
    cx, cy = w // 2, h // 2 - 6
    d.polygon([(cx, cy - 34), (cx + 38, cy + 26), (cx - 38, cy + 26)],
              fill=(255, 200, 0, 255), outline=(20, 20, 20, 255), width=3)
    d.rectangle([cx - 3, cy - 18, cx + 3, cy + 6], fill=(20, 20, 20, 255))
    d.ellipse([cx - 4, cy + 12, cx + 4, cy + 20], fill=(20, 20, 20, 255))
    return img


def art_gavel(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h], fill=(238, 230, 210, 255))
    # palu pengadilan
    d.rectangle([w // 2 - 52, h // 2 - 26, w // 2 + 8, h // 2 - 2],
                fill=(120, 72, 32, 255))
    d.rectangle([w // 2 - 58, h // 2 - 30, w // 2 + 14, h // 2 - 22],
                fill=(90, 52, 22, 255))
    d.rectangle([w // 2 - 6, h // 2 - 22, w // 2 + 6, h // 2 + 34],
                fill=(150, 100, 50, 255))
    d.ellipse([w // 2 - 34, h // 2 + 30, w // 2 + 34, h // 2 + 42],
              fill=(120, 72, 32, 255))
    # segel $
    sx, sy = w - 52, h - 40
    d.ellipse([sx - 24, sy - 24, sx + 24, sy + 24], fill=NAVY + (255,))
    d.ellipse([sx - 24, sy - 24, sx + 24, sy + 24], outline=(255, 255, 255, 255), width=2)
    f = font(SANS_B, 26)
    text(d, (sx, sy), "$", f, fill=(255, 255, 255), anchor="mm")
    return img


def art_blast(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h], fill=(22, 22, 26, 255))
    cx, cy = w // 2, h // 2
    starburst(d, cx, cy, 40, 18, 12, (255, 120, 0, 255))
    starburst(d, cx, cy, 26, 12, 12, (255, 200, 40, 255))
    starburst(d, cx, cy, 13, 6, 12, (255, 240, 150, 255))
    return img


def art_quake(w, h):
    img, d = layer(w, h)
    d.rectangle([0, 0, w, h * 0.55], fill=SKY + (255,))
    d.ellipse([w - 56, 8, w - 22, 42], fill=(250, 214, 90, 255))
    d.polygon([(0, h), (0, h * 0.72), (70, h * 0.42), (140, h * 0.60),
               (210, h * 0.38), (280, h * 0.66), (w, h * 0.80), (w, h)],
              fill=(122, 84, 52, 255))
    d.polygon([(70, h * 0.42), (140, h * 0.60), (110, h * 0.52)],
              fill=(245, 245, 245, 255))
    # retakan merah
    d.line([(150, h * 0.44), (138, h * 0.58), (158, h * 0.68), (142, h * 0.82)],
           fill=RED + (255,), width=4)
    d.line([(210, h * 0.38), (222, h * 0.55), (206, h * 0.66)],
           fill=RED + (255,), width=3)
    # badge 5.6
    bx, by = w - 40, 30
    d.ellipse([bx - 24, by - 24, bx + 24, by + 24], fill=RED + (255,))
    d.ellipse([bx - 24, by - 24, bx + 24, by + 24], outline=(255, 255, 255, 255), width=2)
    f = font(SANS_B, 15)
    text(d, (bx, by), "5.6", f, fill=(255, 255, 255), anchor="mm")
    return img


ART = {"hormuz": art_hormuz, "ulleung": art_ulleung, "sanofi": art_sanofi,
       "chip": art_chip, "eu": art_eu, "warn": art_warn, "gavel": art_gavel,
       "blast": art_blast, "quake": art_quake}


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    x0, x1 = M, W - M

    # ---- masthead
    y = 8
    f = font(SERIF_B, 58)
    text(d, (W // 2, y), "THE WORLD IN ONE DAY", f, anchor="ma")
    y = 66
    f = font(SERIF_B, 27)
    text(d, (W // 2, y), "TUESDAY, 24 NOVEMBER 2026", f, fill=RED, anchor="ma")
    f = font(SANS, 10)
    text(d, (x1, y + 8), "31 stories \u00b7 6 regions \u00b7 Research cutoff 08:30 UTC",
         f, fill=GREY, anchor="ra")
    # garis ganda
    y = 98
    d.line([(x0, y), (x1, y)], fill=INK, width=2)
    d.line([(x0, y + 4), (x1, y + 4)], fill=INK, width=1)

    # ---- strip UTC (label penanda di BAWAH garis agar tidak menabrak angka jam)
    y = 108
    d.rectangle([x0, y, x1, y + 38], fill=NAVY)
    f = font(SANS_B, 12)
    text(d, (x0 + 8, y + 19), "THE DAY IN UTC", f, fill=(255, 255, 255), anchor="lm")
    tx0, tx1 = 210, x1 - 8
    d.line([(tx0, y + 18), (tx1, y + 18)], fill=(150, 170, 200), width=1)
    for hh in (0, 6, 12, 18, 24):
        xx = tx0 + (tx1 - tx0) * hh / 24
        d.line([(xx, y + 14), (xx, y + 22)], fill=(150, 170, 200), width=1)
        f = font(SANS, 8)
        text(d, (xx, y + 4), "%02d" % hh, f, fill=(190, 205, 225), anchor="ma")
    for frac, label in ((1 / 24, "01:00 UTC  HANOI BLAST"),
                        (7.87 / 24, "07:52 KST  ULLEUNG ALERT")):
        xx = tx0 + (tx1 - tx0) * frac
        d.ellipse([xx - 4, y + 14, xx + 4, y + 22], fill=GOLD)
        f = font(SANS_B, 9)
        text(d, (xx, y + 27), label, f, fill=GOLD, anchor="ma")

    # ---- strip angka
    y = 148
    bw = (CW - 6 * 6) // 7
    for i, (val, lab) in enumerate(NUMBERS):
        bx = x0 + i * (bw + 6)
        d.rectangle([bx, y, bx + bw, y + 48], fill=PAPER, outline=RED, width=1)
        d.line([(bx, y), (bx + bw, y)], fill=RED, width=3)
        f = fit_font(val, SANS_B, [20, 18, 16], bw - 8)
        text(d, (bx + bw // 2, y + 14), val, f, fill=RED, anchor="ma")
        f = fit_font(lab, SANS, [10, 9], bw - 8)
        text(d, (bx + bw // 2, y + 36), lab, f, fill=GREY, anchor="ma")

    # ---- judul seksi
    y = 202
    f = font(SANS_B, 14)
    text(d, (x0, y), "THE NINE STORIES THAT LED THE DAY", f, anchor="la")
    d.line([(x0, y + 18), (x1, y + 18)], fill=INK, width=1)

    # ---- 3 hero besar
    colw = (CW - 2 * 6) // 3
    y = 226
    HERO_H = 214
    ART_H = 112
    for i, (title, summ, region, tag, src) in enumerate(LARGE):
        px = x0 + i * (colw + 6)
        d.rectangle([px, y, px + colw, y + HERO_H], fill=PAPER, outline=INK, width=1)
        art = ART[("hormuz", "ulleung", "sanofi")[i]](colw, ART_H)
        img.paste(art, (px, y), art)
        d.line([(px, y + ART_H), (px + colw, y + ART_H)], fill=INK, width=1)
        ty = y + ART_H + 4
        f = font(SANS_B, 10)
        text(d, (px + 8, ty), region, f, fill=REGION_COLOR[
            {"MIDEAST": "ME", "ASIA-PACIFIC": "AP", "EUROPE": "EU"}[region]], anchor="la")
        ty += 13
        f = font(SERIF_B, 18)
        for ln in wrap(title, f, colw - 16)[:2]:
            text(d, (px + 8, ty), ln, f, anchor="la")
            ty += 22
        f = font(SANS, 10)
        for ln in wrap(summ, f, colw - 16)[:2]:
            text(d, (px + 8, ty), ln, f, anchor="la")
            ty += 13
        f = font(SANS_B, 9)
        tcol = (34, 139, 34) if tag == "CONFIRMED" else (176, 106, 20)
        text(d, (px + 8, ty), tag, f, fill=tcol, anchor="la")
        fw = f.getlength(tag)
        f2 = font(SANS, 9)
        text(d, (px + 12 + fw, ty), src, f2, fill=GREY, anchor="la")
        if i == 0:
            f = font(SANS_B, 10)
            rw = f.getlength("TOP STORY") + 14
            d.rectangle([px + colw - rw, y, px + colw, y + 20], fill=RED)
            text(d, (px + colw - rw // 2, y + 10), "TOP STORY", f,
                 fill=(255, 255, 255), anchor="mm")

    # ---- 6 hero kecil (DIGEDEIN: panel 146, art 84) — 2 baris x 3 kolom
    SMALL_H = 146
    SMALL_ART_H = 84
    for row in range(2):
        y = 446 + row * (SMALL_H + 6)
        for col in range(3):
            idx = row * 3 + col
            title, summ, region, tag, src, artkey = SMALL[idx]
            num = (4, 6, 7, 10, 11, 20)[idx]
            px = x0 + col * (colw + 6)
            d.rectangle([px, y, px + colw, y + SMALL_H], fill=PAPER,
                        outline=INK, width=1)
            art = ART[artkey](colw, SMALL_ART_H)
            img.paste(art, (px, y), art)
            d.line([(px, y + SMALL_ART_H), (px + colw, y + SMALL_ART_H)],
                   fill=INK, width=1)
            ty = y + SMALL_ART_H + 4
            f = font(SANS_B, 9)
            text(d, (px + 8, ty), "%d \u00b7 %s" % (num, region), f,
                 fill=REGION_COLOR[{"N. AMERICA": "NA", "EUROPE": "EU",
                                    "MIDEAST": "ME", "ASIA-PACIFIC": "AP"}[region]],
                 anchor="la")
            ty += 13
            f = fit_font(title, SANS_B, [13, 12, 11, 10], colw - 16)
            text(d, (px + 8, ty), title, f, anchor="la")
            ty += 15
            f = fit_font(summ, SANS, [11, 10], colw - 16)
            text(d, (px + 8, ty), summ, f, fill=GREY, anchor="la")
            ty += 14
            f = font(SANS_B, 8)
            tcol = (34, 139, 34) if tag == "CONFIRMED" else (176, 106, 20)
            text(d, (px + 8, ty), tag, f, fill=tcol, anchor="la")
            fw = f.getlength(tag)
            f2 = font(SANS, 8)
            text(d, (px + 12 + fw, ty), src, f2, fill=GREY, anchor="la")

    # ---- peta + ALSO
    y = 750
    SEC_H = 196
    map_w = 470
    d.rectangle([x0, y, x0 + map_w, y + SEC_H], fill=PAPER, outline=INK, width=1)
    f = font(SANS_B, 12)
    text(d, (x0 + 8, y + 4), "WHERE IT HAPPENED", f, anchor="la")
    # peta di layer sendiri (terpotong rapi di kotaknya)
    mw, mh = map_w - 16, 148
    lay, ld = layer(mw, mh)
    ld.rectangle([0, 0, mw, mh], fill=(214, 232, 240, 255))
    for gx in range(0, mw + 1, 30):
        ld.line([(gx, 0), (gx, mh)], fill=(255, 255, 255, 120), width=1)
    for gy in range(0, mh + 1, 30):
        ld.line([(0, gy), (mw, gy)], fill=(255, 255, 255, 120), width=1)

    def proj(lon, lat):
        return ((lon + 180) / 360.0 * mw, (78 - lat) / 136.0 * mh)

    for pts in CONTINENTS.values():
        ld.polygon([proj(lon, lat) for lon, lat in pts],
                   fill=(222, 200, 150, 255), outline=(150, 125, 80, 255))
    placed = []
    for num, lon, lat, reg in DOTS:
        tx, ty = proj(lon, lat)
        tx = min(max(tx, 9), mw - 9)
        ty = min(max(ty, 9), mh - 9)
        dx, dy = tx, ty
        # geser bila bertumpuk (kota berbagi / klaster Eropa), garis leader ke titik asli
        for k in range(6):
            clash = any((dx - px) ** 2 + (dy - py) ** 2 < 15 ** 2
                        for px, py in placed)
            if not clash:
                break
            dx = min(max(tx + (12 if k % 2 == 0 else -12), 9), mw - 9)
            dy = min(max(ty + (-12 if k % 2 == 0 else 12), 9), mh - 9)
        if (dx, dy) != (tx, ty):
            ld.line([(tx, ty), (dx, dy)], fill=INK, width=1)
        placed.append((dx, dy))
        col = REGION_COLOR[reg]
        ld.ellipse([dx - 7, dy - 7, dx + 7, dy + 7], fill=col + (255,),
                   outline=(255, 255, 255, 255), width=2)
        f = font(SANS_B, 8)
        text(ld, (dx, dy), str(num), f, fill=(255, 255, 255), anchor="mm")
    img.paste(lay, (x0 + 8, y + 22), lay)
    # legenda REGION INDEX
    ly = y + SEC_H - 20
    f = font(SANS_B, 9)
    text(d, (x0 + 8, ly), "REGION INDEX", f, anchor="la")
    lx = x0 + 96
    f = font(SANS, 9)
    for _name, cnt, key in REGION_COUNT:
        col = REGION_COLOR[key]
        d.ellipse([lx, ly + 1, lx + 8, ly + 9], fill=col)
        s = "%s %d" % (key, cnt)
        text(d, (lx + 11, ly), s, f, anchor="la")
        lx += 11 + f.getlength(s) + 10
    # ALSO (kanan)
    ax = x0 + map_w + 6
    aw = x1 - ax
    d.rectangle([ax, y, x1, y + SEC_H], fill=PAPER, outline=INK, width=1)
    f = font(SANS_B, 12)
    text(d, (ax + 8, y + 4), "ALSO ON TUESDAY 24 NOVEMBER", f, anchor="la")
    d.line([(ax + 8, y + 20), (x1 - 8, y + 20)], fill=INK, width=1)
    colw2 = (aw - 16 - 8) // 2
    for i, (num, label, src) in enumerate(ALSO):
        c = i // 11
        r = i % 11
        ix = ax + 8 + c * (colw2 + 8)
        iy = y + 26 + r * 15
        s = "%d. %s \u2014 %s" % (num, label, src)
        f = fit_font(s, SANS, [10, 9], colw2)
        text(d, (ix, iy), s, f, anchor="la")

    # ---- DATE CHECK
    y = 952
    d.rectangle([x0, y, x1, y + 26], fill=PAPER, outline=RED, width=1)
    s = ("DATE CHECK \u2014 Left out, wrong date: Nvidia/Huang +31% (23 Nov) \u00b7 "
         "COP31 collapse (23 Nov) \u00b7 Merkury sinking (22\u201323 Nov) \u00b7 "
         "SoftBank\u2013Intel $2B (Aug 2025) \u00b7 CAS ruling (not yet decided)")
    f = fit_font(s, SANS, [11, 10, 9], CW - 16)
    text(d, (x0 + 8, y + 13), s, f, anchor="lm")

    # ---- footer
    y = 984
    d.line([(x0, y), (x1, y)], fill=INK, width=2)
    d.line([(x0, y + 4), (x1, y + 4)], fill=INK, width=1)
    f = font(SANS_B, 10)
    text(d, (W // 2, y + 12),
         "Every story above happened or was first reported on Tuesday 24 November 2026.",
         f, anchor="ma")
    f = font(SANS, 9)
    text(d, (W // 2, y + 23),
         "CONFIRMED = the event happened that day; REPORTED = first reported that day.  "
         "Sources: Reuters, AFP, Al Jazeera, El Tiempo, WFP, WHO, Africa CDC.",
         f, fill=GREY, anchor="ma")
    assert y + 28 == 1012, "footer harus berakhir di y=1012, dapat %d" % (y + 28)

    img.save(OUT, "PNG")
    data = open(OUT, "rb").read()
    print("OK entry.png", len(data), "bytes",
          "sha256", hashlib.sha256(data).hexdigest())
    return img


if __name__ == "__main__":
    build()
