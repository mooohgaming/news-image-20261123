#!/usr/bin/env python3
"""news-image-20261123: draw one newspaper page summing up the world news of
Monday 23 November 2026, as a deterministic 1024x1024 PNG.

Python 3.13 standard library only. No network, no clock, no randomness: the
same bytes come out of every run. The PNG is encoded by hand (zlib + struct),
text is drawn with a built-in 5x7 bitmap font, and every picture is drawn from
shapes (rectangles, circles, lines, polygons).

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
    python3 main.py                           # writes /output/entry.png
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (246, 241, 227)     # warm newsprint
NAVY = (20, 38, 74)         # masthead / ink
GOLD = (232, 193, 90)       # masthead accent
INK = (24, 24, 24)          # headline ink
BODY = (58, 58, 58)         # body ink
GREY = (120, 120, 112)      # source lines
WHITE = (255, 255, 255)
CARD = (255, 255, 255)

# ------------------------------------------------------------------- font ---
# 5x7 bitmap font, rows are 5-character strings of '0'/'1'.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "=": ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '"': ["01010", "01010", "01010", "00000", "00000", "00000", "00000"],
}


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap per glyph column)."""
    return len(text) * (5 * scale + scale) - scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------- canvas ---
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def circle_outline(self, cx, cy, r, color, t=1):
        for dy in range(-r - t, r + t + 1):
            for dx in range(-r - t, r + t + 1):
                d = (dx * dx + dy * dy) ** 0.5
                if r - t < d <= r:
                    self.set(cx + dx, cy + dy, color)

    def polygon(self, points, color):
        """Scanline fill (even-odd), works for convex and concave polygons."""
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 5 * scale + scale
        return cx

    def text_centred(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# -------------------------------------------------------------------- png ----
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- illustrations --
# Each scene draws inside a panel (px, py, pw, ph). All shapes are drawn
# from code; nothing is loaded from disk.

def burst(cv, cx, cy, r, color):
    """Starburst: 8 spikes from a centre disc."""
    for k in range(8):
        a = k * 3.14159265 / 4.0
        x2 = cx + int(r * 1.6 * (1 if k % 2 == 0 else 0.55) * _cos(a))
        y2 = cy + int(r * 1.6 * (1 if k % 2 == 0 else 0.55) * _sin(a))
        cv.line(cx, cy, x2, y2, color, 4)
    cv.circle(cx, cy, r // 2 + 2, color)
    cv.circle(cx, cy, r // 3, (241, 196, 15))


def _cos(a):
    # cos via a tiny Taylor-free table is overkill; use math-free series.
    return _trig(a, True)


def _sin(a):
    return _trig(a, False)


def _trig(a, is_cos):
    # 7-term Taylor series; a is in radians, |a| <= pi.
    x = a
    if is_cos:
        term, total, sign = 1.0, 1.0, -1.0
        for n in range(1, 5):
            term *= x * x / ((2 * n - 1) * (2 * n))
            total += sign * term
            sign = -sign
        return total
    term, total, sign = x, x, -1.0
    for n in range(1, 5):
        term *= x * x / ((2 * n) * (2 * n + 1))
        total += sign * term
        sign = -sign
    return total


def scene_cop31(cv, px, py, pw, ph):
    cv.fill_rect(px, py, pw, ph, (220, 239, 230))
    # sun, top right
    cv.circle(px + 408, py + 18, 13, (240, 196, 60))
    for k in range(8):
        a = k * 3.14159265 / 4.0
        cv.line(px + 408 + int(17 * _cos(a)), py + 18 + int(17 * _sin(a)),
                px + 408 + int(24 * _cos(a)), py + 18 + int(24 * _sin(a)),
                (240, 196, 60), 2)
    # globe, left
    gx, gy, gr = px + 62, py + 40, 28
    cv.circle(gx, gy, gr, (46, 139, 122))
    cv.circle_outline(gx, gy, gr, (255, 255, 255), 2)
    cv.line(gx - gr, gy, gx + gr, gy, (255, 255, 255), 2)
    cv.line(gx, gy - gr, gx, gy + gr, (255, 255, 255), 2)
    cv.line(gx - 20, gy - 22, gx - 6, gy - 6, (214, 48, 49), 3)
    cv.line(gx - 6, gy - 6, gx + 8, gy + 8, (214, 48, 49), 3)
    cv.line(gx + 8, gy + 8, gx + 20, gy + 24, (214, 48, 49), 3)
    # thermometer, middle
    tx = px + 168
    cv.fill_rect(tx, py + 12, 16, 42, (255, 255, 255))
    cv.rect(tx, py + 12, 16, 42, (120, 120, 120), 1)
    cv.fill_rect(tx + 3, py + 30, 10, 24, (214, 48, 49))
    cv.circle(tx + 8, py + 56, 11, (214, 48, 49))
    # factory silhouette, right
    fx = px + 250
    cv.fill_rect(fx, py + 38, 96, 30, (70, 80, 95))
    cv.fill_rect(fx + 78, py + 16, 12, 52, (70, 80, 95))
    cv.circle(fx + 84, py + 10, 7, (160, 160, 160))
    cv.circle(fx + 96, py + 6, 5, (160, 160, 160))
    cv.fill_rect(fx + 8, py + 46, 12, 10, (232, 193, 90))
    cv.fill_rect(fx + 28, py + 46, 12, 10, (232, 193, 90))
    cv.fill_rect(fx + 48, py + 46, 12, 10, (232, 193, 90))


def scene_democrats(cv, px, py, pw, ph):
    cv.fill_rect(px, py, pw, ph, (220, 230, 245))
    # Capitol dome, left: white dome with a dark outline, dark columns below
    dx = px + 118
    cv.circle(dx, py + 32, 30, (255, 255, 255))
    cv.circle_outline(dx, py + 32, 30, NAVY, 2)
    cv.fill_rect(dx - 30, py + 32, 60, 36, (220, 230, 245))
    for cx in range(dx - 60, dx + 61, 24):
        cv.fill_rect(cx, py + 32, 8, 20, NAVY)
    cv.fill_rect(dx - 72, py + 52, 144, 16, NAVY)
    cv.line(dx, py + 32, dx, py + 4, (120, 120, 120), 2)
    cv.fill_rect(dx, py + 4, 18, 10, (178, 34, 34))
    cv.fill_rect(dx, py + 4, 18, 3, (255, 255, 255))
    # the number, right
    cv.text(px + 252, py + 16, "258", 5, NAVY)
    cv.text(px + 252, py + 56, "SEATS", 2, (58, 58, 58))
    # stars
    for sx, sy in ((px + 30, py + 12), (px + 210, py + 12), (px + 420, py + 58)):
        cv.line(sx - 5, sy, sx + 5, sy, GOLD, 2)
        cv.line(sx, sy - 5, sx, sy + 5, GOLD, 2)


def scene_merkury(cv, px, py, pw, ph):
    cv.fill_rect(px, py, pw, ph, (214, 234, 248))
    # sea
    cv.fill_rect(px, py + 52, pw, ph - 52, (46, 134, 193))
    cv.line(px + 10, py + 58, px + 60, py + 58, (255, 255, 255), 2)
    cv.line(px + 240, py + 62, px + 300, py + 62, (255, 255, 255), 2)
    cv.line(px + 330, py + 58, px + 380, py + 58, (255, 255, 255), 2)
    # warship hull
    cv.polygon([(px + 60, py + 40), (px + 210, py + 40),
                (px + 196, py + 54), (px + 74, py + 54)], (93, 109, 126))
    cv.fill_rect(px + 96, py + 28, 62, 12, (93, 109, 126))
    cv.line(px + 127, py + 28, px + 127, py + 10, (93, 109, 126), 3)
    cv.fill_rect(px + 80, py + 44, 14, 6, (232, 193, 90))
    cv.fill_rect(px + 110, py + 44, 14, 6, (232, 193, 90))
    # explosion above the ship
    burst(cv, px + 150, py + 14, 8, (230, 126, 34))
    # sea drone, right
    dx, dy = px + 330, py + 30
    cv.fill_rect(dx - 14, dy - 4, 28, 8, (40, 40, 40))
    for ox, oy in ((-20, -10), (20, -10), (-20, 10), (20, 10)):
        cv.line(dx, dy, dx + ox, dy + oy, (40, 40, 40), 2)
        cv.circle(dx + ox, dy + oy, 4, (40, 40, 40))
    cv.line(dx - 14, dy + 14, dx - 40, dy + 20, (255, 255, 255), 2)


def scene_fire(cv, px, py, pw, ph):
    cv.fill_rect(px, py, pw, ph, (253, 235, 208))
    # smoke
    cv.circle(px + 258, py + 12, 9, (150, 150, 150))
    cv.circle(px + 276, py + 8, 7, (170, 170, 170))
    cv.circle(px + 240, py + 18, 6, (170, 170, 170))
    # factory
    cv.fill_rect(px + 48, py + 40, 170, 28, (97, 106, 107))
    cv.polygon([(px + 48, py + 40), (px + 83, py + 24), (px + 118, py + 40)],
               (97, 106, 107))
    cv.polygon([(px + 118, py + 40), (px + 153, py + 24), (px + 188, py + 40)],
               (97, 106, 107))
    cv.fill_rect(px + 228, py + 10, 14, 58, (97, 106, 107))
    # flames on the roof
    for fx in (70, 108, 146):
        cv.polygon([(px + fx, py + 38), (px + fx + 12, py + 10),
                    (px + fx + 24, py + 38)], (230, 126, 34))
        cv.polygon([(px + fx + 6, py + 38), (px + fx + 12, py + 22),
                    (px + fx + 18, py + 38)], (241, 196, 15))
    # windows
    for wx in (60, 92, 124, 156, 188):
        cv.fill_rect(px + wx, py + 48, 14, 12, (232, 193, 90))
    # ground
    cv.fill_rect(px, py + 68, pw, 6, (120, 100, 80))


def scene_football(cv, px, py, pw, ph):
    cv.fill_rect(px, py, pw, ph, (169, 223, 191))
    # pitch markings
    cv.rect(px + 16, py + 8, pw - 32, ph - 16, (255, 255, 255), 2)
    cv.line(px + pw // 2, py + 8, px + pw // 2, py + ph - 8, (255, 255, 255), 2)
    cv.circle_outline(px + pw // 2, py + ph // 2, 13, (255, 255, 255), 2)
    # goal, right
    cv.fill_rect(px + 396, py + 18, 4, 38, (255, 255, 255))
    cv.fill_rect(px + 396, py + 18, 28, 4, (255, 255, 255))
    cv.fill_rect(px + 420, py + 18, 4, 38, (255, 255, 255))
    for gx in range(400, 421, 7):
        cv.line(px + gx, py + 22, px + gx, py + 52, (255, 255, 255), 1)
    # ball, left
    bx, by = px + 92, py + 37
    cv.circle(bx, by, 13, (255, 255, 255))
    cv.circle(bx, by, 4, (24, 24, 24))
    cv.circle(bx - 8, by - 6, 2, (24, 24, 24))
    cv.circle(bx + 8, by - 6, 2, (24, 24, 24))
    cv.circle(bx, by + 9, 2, (24, 24, 24))
    # the score, centre
    cv.text(px + 252, py + 18, "4-0", 5, NAVY)


def scene_drone(cv, px, py, pw, ph):
    cv.fill_rect(px, py, pw, ph, (214, 219, 223))
    # sea
    cv.fill_rect(px, py + 56, pw, ph - 56, (36, 90, 140))
    cv.line(px + 20, py + 62, px + 70, py + 62, (255, 255, 255), 2)
    cv.line(px + 300, py + 66, px + 360, py + 66, (255, 255, 255), 2)
    # small ship on the sea
    cv.polygon([(px + 310, py + 48), (px + 400, py + 48),
                (px + 388, py + 58), (px + 322, py + 58)], (60, 60, 60))
    cv.line(px + 355, py + 48, px + 355, py + 34, (60, 60, 60), 2)
    # the drone, centre-left, hit by a burst
    dx, dy = px + 150, py + 26
    cv.fill_rect(dx - 18, dy - 5, 36, 10, (70, 70, 70))
    for ox, oy in ((-26, -12), (26, -12), (-26, 12), (26, 12)):
        cv.line(dx, dy, dx + ox, dy + oy, (70, 70, 70), 2)
        cv.circle(dx + ox, dy + oy, 5, (70, 70, 70))
    burst(cv, dx + 30, dy - 8, 7, (230, 126, 34))
    # falling trail
    cv.line(dx + 30, dy + 2, dx + 44, dy + 26, (214, 48, 49), 3)
    cv.line(dx + 44, dy + 26, dx + 36, dy + 18, (214, 48, 49), 3)


# ------------------------------------------------------------------ stories --
# Six stories of Monday 23 November 2026, each verified against a real report
# published that day. Headlines are short; bodies are two lines at most.
STORIES = [
    dict(kicker="CLIMATE", color=(46, 139, 122),
         headline="COP31 ENDS WITH NO DEAL",
         body=("Nearly 200 nations leave Antalya without a climate pact "
               "after talks collapse over fossil fuels."),
         source="SOURCE: CNN - 23 NOV 2026",
         scene=scene_cop31),
    dict(kicker="POLITICS", color=(20, 38, 74),
         headline="DEMOCRATS WIN 258 HOUSE SEATS",
         body=("AP calls a historic majority, the largest for either "
               "party since 1992."),
         source="SOURCE: ASSOCIATED PRESS - 23 NOV 2026",
         scene=scene_democrats),
    dict(kicker="WAR AT SEA", color=(93, 109, 126),
         headline="UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
         body=("Seven naval drones sink the corvette Merkury in Benghazi; "
               "a cargo ship and a helicopter are also hit."),
         source="SOURCE: REUTERS - 23 NOV 2026",
         scene=scene_merkury),
    dict(kicker="DISASTER", color=(214, 48, 49),
         headline="24 DEAD IN INDONESIA FACTORY FIRE",
         body=("A blaze at a candy factory in Banten leaves about 30 "
               "people unaccounted for."),
         source="SOURCE: XINHUA - 23 NOV 2026",
         scene=scene_fire),
    dict(kicker="SPORT", color=(39, 174, 96),
         headline="LIVERPOOL THRASH MAN UTD 4-0",
         body=("Pochettino's first match as United boss ends in a rout "
               "at Anfield; Yoro sent off after 8 minutes."),
         source="SOURCE: REUTERS - 23 NOV 2026",
         scene=scene_football),
    dict(kicker="MIDDLE EAST", color=(142, 68, 173),
         headline="IRAN SAYS IT DOWNED A US DRONE",
         body=("Tehran says it shot down a US MQ-9 Reaper over the "
               "Strait of Hormuz."),
         source="SOURCE: INSHORTS - 23 NOV 2026",
         scene=scene_drone),
]


# -------------------------------------------------------------------- page ---
def draw_card(cv, x, y, w, h, story):
    cv.fill_rect(x, y, w, h, CARD)
    cv.rect(x, y, w, h, NAVY, 2)
    # kicker strip
    cv.fill_rect(x + 2, y + 2, w - 4, 30, story["color"])
    cv.text(x + 14, y + 10, story["kicker"], 2, WHITE)
    # headline, up to two lines
    lines = wrap_text(story["headline"], 3, w - 28)[:2]
    for i, line in enumerate(lines):
        cv.text(x + 14, y + 42 + i * 26, line, 3, INK)
    # body, up to three lines
    lines = wrap_text(story["body"], 2, w - 28)[:3]
    for i, line in enumerate(lines):
        cv.text(x + 14, y + 102 + i * 18, line, 2, BODY)
    # illustration panel
    story["scene"](cv, x + 12, y + 162, w - 24, 74)
    # source line
    cv.text(x + 14, y + 244, story["source"], 1, GREY)


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(12, 12, W - 24, H - 24, NAVY, 4)
    # masthead
    cv.fill_rect(24, 24, W - 48, 124, NAVY)
    cv.text_centred(W // 2, 38, "THE WORLD IN ONE PAGE", 5, GOLD)
    cv.text_centred(W // 2, 86, "MONDAY 23 NOVEMBER 2026", 4, WHITE)
    cv.text_centred(W // 2, 124, "SIX STORIES THAT DEFINED THE DAY", 2, GOLD)
    # six cards: 2 columns x 3 rows
    cw, ch, gap = 476, 264, 14
    for i, story in enumerate(STORIES):
        x = 24 + (i % 2) * (cw + gap)
        y = 164 + (i // 2) * (ch + gap)
        draw_card(cv, x, y, cw, ch, story)
    # footer
    cv.text_centred(W // 2, 994, "THE WORLD IN ONE PAGE - MONDAY 23 NOVEMBER 2026",
                    1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, build())
    print(f"wrote {path} ({size} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
