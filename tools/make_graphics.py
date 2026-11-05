#!/usr/bin/env python3
"""Generates the simple placeholder graphics for Cozy Farm (pure Python, no PIL).

Usage: python3 make_graphics.py <mod-dir>
Writes <mod-dir>/graphics/icons/*.png (64x64) and <mod-dir>/graphics/entity/*.png.
"""
import math
import os
import struct
import sys
import zlib

SS = 4  # supersampling factor for anti-aliasing


class Canvas:
    def __init__(self, w, h, ss=SS):
        self.ss = ss
        self.w, self.h = w, h
        self.W, self.H = w * self.ss, h * self.ss
        self.px = [[0.0, 0.0, 0.0, 0.0] for _ in range(self.W * self.H)]

    def _blend(self, x, y, c):
        p = self.px[y * self.W + x]
        a = c[3]
        inv = 1 - a
        # premultiplied "over"
        p[0] = c[0] * a + p[0] * inv
        p[1] = c[1] * a + p[1] * inv
        p[2] = c[2] * a + p[2] * inv
        p[3] = a + p[3] * inv

    def fill(self, inside, bbox, color):
        """inside(x, y) in output-pixel coordinates (floats)."""
        c = rgba(color)
        x0, y0, x1, y1 = bbox
        X0 = max(0, int(math.floor(x0 * self.ss)))
        Y0 = max(0, int(math.floor(y0 * self.ss)))
        X1 = min(self.W, int(math.ceil(x1 * self.ss)) + 1)
        Y1 = min(self.H, int(math.ceil(y1 * self.ss)) + 1)
        for Y in range(Y0, Y1):
            fy = (Y + 0.5) / self.ss
            for X in range(X0, X1):
                if inside((X + 0.5) / self.ss, fy):
                    self._blend(X, Y, c)

    def ellipse(self, cx, cy, rx, ry, color, angle=0.0):
        ca, sa = math.cos(-angle), math.sin(-angle)
        r = max(rx, ry)

        def inside(x, y):
            dx, dy = x - cx, y - cy
            u = dx * ca - dy * sa
            v = dx * sa + dy * ca
            return (u / rx) ** 2 + (v / ry) ** 2 <= 1.0

        self.fill(inside, (cx - r, cy - r, cx + r, cy + r), color)

    def circle(self, cx, cy, r, color):
        self.ellipse(cx, cy, r, r, color)

    def poly(self, pts, color):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]

        def inside(x, y):
            n = len(pts)
            ins = False
            j = n - 1
            for i in range(n):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                    ins = not ins
                j = i
            return ins

        self.fill(inside, (min(xs), min(ys), max(xs), max(ys)), color)

    def rect(self, x0, y0, x1, y1, color):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color)

    def line(self, x0, y0, x1, y1, width, color):
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln * width / 2, dx / ln * width / 2
        self.poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], color)
        self.circle(x0, y0, width / 2, color)
        self.circle(x1, y1, width / 2, color)

    def save(self, path):
        rows = []
        for y in range(self.h):
            row = bytearray([0])
            for x in range(self.w):
                r = g = b = a = 0.0
                for sy in range(self.ss):
                    base = (y * self.ss + sy) * self.W + x * self.ss
                    for sx in range(self.ss):
                        p = self.px[base + sx]
                        r += p[0]; g += p[1]; b += p[2]; a += p[3]
                n = self.ss * self.ss
                r, g, b, a = r / n, g / n, b / n, a / n
                if a > 0:
                    r, g, b = r / a, g / a, b / a  # un-premultiply
                row += bytes([clamp(r), clamp(g), clamp(b), clamp(a)])
            rows.append(bytes(row))
        raw = b"".join(rows)

        def chunk(tag, data):
            c = struct.pack(">I", len(data)) + tag + data
            return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(raw, 9))
        png += chunk(b"IEND", b"")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(png)


def clamp(v):
    return max(0, min(255, int(round(v * 255))))


def rgba(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        vals = [int(c[i:i + 2], 16) / 255 for i in range(0, len(c), 2)]
        if len(vals) == 3:
            vals.append(1.0)
        return vals
    return list(c) if len(c) == 4 else list(c) + [1.0]


def shade(color, f):
    c = rgba(color)
    return [min(1, c[0] * f), min(1, c[1] * f), min(1, c[2] * f), c[3]]


OUT = "#2b1d12"  # outline colour

# ---------------------------------------------------------------- drawing pieces
# All "draw_*" functions draw into a 64x64 space; `o` offsets/scales for reuse in entity sprites.


def leaves(c, x, y, s, color="#4caf50", n=3, spread=0.5, length=14):
    for i in range(n):
        a = -math.pi / 2 + (i - (n - 1) / 2) * spread
        ex, ey = x + math.cos(a) * length * s, y + math.sin(a) * length * s
        mx, my = (x + ex) / 2, (y + ey) / 2
        c.ellipse(mx, my, length * s / 2 + 1, 4 * s + 1, OUT, a)
        c.ellipse(mx, my, length * s / 2, 4 * s, color, a)


def draw_carrot(c, x=32, y=36, s=1.0):
    leaves(c, x, y - 14 * s, s, "#5cb85c", 3, 0.45, 16)
    pts = [(x - 9 * s, y - 14 * s), (x + 9 * s, y - 14 * s), (x + 1.5 * s, y + 22 * s), (x - 1.5 * s, y + 22 * s)]
    c.poly([(px + (1 if px > x else -1) * 1.5, py + (-1.5 if py < y else 1.5)) for px, py in pts], OUT)
    c.poly(pts, "#f28a1e")
    for k in range(3):
        yy = y - 6 * s + k * 8 * s
        c.line(x - 5 * s + k * s, yy, x - 1 * s + k * s, yy + 1, 1.5 * s, "#c9650c")


def draw_potato(c, x=32, y=34, s=1.0):
    c.ellipse(x, y, 22 * s + 1.5, 16 * s + 1.5, OUT, 0.3)
    c.ellipse(x, y, 22 * s, 16 * s, "#c8a165", 0.3)
    c.ellipse(x - 4 * s, y - 5 * s, 12 * s, 6 * s, "#dcbb85", 0.3)
    for dx, dy in [(-9, 2), (6, -6), (10, 6), (-2, 9)]:
        c.circle(x + dx * s, y + dy * s, 1.6 * s, "#8a6a3a")


def draw_wheat(c, x=32, y=34, s=1.0):
    for off, ang in [(-8, -0.25), (0, 0), (8, 0.25)]:
        bx, by = x + off * s, y + 26 * s
        tx, ty = x + off * s + math.sin(ang) * 30 * s, y - 20 * s
        c.line(bx, by, tx, ty + 10 * s, 2.5 * s, "#b88a2a")
        for k in range(4):
            gy = ty + k * 6 * s
            gx = tx - (tx - bx) * (k * 6 * s) / (by - ty)
            for side in (-1, 1):
                c.ellipse(gx + side * 3 * s, gy, 3.5 * s + 1, 5.5 * s + 1, OUT, side * 0.5)
                c.ellipse(gx + side * 3 * s, gy, 3.5 * s, 5.5 * s, "#e9c14a", side * 0.5)


def draw_tomato(c, x=32, y=36, s=1.0):
    c.circle(x, y, 22 * s + 1.5, OUT)
    c.circle(x, y, 22 * s, "#e53935")
    c.ellipse(x - 8 * s, y - 8 * s, 7 * s, 4 * s, "#ff8a80", -0.6)
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        c.ellipse(x + math.cos(a) * 6 * s, y - 20 * s + math.sin(a) * 3 * s, 6 * s, 2.5 * s, "#2e7d32", a)
    c.line(x, y - 22 * s, x + 2 * s, y - 28 * s, 3 * s, "#2e7d32")


def draw_pumpkin(c, x=32, y=38, s=1.0):
    c.ellipse(x, y, 27 * s + 1.5, 20 * s + 1.5, OUT)
    for dx, rx, col in [(-14, 12, "#e07b16"), (14, 12, "#e07b16"), (-6, 12, "#f39c2a"), (6, 12, "#f39c2a"), (0, 9, "#f7ad45")]:
        c.ellipse(x + dx * s, y, rx * s, 20 * s, col)
    c.line(x, y - 18 * s, x + 4 * s, y - 27 * s, 4 * s, "#6d4c22")
    c.ellipse(x + 10 * s, y - 22 * s, 7 * s, 3.5 * s, "#4caf50", -0.4)


def draw_seed_packet(c, crop_fn, tint):
    c.rect(11, 6, 53, 60, OUT)
    c.rect(13, 8, 51, 58, "#efe2c4")
    c.rect(13, 8, 51, 16, tint)
    c.poly([(13, 8), (51, 8), (47, 4), (17, 4)], shade(tint, 0.8))
    crop_fn(c, 32, 40, 0.55)


def draw_soil(c):
    c.rect(4, 12, 60, 54, OUT)
    c.rect(6, 14, 58, 52, "#6b4423")
    for k in range(4):
        y = 19 + k * 9
        c.rect(8, y, 56, y + 4, "#4a2e16")
        c.rect(8, y - 2, 56, y, "#82552e")


def draw_hay(c):
    c.rect(6, 18, 58, 52, OUT)
    c.rect(8, 20, 56, 50, "#e3c25a")
    for k in range(9):
        x = 10 + k * 5.5
        c.line(x, 22, x + 3, 48, 1.2, "#c49a32")
    c.rect(20, 20, 24, 50, "#8a5a2b")
    c.rect(40, 20, 44, 50, "#8a5a2b")


def draw_egg(c, x=32, y=34, s=1.0):
    c.ellipse(x, y, 17 * s + 1.5, 23 * s + 1.5, OUT)
    c.ellipse(x, y, 17 * s, 23 * s, "#f5ead6")
    c.ellipse(x - 6 * s, y - 9 * s, 5 * s, 8 * s, "#ffffff", -0.3)


def draw_feather(c):
    c.ellipse(32, 30, 11, 25, OUT, 0.6)
    c.ellipse(32, 30, 9.5, 23.5, "#f4f4f4", 0.6)
    c.line(20, 52, 44, 10, 2, "#9e9e9e")


def draw_milk(c):
    c.poly([(22, 14), (42, 14), (46, 26), (46, 58), (18, 58), (18, 26)], OUT)
    c.poly([(24, 16), (40, 16), (44, 27), (44, 56), (20, 56), (20, 27)], "#fafafa")
    c.rect(24, 8, 40, 16, OUT)
    c.rect(26, 10, 38, 16, "#64b5f6")
    c.rect(20, 34, 44, 46, "#90caf9")


def draw_wool(c):
    for x, y, r in [(22, 36, 13), (40, 34, 14), (31, 26, 13), (32, 42, 13)]:
        c.circle(x, y, r + 1.5, OUT)
    for x, y, r in [(22, 36, 13), (40, 34, 14), (31, 26, 13), (32, 42, 13)]:
        c.circle(x, y, r, "#f3efe6")
    c.circle(28, 28, 5, "#ffffff")


def draw_flour(c):
    c.poly([(16, 20), (48, 20), (54, 58), (10, 58)], OUT)
    c.poly([(18, 22), (46, 22), (52, 56), (12, 56)], "#f1e9d8")
    c.ellipse(32, 18, 12, 6, OUT)
    c.ellipse(32, 18, 10, 4.5, "#d8ccb4")
    draw_wheat(c, 32, 42, 0.35)


def draw_bread(c):
    c.ellipse(32, 38, 27, 17, OUT)
    c.ellipse(32, 38, 25.5, 15.5, "#c98a3e")
    c.ellipse(32, 33, 23, 10, "#dda25a")
    for dx in (-10, 0, 10):
        c.line(32 + dx - 4, 30, 32 + dx + 4, 36, 2, "#8f5a22")


def draw_cheese(c):
    c.poly([(8, 44), (56, 30), (56, 52), (8, 58)], OUT)
    c.poly([(10, 45), (54, 32), (54, 51), (10, 56)], "#f5c542")
    c.poly([(8, 44), (36, 12), (56, 30)], OUT)
    c.poly([(11, 43), (36, 15), (53, 30)], "#ffd966")
    for x, y, r in [(22, 48, 3), (40, 44, 4), (32, 32, 3)]:
        c.circle(x, y, r, "#d9a520")


def draw_pie(c):
    c.ellipse(32, 40, 28, 16, OUT)
    c.ellipse(32, 40, 26.5, 14.5, "#b5762f")
    c.ellipse(32, 37, 23, 11, "#e0892b")
    for k in range(5):
        c.line(14 + k * 9, 30, 18 + k * 9, 46, 2, "#c96d14")


def draw_soup(c):
    c.ellipse(32, 30, 26, 9, OUT)
    c.poly([(6, 30), (58, 30), (46, 54), (18, 54)], OUT)
    c.poly([(8, 31), (56, 31), (45, 52), (19, 52)], "#5d8aa8")
    c.ellipse(32, 30, 24, 7.5, "#e0703a")
    for x, y, col in [(22, 30, "#f28a1e"), (36, 28, "#c8a165"), (42, 31, "#5cb85c")]:
        c.circle(x, y, 3, col)


def draw_chicken(c, x=32, y=36, s=1.0):
    c.ellipse(x, y, 20 * s + 1.5, 16 * s + 1.5, OUT)
    c.ellipse(x, y, 20 * s, 16 * s, "#fafafa")
    c.circle(x + 14 * s, y - 14 * s, 9 * s + 1.5, OUT)
    c.circle(x + 14 * s, y - 14 * s, 9 * s, "#fafafa")
    c.poly([(x + 22 * s, y - 15 * s), (x + 29 * s, y - 12 * s), (x + 22 * s, y - 10 * s)], "#f5a623")
    c.circle(x + 12 * s, y - 23 * s, 4 * s, "#e53935")
    c.circle(x + 16 * s, y - 22 * s, 3 * s, "#e53935")
    c.circle(x + 16 * s, y - 15 * s, 1.6 * s, OUT)
    c.ellipse(x - 5 * s, y, 10 * s, 6 * s, "#e8e8e8", 0.3)
    c.line(x - 4 * s, y + 15 * s, x - 4 * s, y + 23 * s, 2 * s, "#f5a623")
    c.line(x + 5 * s, y + 15 * s, x + 5 * s, y + 23 * s, 2 * s, "#f5a623")


def draw_cow(c, x=32, y=36, s=1.0):
    for lx in (-14, -6, 8, 15):
        c.rect(x + lx * s - 2.5 * s, y + 6 * s, x + lx * s + 2.5 * s, y + 22 * s, OUT)
    c.ellipse(x - 2 * s, y, 24 * s + 1.5, 13 * s + 1.5, OUT)
    c.ellipse(x - 2 * s, y, 24 * s, 13 * s, "#fafafa")
    c.ellipse(x - 10 * s, y - 3 * s, 7 * s, 5 * s, "#3b2a20")
    c.ellipse(x + 6 * s, y + 4 * s, 6 * s, 4 * s, "#3b2a20")
    c.ellipse(x + 23 * s, y - 9 * s, 9 * s + 1.5, 8 * s + 1.5, OUT)
    c.ellipse(x + 23 * s, y - 9 * s, 9 * s, 8 * s, "#fafafa")
    c.ellipse(x + 27 * s, y - 5 * s, 5 * s, 4 * s, "#f4b6b6")
    c.line(x + 18 * s, y - 16 * s, x + 15 * s, y - 21 * s, 2.5 * s, "#d7c49e")
    c.circle(x + 22 * s, y - 11 * s, 1.6 * s, OUT)


def draw_sheep(c, x=32, y=36, s=1.0):
    for lx in (-12, -4, 6, 13):
        c.rect(x + lx * s - 2.2 * s, y + 6 * s, x + lx * s + 2.2 * s, y + 21 * s, OUT)
    for dx, dy, r in [(-12, 0, 10), (-2, -5, 11), (8, 0, 10), (-3, 5, 10)]:
        c.circle(x + dx * s, y + dy * s, r * s + 1.5, OUT)
    for dx, dy, r in [(-12, 0, 10), (-2, -5, 11), (8, 0, 10), (-3, 5, 10)]:
        c.circle(x + dx * s, y + dy * s, r * s, "#f3efe6")
    c.ellipse(x + 20 * s, y - 6 * s, 7 * s + 1.5, 8 * s + 1.5, OUT, -0.3)
    c.ellipse(x + 20 * s, y - 6 * s, 7 * s, 8 * s, "#4a3b33", -0.3)
    c.circle(x + 22 * s, y - 8 * s, 1.5 * s, "#ffffff")


def draw_farm_pack(c):
    c.poly([(26, 6), (38, 6), (38, 24), (54, 54), (50, 60), (14, 60), (10, 54), (26, 24)], OUT)
    c.poly([(28, 8), (36, 8), (36, 25), (51, 54), (48, 58), (16, 58), (13, 54), (28, 25)], "#e8f5e9")
    c.poly([(21, 40), (43, 40), (51, 54), (48, 58), (16, 58), (13, 54)], "#7cb342")
    leaves(c, 32, 42, 0.8, "#33691e", 2, 0.9, 14)
    c.rect(26, 4, 38, 9, "#8d6e63")


def draw_tower_badge(c):
    # A watering-can like badge used for the garden tower icon overlay
    c.ellipse(30, 38, 20, 16, OUT)
    c.ellipse(30, 38, 18, 14, "#4fa3d1")
    c.line(44, 34, 58, 20, 4, OUT)
    c.line(44, 34, 57, 21, 2.5, "#4fa3d1")
    c.line(14, 26, 26, 22, 3, OUT)


def draw_flax(c, x=32, y=34, s=1.0):
    for off, ang in [(-8, -0.2), (0, 0), (8, 0.2)]:
        bx, by = x + off * s, y + 26 * s
        tx, ty = x + off * s + math.sin(ang) * 30 * s, y - 18 * s
        c.line(bx, by, tx, ty, 2 * s, "#6a9a3a")
        for i in range(5):
            a = i * 2 * math.pi / 5
            c.ellipse(tx + math.cos(a) * 4 * s, ty + math.sin(a) * 4 * s, 3.5 * s, 2.2 * s, "#6fa8dc", a)
        c.circle(tx, ty, 2 * s, "#f6e27a")


def draw_fiber(c):
    for k in range(7):
        y0 = 14 + k * 5
        c.line(10, y0 + 8, 54, y0, 2.2, "#a68a5b" if k % 2 else "#c9b07a")
    c.rect(26, 10, 34, 56, OUT)
    c.rect(27, 11, 33, 55, "#7a5c34")


def draw_plank(c):
    for k, (y, col) in enumerate([(16, "#c8925a"), (30, "#b98450"), (44, "#d29d63")]):
        c.rect(6, y, 58, y + 12, OUT)
        c.rect(7.5, y + 1.5, 56.5, y + 10.5, col)
        c.line(12, y + 5, 30, y + 6, 1, "#9c6b3a")
        c.line(36, y + 7, 52, y + 6, 1, "#9c6b3a")


def draw_resin(c):
    c.ellipse(32, 40, 20 + 1.5, 16 + 1.5, OUT)
    c.ellipse(32, 40, 20, 16, "#e3a018")
    c.poly([(24, 30), (32, 6), (40, 30)], OUT)
    c.poly([(26, 30), (32, 9), (38, 30)], "#e3a018")
    c.ellipse(25, 36, 6, 4, "#ffd36a", -0.5)


def draw_limestone(c):
    c.poly([(10, 44), (18, 20), (38, 12), (54, 26), (56, 46), (36, 56)], OUT)
    c.poly([(12, 43), (19, 22), (37, 14), (52, 27), (54, 45), (36, 54)], "#e6e1cf")
    c.poly([(19, 22), (37, 14), (34, 30), (22, 34)], "#f6f3e8")
    c.circle(40, 40, 3, "#c9c2a8")
    c.circle(26, 44, 2, "#c9c2a8")


def draw_biocement(c):
    c.rect(8, 16, 56, 52, OUT)
    c.rect(10, 18, 54, 50, "#cfd8c4")
    c.rect(10, 18, 54, 26, "#e3ead9")
    leaves(c, 32, 44, 0.7, "#6fbf4a", 3, 0.6, 14)


def draw_sugar(c):
    c.poly([(14, 52), (20, 24), (44, 24), (50, 52)], OUT)
    c.poly([(16, 50), (21.5, 26), (42.5, 26), (48, 50)], "#f7f3ea")
    for x, y in [(22, 18), (32, 12), (42, 18), (27, 6), (37, 6)]:
        c.rect(x - 4, y - 4, x + 4, y + 4, OUT)
        c.rect(x - 3, y - 3, x + 3, y + 3, "#ffffff")


def draw_digester_badge(c):
    c.ellipse(32, 36, 24, 20, OUT)
    c.ellipse(32, 36, 22, 18, "#d97a8a")
    c.ellipse(26, 30, 8, 5, "#f2b3bd", -0.4)
    for x, y in [(36, 40), (24, 42), (40, 30)]:
        c.circle(x, y, 3, "#a64b5c")


def helix(c, x0, y0, x1, y1, amp, turns, w, col_a, col_b, rungs=True):
    n = 60
    pts_a, pts_b = [], []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        ph = t * turns * 2 * math.pi
        pts_a.append((x0 + (x1 - x0) * t + math.sin(ph) * amp, y))
        pts_b.append((x0 + (x1 - x0) * t - math.sin(ph) * amp, y))
    if rungs:
        for i in range(0, n + 1, 5):
            c.line(pts_a[i][0], pts_a[i][1], pts_b[i][0], pts_b[i][1], w * 0.6, "#d8d8e8")
    for i in range(n):
        c.line(pts_a[i][0], pts_a[i][1], pts_a[i + 1][0], pts_a[i + 1][1], w, col_a)
        c.line(pts_b[i][0], pts_b[i][1], pts_b[i + 1][0], pts_b[i + 1][1], w, col_b)


def draw_dna_sample(c):
    # test tube with green liquid and a helix
    c.poly([(22, 4), (42, 4), (42, 50), (32, 60), (22, 50)], OUT)
    c.poly([(24, 6), (40, 6), (40, 49), (32, 57.5), (24, 49)], "#eef6f0")
    c.poly([(24, 30), (40, 30), (40, 49), (32, 57.5), (24, 49)], "#7cc35a")
    c.rect(20, 2, 44, 8, "#8d6e63")
    helix(c, 32, 12, 32, 52, 5, 1.5, 2, "#2e7d32", "#c2185b")


def draw_genome_sequence(c):
    c.circle(32, 32, 27, OUT)
    c.circle(32, 32, 25.5, "#2c3e50")
    c.circle(32, 32, 20, "#34495e")
    for k in range(12):
        a = k * math.pi / 6
        c.line(32 + math.cos(a) * 21, 32 + math.sin(a) * 21, 32 + math.cos(a) * 25, 32 + math.sin(a) * 25, 2, "#7cc35a")
    helix(c, 18, 32, 46, 32, 0.01, 0, 1, "#000000", "#000000", rungs=False)
    n = 40
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        for sgn, col in ((1, "#7cc35a"), (-1, "#f06292")):
            x0 = 16 + 32 * t0; x1 = 16 + 32 * t1
            y0 = 32 + sgn * math.sin(t0 * 3 * math.pi) * 8
            y1 = 32 + sgn * math.sin(t1 * 3 * math.pi) * 8
            c.line(x0, y0, x1, y1, 2.2, col)


def draw_silk(c):
    c.rect(18, 8, 46, 14, OUT); c.rect(18, 50, 46, 56, OUT)
    c.rect(20, 9.5, 44, 12.5, "#a1887f"); c.rect(20, 51.5, 44, 54.5, "#a1887f")
    c.rect(22, 14, 42, 50, OUT)
    c.rect(23.5, 14, 40.5, 50, "#fbfbff")
    for k in range(9):
        y = 16 + k * 4
        c.line(24, y, 40, y + 2, 1, "#d6d6ea")
    c.line(40, 40, 56, 58, 1.5, "#fbfbff")


def draw_ant(c, x=32, y=34, s=1.0):
    for side in (-1, 1):
        for k, dy in enumerate((-6, 0, 6)):
            c.line(x, y + dy * s, x + side * 18 * s, y + dy * s + (k - 1) * 8 * s, 2 * s, OUT)
    c.ellipse(x, y + 16 * s, 8 * s, 11 * s, OUT); c.ellipse(x, y + 16 * s, 6.5 * s, 9.5 * s, "#a0522d")
    c.ellipse(x, y, 5 * s, 7 * s, OUT); c.ellipse(x, y, 3.8 * s, 5.8 * s, "#b5652d")
    c.circle(x, y - 12 * s, 7 * s, OUT); c.circle(x, y - 12 * s, 5.8 * s, "#a0522d")
    c.line(x - 2 * s, y - 17 * s, x - 9 * s, y - 26 * s, 1.5 * s, OUT)
    c.line(x + 2 * s, y - 17 * s, x + 9 * s, y - 26 * s, 1.5 * s, OUT)


def draw_spider(c, x=32, y=34, s=1.0):
    for side in (-1, 1):
        for k in range(4):
            a = (k - 1.5) * 0.45
            mx, my = x + side * 14 * s, y + (k - 1.5) * 8 * s - 6 * s
            c.line(x, y, mx, my, 2.2 * s, OUT)
            c.line(mx, my, mx + side * 8 * s, my + 12 * s, 2.2 * s, OUT)
    c.circle(x, y + 8 * s, 12 * s, OUT); c.circle(x, y + 8 * s, 10.5 * s, "#5d4037")
    c.circle(x, y - 6 * s, 7 * s, OUT); c.circle(x, y - 6 * s, 5.8 * s, "#6d4c41")
    c.ellipse(x, y + 8 * s, 3 * s, 5 * s, "#ffcc80")


def draw_mushroom(c, x=32, y=36, s=1.0):
    c.rect(x - 7 * s, y - 4 * s, x + 7 * s, y + 20 * s, OUT)
    c.rect(x - 5.5 * s, y - 4 * s, x + 5.5 * s, y + 18.5 * s, "#f3e9d8")
    c.ellipse(x, y - 6 * s, 24 * s + 1.5, 14 * s + 1.5, OUT)
    c.ellipse(x, y - 6 * s, 24 * s, 14 * s, "#c0392b")
    c.rect(x - 26 * s, y - 6 * s, x + 26 * s, y + 10 * s, (0, 0, 0, 0))
    for dx, dy, r in [(-12, -10, 3.5), (2, -14, 3), (12, -6, 4), (-3, -4, 2.5)]:
        c.circle(x + dx * s, y + dy * s, r * s, "#fff6e8")


def draw_mycelium(c):
    c.ellipse(32, 46, 26, 12, OUT)
    c.ellipse(32, 46, 24.5, 10.5, "#6d4c41")
    import random
    rnd = random.Random(7)
    for _ in range(26):
        x0, y0 = 32 + rnd.uniform(-20, 20), 46 + rnd.uniform(-6, 6)
        a = rnd.uniform(-math.pi, 0)
        l = rnd.uniform(8, 22)
        c.line(x0, y0, x0 + math.cos(a) * l, y0 + math.sin(a) * l * 1.3, 1.3, "#f5f0e6")
    for x, y in [(18, 24), (40, 18), (50, 30), (28, 14)]:
        c.circle(x, y, 2.5, "#ffffff")


def draw_nerve_tissue(c):
    c.circle(32, 32, 10 + 1.5, OUT)
    c.circle(32, 32, 10, "#f48fb1")
    c.circle(32, 32, 4, "#ad1457")
    for k in range(6):
        a = k * math.pi / 3 + 0.3
        ex, ey = 32 + math.cos(a) * 26, 32 + math.sin(a) * 26
        c.line(32 + math.cos(a) * 9, 32 + math.sin(a) * 9, ex, ey, 3, OUT)
        c.line(32 + math.cos(a) * 9, 32 + math.sin(a) * 9, ex, ey, 1.8, "#f8bbd0")
        for side in (-0.5, 0.5):
            c.line(ex, ey, ex + math.cos(a + side) * 6, ey + math.sin(a + side) * 6, 1.4, "#f8bbd0")


def draw_chitin(c):
    c.poly([(32, 6), (54, 18), (50, 46), (32, 58), (14, 46), (10, 18)], OUT)
    c.poly([(32, 9), (51, 19.5), (47.5, 44.5), (32, 55), (16.5, 44.5), (13, 19.5)], "#2e7d6b")
    c.poly([(32, 9), (51, 19.5), (32, 30), (13, 19.5)], "#3fa58c")
    c.line(32, 30, 32, 55, 1.5, "#1b4d42")
    c.ellipse(24, 18, 6, 2.5, "#9be7d3", -0.4)


def draw_seedling(c):
    c.ellipse(32, 50, 22, 8, OUT)
    c.ellipse(32, 50, 20.5, 6.5, "#6b4423")
    c.line(32, 50, 32, 22, 4, "#3d8b37")
    c.ellipse(21, 24, 12, 6, OUT, -0.5); c.ellipse(21, 24, 10.5, 4.8, "#7bc96f", -0.5)
    c.ellipse(43, 20, 12, 6, OUT, 0.5); c.ellipse(43, 20, 10.5, 4.8, "#7bc96f", 0.5)


def big_sprout(path):
    c = Canvas(128, 128)
    c.ellipse(64, 70, 58, 50, (0.24, 0.15, 0.07, 0.9))
    c.ellipse(64, 66, 50, 42, (0.36, 0.23, 0.11, 1))
    import random
    rnd = random.Random(3)
    for _ in range(9):
        x, y = 64 + rnd.uniform(-34, 34), 66 + rnd.uniform(-26, 26)
        c.line(x, y, x, y - 14, 2.5, "#3d8b37")
        c.ellipse(x - 5, y - 15, 6, 3, "#7bc96f", -0.5)
        c.ellipse(x + 5, y - 17, 6, 3, "#7bc96f", 0.5)
    c.save(path)


def draw_bacteria_culture(c):
    c.ellipse(32, 40, 28, 14, OUT)
    c.ellipse(32, 40, 26.5, 12.5, "#e3f2fd")
    c.ellipse(32, 38, 23, 10, "#f0e6c8")
    for x, y, r, col in [(20, 38, 4, "#8bc34a"), (34, 35, 5, "#cddc39"), (44, 40, 3.5, "#7cb342"), (28, 43, 3, "#9ccc65"), (40, 44, 2.5, "#aed581")]:
        c.circle(x, y, r, col)
    c.ellipse(32, 28, 27, 9, (0.85, 0.92, 1, 0.5))


def draw_crispr_kit(c):
    helix(c, 14, 50, 50, 14, 6, 1.5, 2.2, "#7cc35a", "#f06292")
    # scissors
    c.line(30, 30, 52, 52, 3.5, OUT); c.line(30, 30, 52, 52, 2, "#cfd8dc")
    c.line(52, 30, 30, 52, 3.5, OUT); c.line(52, 30, 30, 52, 2, "#cfd8dc")
    c.circle(54, 54, 6, OUT); c.circle(54, 54, 4, "#e53935"); c.circle(54, 54, 2, "#e3f2fd")
    c.circle(28, 54, 6, OUT); c.circle(28, 54, 4, "#e53935"); c.circle(28, 54, 2, "#e3f2fd")


def draw_bee(c, x=32, y=34, s=1.0):
    c.ellipse(x - 8 * s, y - 12 * s, 10 * s, 6 * s, (0.85, 0.95, 1, 0.85), -0.5)
    c.ellipse(x + 8 * s, y - 12 * s, 10 * s, 6 * s, (0.85, 0.95, 1, 0.85), 0.5)
    c.ellipse(x, y + 4 * s, 13 * s + 1.5, 17 * s + 1.5, OUT)
    c.ellipse(x, y + 4 * s, 13 * s, 17 * s, "#fbc02d")
    for dy in (-2, 6, 14):
        c.rect(x - 13 * s, y + dy * s, x + 13 * s, y + (dy + 3.5) * s, OUT)
    c.circle(x, y - 14 * s, 7 * s + 1.5, OUT); c.circle(x, y - 14 * s, 7 * s, "#3e2723")


def draw_algae(c):
    c.ellipse(32, 40, 28, 16, OUT)
    c.ellipse(32, 40, 26.5, 14.5, "#3d7fa6")
    for x, y, r, col in [(20, 38, 7, "#5fbf5a"), (34, 34, 8, "#7ed36a"), (44, 42, 6, "#4caf50"), (28, 46, 5, "#8bd47a")]:
        c.circle(x, y, r + 1, OUT)
        c.circle(x, y, r, col)
    c.ellipse(30, 32, 4, 2, "#c8f0b8", -0.4)


def draw_reed(c, x=32, y=34, s=1.0):
    c.ellipse(x, y + 22 * s, 24 * s, 6 * s, "#3d7fa6")
    for off, h in [(-12, 34), (-4, 42), (4, 38), (12, 30)]:
        c.line(x + off * s, y + 22 * s, x + off * s, y + (22 - h) * s, 2 * s, "#6a8f3a")
        c.ellipse(x + off * s, y + (22 - h + 5) * s, 3.5 * s + 1, 7 * s + 1, OUT)
        c.ellipse(x + off * s, y + (22 - h + 5) * s, 3.5 * s, 7 * s, "#8d5a2b")


def draw_lotus(c, x=32, y=36, s=1.0):
    c.ellipse(x, y + 12 * s, 28 * s, 8 * s, "#4caf50")
    for k, (a, l) in enumerate([(-1.1, 18), (-0.55, 22), (0, 24), (0.55, 22), (1.1, 18)]):
        ex, ey = x + math.sin(a) * l * s, y - math.cos(a) * l * s + 8 * s
        mx, my = (x + ex) / 2, (y + 8 * s + ey) / 2
        c.ellipse(mx, my, 6 * s + 1, l * s / 2 + 1, OUT, a)
        c.ellipse(mx, my, 6 * s, l * s / 2, "#f48fb1" if k % 2 else "#f8bbd0", a)
    c.circle(x, y + 6 * s, 4 * s, "#fdd835")


def draw_plant_oil(c):
    c.poly([(26, 6), (38, 6), (38, 18), (48, 28), (48, 58), (16, 58), (16, 28), (26, 18)], OUT)
    c.poly([(28, 8), (36, 8), (36, 19), (46, 29), (46, 56), (18, 56), (18, 29), (28, 19)], "#fff8e1")
    c.poly([(18, 34), (46, 34), (46, 56), (18, 56)], "#e6b422")
    c.rect(25, 3, 39, 8, "#6d4c41")
    leaves(c, 32, 52, 0.6, "#5a8f2e", 3, 0.6, 14)


def draw_synthetic_genome(c):
    c.poly([(32, 4), (56, 18), (56, 46), (32, 60), (8, 46), (8, 18)], OUT)
    c.poly([(32, 7), (53.5, 19.5), (53.5, 44.5), (32, 57), (10.5, 44.5), (10.5, 19.5)], "#1f3b4d")
    helix(c, 32, 12, 32, 52, 9, 2, 2.4, "#4dd0e1", "#f48fb1")
    c.circle(32, 32, 5, OUT)
    c.circle(32, 32, 3.5, "#fdd835")


# ---------------------------------------------------------------- entity sprites (crop on soil)


def crop_sprite(fn, path, scale):
    c = Canvas(64, 64)
    c.ellipse(32, 52, 22, 7, (0.24, 0.15, 0.07, 0.85))  # soil patch
    for k in range(3):
        c.line(14 + k * 12, 52, 20 + k * 12, 50, 1.5, (0.4, 0.26, 0.13, 0.9))
    fn(c, 32, 36, scale)
    c.save(path)


def plant_draw(kind):
    def f(c, x, y, s):
        if kind == "carrot":
            leaves(c, x, y + 14, s * 1.4, "#5cb85c", 5, 0.4, 22)
            c.ellipse(x, y + 15, 6 * s, 3 * s, "#f28a1e")
        elif kind == "potato":
            leaves(c, x, y + 14, s * 1.3, "#4f9a3f", 5, 0.5, 20)
            for dx in (-12, 12, 0):
                c.circle(x + dx * s, y - 2 * s + abs(dx) * 0.6, 4 * s, "#ffffff")
                c.circle(x + dx * s, y - 2 * s + abs(dx) * 0.6, 1.6 * s, "#f1c40f")
        elif kind == "wheat":
            for off in (-12, -4, 4, 12):
                draw_wheat_stalk(c, x + off * s, y + 16, s)
        elif kind == "tomato":
            c.line(x, y + 16, x, y - 18 * s, 3 * s, "#8d6e63")
            leaves(c, x, y + 10, s * 1.2, "#43a047", 5, 0.55, 20)
            for dx, dy in [(-8, -2), (7, 3), (-2, -12), (9, -10)]:
                c.circle(x + dx * s, y + dy * s, 5 * s + 1, OUT)
                c.circle(x + dx * s, y + dy * s, 5 * s, "#e53935")
        elif kind == "flax":
            for off in (-12, -4, 4, 12):
                c.line(x + off * s, y + 16, x + off * s, y - 22 * s, 1.8 * s, "#6a9a3a")
                c.circle(x + off * s, y - 22 * s, 3.5 * s, "#6fa8dc")
        elif kind == "pumpkin":
            leaves(c, x - 8, y + 12, s * 1.1, "#43a047", 3, 0.8, 16)
            leaves(c, x + 10, y + 12, s * 1.1, "#4caf50", 3, 0.8, 14)
            draw_pumpkin(c, x, y + 6, s * 0.6)
    return f


def draw_wheat_stalk(c, x, y, s):
    c.line(x, y, x, y - 30 * s, 2 * s, "#b88a2a")
    for k in range(4):
        gy = y - 30 * s + k * 5 * s
        for side in (-1, 1):
            c.ellipse(x + side * 2.5 * s, gy, 2.5 * s, 4 * s, "#e9c14a", side * 0.5)


def mound(path):
    c = Canvas(64, 64)
    c.ellipse(32, 46, 20, 9, (0.2, 0.12, 0.05, 0.9))
    c.ellipse(32, 44, 16, 6, (0.36, 0.23, 0.11, 1))
    c.line(32, 44, 30, 36, 2, "#6fbf4a")
    c.ellipse(27, 36, 4, 2, "#6fbf4a", -0.5)
    c.ellipse(34, 35, 4, 2, "#6fbf4a", 0.5)
    c.save(path)


# ---------------------------------------------------------------- building sprites
# Drawn in tile units: (cx, cy) is the building centre, s = pixels per tile (64 for entity sprites).
# Each building has draw(c, cx, cy, s) and shadow(c, cx, cy, s).

SHADOW = (0, 0, 0, 0.55)


def algae_farm(c, cx, cy, s):
    import random
    rnd = random.Random(11)
    c.ellipse(cx, cy + 0.1 * s, 1.6 * s, 1.45 * s, (0.75, 0.9, 1, 0.3))          # ripple on water
    c.ellipse(cx, cy + 0.12 * s, 1.47 * s, 1.32 * s, OUT)
    c.ellipse(cx, cy + 0.1 * s, 1.43 * s, 1.28 * s, "#6b4f33")                   # front wall
    c.ellipse(cx, cy - 0.02 * s, 1.43 * s, 1.24 * s, "#a07a52")                  # rim top
    for k in range(28):                                                         # woven rim
        a = k * 2 * math.pi / 28
        x, y = cx + math.cos(a) * 1.3 * s, cy - 0.02 * s + math.sin(a) * 1.12 * s
        c.line(x - 0.06 * s, y - 0.04 * s, x + 0.06 * s, y + 0.04 * s, 0.04 * s, "#7a5a3a")
    c.ellipse(cx, cy - 0.05 * s, 1.16 * s, 0.98 * s, "#1f5e46")                  # water
    c.ellipse(cx, cy - 0.1 * s, 1.08 * s, 0.9 * s, "#2f7a5a")
    for _ in range(26):                                                         # algae mats
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, 0.85)
        x, y = cx + math.cos(a) * r * s, cy - 0.08 * s + math.sin(a) * r * 0.85 * s
        col = rnd.choice(["#5fbf5a", "#7ed36a", "#4caf50", "#9ad97a"])
        c.ellipse(x, y, rnd.uniform(0.08, 0.2) * s, rnd.uniform(0.06, 0.14) * s, col, rnd.uniform(0, 3))
    for _ in range(10):                                                         # bubbles
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, 0.8)
        c.circle(cx + math.cos(a) * r * s, cy - 0.08 * s + math.sin(a) * r * 0.85 * s, 0.035 * s, (1, 1, 1, 0.8))
    for a in (math.pi * 1.25, math.pi * 1.75, math.pi * 0.5):                   # light posts with glowing bulbs
        x, y = cx + math.cos(a) * 1.3 * s, cy - 0.02 * s + math.sin(a) * 1.12 * s
        c.line(x, y, x, y - 0.55 * s, 0.07 * s, OUT)
        c.line(x, y, x, y - 0.55 * s, 0.04 * s, "#8d6e4a")
        c.circle(x, y - 0.6 * s, 0.13 * s, (0.7, 1, 0.5, 0.35))
        c.circle(x, y - 0.6 * s, 0.08 * s, "#c6ff8a")


def algae_farm_shadow(c, cx, cy, s):
    c.ellipse(cx + 0.25 * s, cy + 0.2 * s, 1.45 * s, 1.25 * s, SHADOW)


REED_SPOTS = [(-0.9, -0.85), (0.1, -0.95), (0.95, -0.8), (-0.6, 0.0), (0.55, 0.05), (-1.0, 0.85), (0.0, 0.8), (0.95, 0.9)]


def reed_filter(c, cx, cy, s):
    import random
    rnd = random.Random(5)
    c.ellipse(cx, cy + 0.15 * s, 1.75 * s, 1.6 * s, (0.75, 0.9, 1, 0.25))         # ripple
    c.rect(cx - 1.45 * s, cy - 1.35 * s, cx + 1.45 * s, cy + 1.55 * s, OUT)
    c.rect(cx - 1.4 * s, cy + 1.3 * s, cx + 1.4 * s, cy + 1.5 * s, "#6b4f33")      # front edge of the raft
    c.rect(cx - 1.4 * s, cy - 1.3 * s, cx + 1.4 * s, cy + 1.3 * s, "#a07a52")
    for k in range(8):                                                          # logs
        y = cy - 1.3 * s + (k + 0.5) * 2.6 * s / 8
        c.line(cx - 1.38 * s, y, cx + 1.38 * s, y, 0.03 * s, "#7a5a3a")
    for y0 in (-0.95, -0.1, 0.75):                                              # filtering channels
        c.rect(cx - 1.25 * s, cy + (y0 - 0.25) * s, cx + 1.25 * s, cy + (y0 + 0.25) * s, "#2b5f78")
        c.rect(cx - 1.2 * s, cy + (y0 - 0.2) * s, cx + 1.2 * s, cy + (y0 + 0.2) * s, "#3f88a8")
        for k in range(5):
            x = cx + (-1 + k * 0.5) * s
            c.line(x, cy + y0 * s, x + 0.2 * s, cy + y0 * s, 0.025 * s, (1, 1, 1, 0.6))
    for dx, dy in sorted(REED_SPOTS, key=lambda p: p[1]):                       # back to front
        bx, by = cx + dx * s, cy + dy * s
        for k in range(5):
            ox = (k - 2) * 0.09 * s
            h = rnd.uniform(1.1, 1.7) * s
            lean = rnd.uniform(-0.15, 0.15) * s
            tx, ty = bx + ox + lean, by - h
            c.line(bx + ox, by, tx, ty, 0.06 * s, OUT)
            c.line(bx + ox, by, tx, ty, 0.035 * s, "#7fa046")
            if k % 2 == 0:                                                      # cattail
                c.ellipse(tx, ty + 0.22 * s, 0.07 * s + 1, 0.2 * s + 1, OUT)
                c.ellipse(tx, ty + 0.22 * s, 0.07 * s, 0.2 * s, "#8d5a2b")
            else:                                                               # leaf
                c.line(bx + ox, by - 0.2 * s, bx + ox + rnd.choice((-1, 1)) * 0.35 * s, by - 0.9 * s, 0.03 * s, "#9cc35a")


def reed_filter_shadow(c, cx, cy, s):
    c.rect(cx - 1.2 * s, cy - 1.1 * s, cx + 1.7 * s, cy + 1.7 * s, SHADOW)
    for dx, dy in REED_SPOTS:
        bx, by = cx + dx * s, cy + dy * s
        c.line(bx, by, bx + 1.2 * s, by + 0.5 * s, 0.25 * s, SHADOW)


def lotus_reactor(c, cx, cy, s):
    c.ellipse(cx, cy + 0.2 * s, 2.55 * s, 2.25 * s, (0.75, 0.9, 1, 0.3))          # ripple
    c.ellipse(cx, cy + 0.15 * s, 2.42 * s, 2.12 * s, OUT)
    c.ellipse(cx, cy + 0.15 * s, 2.38 * s, 2.08 * s, "#2f7a35")                   # pad edge
    c.ellipse(cx, cy + 0.05 * s, 2.32 * s, 2.0 * s, "#4f9e48")
    c.poly([(cx, cy + 0.05 * s), (cx + 0.5 * s, cy + 2.1 * s), (cx + 1.0 * s, cy + 1.9 * s)], "#2b5f78")  # notch
    for k in range(14):                                                         # veins
        a = k * 2 * math.pi / 14 + 0.1
        c.line(cx, cy + 0.05 * s, cx + math.cos(a) * 2.1 * s, cy + 0.05 * s + math.sin(a) * 1.8 * s, 0.035 * s, "#3d8a3a")
    c.circle(cx, cy - 0.5 * s, 1.4 * s, (1, 0.9, 0.6, 0.18))                      # glow
    for ring, (n, length, width, lift, cols) in enumerate([
        (10, 1.25, 0.42, 0.25, ("#f48fb1", "#f06292")),
        (8, 1.0, 0.38, 0.5, ("#f8bbd0", "#f48fb1")),
        (6, 0.72, 0.32, 0.75, ("#fce4ec", "#f8bbd0")),
    ]):
        petals = []
        for k in range(n):
            a = k * 2 * math.pi / n + ring * 0.3
            petals.append((math.sin(a), a))
        for _, a in sorted(petals):                                             # back petals first
            px = cx + math.cos(a) * length * 0.55 * s
            py = cy - lift * s + math.sin(a) * length * 0.38 * s
            ang = math.atan2(math.sin(a) * 0.7, math.cos(a))
            c.ellipse(px, py, length * 0.55 * s + 1.5, width * s + 1.5, OUT, ang)
            c.ellipse(px, py, length * 0.55 * s, width * s, cols[0], ang)
            c.ellipse(px - math.cos(a) * 0.1 * s, py - 0.05 * s, length * 0.35 * s, width * 0.5 * s, cols[1], ang)
    c.ellipse(cx, cy - 0.85 * s, 0.38 * s + 1.5, 0.26 * s + 1.5, OUT)               # seed pod
    c.ellipse(cx, cy - 0.85 * s, 0.38 * s, 0.26 * s, "#fdd835")
    for k in range(7):
        a = k * 2 * math.pi / 7
        c.circle(cx + math.cos(a) * 0.2 * s, cy - 0.85 * s + math.sin(a) * 0.12 * s, 0.04 * s, "#c49000")
    c.circle(cx, cy - 0.85 * s, 0.6 * s, (1, 0.95, 0.5, 0.25))


def lotus_reactor_shadow(c, cx, cy, s):
    c.ellipse(cx + 0.35 * s, cy + 0.3 * s, 2.3 * s, 2.0 * s, (0, 0, 0, 0.35))
    c.ellipse(cx + 0.9 * s, cy + 0.2 * s, 1.4 * s, 0.9 * s, SHADOW)


# ---- helpers for land buildings


def opoly(c, pts, color, w=1.5):
    """Polygon with an outline: the outline is the full shape, the fill is shrunk w px towards the centre."""
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    c.poly(pts, OUT)
    inner = []
    for x, y in pts:
        d = math.hypot(x - mx, y - my) or 1
        inner.append((x + (mx - x) * w / d, y + (my - y) * w / d))
    c.poly(inner, color)


def oellipse(c, x, y, rx, ry, color, angle=0.0, w=1.5):
    c.ellipse(x, y, rx + w, ry + w, OUT, angle)
    c.ellipse(x, y, rx, ry, color, angle)


def grass(c, cx, cy, s, rx=1.5, ry=1.35, col="#6fa84a"):
    c.ellipse(cx, cy + 0.1 * s, rx * s + 1.5, ry * s + 1.5, (0.17, 0.11, 0.07, 0.6))
    c.ellipse(cx, cy + 0.1 * s, rx * s, ry * s, col)
    c.ellipse(cx - 0.2 * s, cy - 0.05 * s, rx * 0.8 * s, ry * 0.7 * s, shade(col, 1.12))


def house(c, x0, x1, yb, hw, rh, d, wall, roof):
    """3/4 view house: front wall x0..x1 standing on yb (hw tall), gable roof rh tall, d deep (drawn upwards)."""
    cx, yt, e = (x0 + x1) / 2, yb - hw, (x1 - x0) * 0.06
    opoly(c, [(x0, yb), (x0, yt - d), (x1, yt - d), (x1, yb)], shade(wall, 0.75))                 # side/back mass
    opoly(c, [(x0 - e, yt), (cx, yt - rh), (cx, yt - rh - d), (x0 - e, yt - d)], shade(roof, 0.8))  # roof planes
    opoly(c, [(x1 + e, yt), (cx, yt - rh), (cx, yt - rh - d), (x1 + e, yt - d)], roof)
    opoly(c, [(x0, yb), (x0, yt), (x1, yt), (x1, yb)], wall)                                        # front wall
    opoly(c, [(x0 - e, yt + 1), (x1 + e, yt + 1), (cx, yt - rh)], shade(wall, 1.1))                 # gable


def fence(c, x0, y0, x1, y1, s, col="#8d6e4a"):
    """Fence along the rectangle edges (posts + two rails)."""
    k = s / 64
    for (ax, ay), (bx, by) in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        for h in (0.12, 0.26):
            c.line(ax, ay - h * s, bx, by - h * s, 2.4 * k, OUT)
            c.line(ax, ay - h * s, bx, by - h * s, 1.4 * k, col)
        n = max(2, int(math.hypot(bx - ax, by - ay) / (0.4 * s)))
        for i in range(n + 1):
            px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            c.line(px, py, px, py - 0.34 * s, 3.4 * k, OUT)
            c.line(px, py, px, py - 0.34 * s, 2.2 * k, shade(col, 0.85))


def blob_shadow(rx, ry, dx=0.4, dy=0.2, tall=0.0):
    """Generic shadow: footprint blob, plus a stretched blob to the right for tall buildings."""
    def f(c, cx, cy, s):
        c.ellipse(cx + dx * s, cy + dy * s, rx * s, ry * s, SHADOW)
        if tall:
            c.ellipse(cx + (rx * 0.6 + tall * 0.5) * s, cy + 0.2 * s, tall * 0.7 * s, ry * 0.55 * s, SHADOW)
    return f


def scatter(rnd, n, rx, ry):
    for _ in range(n):
        a, r = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.uniform(0, 1))
        yield math.cos(a) * r * rx, math.sin(a) * r * ry


# ---- the buildings


def digester(c, cx, cy, s):
    import random
    rnd = random.Random(2)
    k = s / 64
    c.ellipse(cx, cy + 0.45 * s, 1.45 * s, 0.95 * s, "#6b4423")                     # soil
    c.ellipse(cx, cy + 0.4 * s, 1.35 * s, 0.85 * s, "#82552e")
    for side in (-1, 1):                                                            # intestine loops
        oellipse(c, cx + side * 0.95 * s, cy + 0.55 * s, 0.42 * s, 0.3 * s, "#e8a0ab", side * 0.4, 1.5 * k)
        c.ellipse(cx + side * 0.95 * s, cy + 0.55 * s, 0.2 * s, 0.1 * s, "#c9707f", side * 0.4)
    oellipse(c, cx, cy - 0.1 * s, 1.2 * s, 1.0 * s, "#d97a8a", 0, 2 * k)           # stomach
    c.ellipse(cx - 0.1 * s, cy + 0.25 * s, 1.05 * s, 0.6 * s, "#c9687a")
    c.ellipse(cx - 0.35 * s, cy - 0.45 * s, 0.6 * s, 0.35 * s, "#f2b3bd", -0.4)
    for _ in range(7):                                                              # veins
        x, y = cx + rnd.uniform(-0.8, 0.8) * s, cy + rnd.uniform(-0.6, 0.5) * s
        a = rnd.uniform(0, math.pi)
        for _ in range(3):
            nx, ny = x + math.cos(a) * 0.18 * s, y + math.sin(a) * 0.18 * s
            c.line(x, y, nx, ny, 1.6 * k, "#a64b5c")
            x, y, a = nx, ny, a + rnd.uniform(-0.8, 0.8)
    oellipse(c, cx + 0.15 * s, cy - 0.75 * s, 0.25 * s, 0.13 * s, "#7a2f3d", 0, 1.5 * k)  # mouth
    for x, y in [(0.5, -0.3), (-0.55, 0.05), (0.2, 0.2)]:
        c.circle(cx + x * s, cy + y * s, 0.06 * s, (1, 0.9, 0.92, 0.8))


def fermentation_chamber(c, cx, cy, s):
    k = s / 64
    grass(c, cx, cy + 0.3 * s, s, 1.45, 1.0)
    top, bot, rx = cy - 0.75 * s, cy + 0.85 * s, 1.1 * s
    oellipse(c, cx, bot, rx, 0.42 * s, "#6b4f33", 0, 2 * k)                          # barrel
    opoly(c, [(cx - rx, top), (cx + rx, top), (cx + rx, bot), (cx - rx, bot)], "#a07a52", 2 * k)
    c.ellipse(cx, bot, rx - 2 * k, 0.4 * s, "#a07a52")
    for i in range(1, 8):                                                           # staves
        x = cx - rx + i * 2 * rx / 8
        c.line(x, top + 0.2 * s, x, bot + 0.3 * s * math.sqrt(max(0, 1 - ((x - cx) / rx) ** 2)), 1.2 * k, "#7a5a3a")
    for y in (top + 0.35 * s, bot - 0.3 * s):                                       # vine hoops
        for i in range(24):
            a0, a1 = math.pi * i / 24, math.pi * (i + 1) / 24
            c.line(cx - math.cos(a0) * rx, y + math.sin(a0) * 0.4 * s, cx - math.cos(a1) * rx, y + math.sin(a1) * 0.4 * s,
                   4 * k, "#4f8f3a")
        for x in (-0.7, 0.1, 0.8):
            c.ellipse(cx + x * s, y + 0.3 * s * math.sqrt(1 - x * x / 1.21), 0.12 * s, 0.06 * s, "#7bc96f", 0.5)
    oellipse(c, cx, top, rx, 0.42 * s, "#8d6e4a", 0, 2 * k)                          # rim + foam
    c.ellipse(cx, top + 0.03 * s, rx * 0.86, 0.33 * s, "#f3e3b3")
    for x, y, r in [(-0.5, 0, 0.12), (0.2, -0.08, 0.09), (0.55, 0.05, 0.1), (-0.1, 0.1, 0.07), (0.3, 0.12, 0.05)]:
        c.circle(cx + x * s, top + y * s, r * s, "#e0a030")
        c.circle(cx + x * s - r * 0.3 * s, top + y * s - r * 0.3 * s, r * 0.35 * s, "#fff3cf")


def mini_mushroom(c, x, y, h, r, cap, k):
    c.rect(x - r * 0.3 - 1.2 * k, y - h, x + r * 0.3 + 1.2 * k, y, OUT)
    c.rect(x - r * 0.3, y - h, x + r * 0.3, y, "#f3e9d8")
    c.ellipse(x, y - h, r + 1.5 * k, r * 0.6 + 1.5 * k, OUT)
    c.ellipse(x, y - h, r, r * 0.6, cap)
    c.ellipse(x - r * 0.3, y - h - r * 0.2, r * 0.3, r * 0.15, shade(cap, 1.3))


def mushroom_farm(c, cx, cy, s):
    import random
    rnd = random.Random(4)
    k = s / 64
    grass(c, cx, cy + 0.2 * s, s, 1.5, 1.3, "#5f8f45")
    for lx, ly in [(-0.1, -0.7), (0.0, 0.05), (0.05, 0.8)]:                          # mossy logs, back to front
        x0, x1, y = cx - 1.1 * s + lx * s, cx + 1.1 * s + lx * s, cy + ly * s
        opoly(c, [(x0, y - 0.25 * s), (x1, y - 0.25 * s), (x1, y + 0.2 * s), (x0, y + 0.2 * s)], "#7a5a3a", 1.5 * k)
        oellipse(c, x1, y - 0.02 * s, 0.13 * s, 0.22 * s, "#c8a070", 0, 1.5 * k)
        c.circle(x1, y - 0.02 * s, 0.06 * s, "#a07a52")
        c.ellipse((x0 + x1) / 2 - 0.1 * s, y - 0.24 * s, 0.95 * s, 0.07 * s, "#6f9a3a")
        for _ in range(5):
            x = rnd.uniform(x0 + 0.15 * s, x1 - 0.2 * s)
            mini_mushroom(c, x, y - 0.18 * s, rnd.uniform(0.12, 0.28) * s, rnd.uniform(0.1, 0.17) * s,
                          rnd.choice(["#c0392b", "#9c5fc9", "#e08a3a", "#b07ad9"]), k)
    for x, y in [(-0.7, -0.4), (0.5, 0.45), (0.9, -0.3)]:                           # glowing spores
        c.circle(cx + x * s, cy + y * s - 0.6 * s, 0.07 * s, (0.85, 0.75, 1, 0.5))
        c.circle(cx + x * s, cy + y * s - 0.6 * s, 0.035 * s, "#f3e8ff")


def ant_workshop(level):
    def draw(c, cx, cy, s):
        import random
        rnd = random.Random(10 + level)
        k = s / 64
        sand = ["#c9a26b", "#b8875a", "#a0674a"][level - 1]
        c.ellipse(cx, cy + 0.45 * s, 1.5 * s, 0.95 * s, shade(sand, 0.7))
        c.ellipse(cx, cy + 0.4 * s, 1.4 * s, 0.85 * s, shade(sand, 0.85))
        if level >= 2:                                                              # twig scaffolding behind
            for x in (-1.1, 1.1):
                c.line(cx + x * s, cy + 0.4 * s, cx + x * 0.8 * s, cy - 1.5 * s, 3 * k, OUT)
                c.line(cx + x * s, cy + 0.4 * s, cx + x * 0.8 * s, cy - 1.5 * s, 2 * k, "#8d6e4a")
            c.line(cx - 0.9 * s, cy - 1.45 * s, cx + 0.9 * s, cy - 1.45 * s, 3 * k, OUT)
            c.line(cx - 0.9 * s, cy - 1.45 * s, cx + 0.9 * s, cy - 1.45 * s, 2 * k, "#8d6e4a")
            for x in (-0.7, -0.2, 0.3, 0.8):
                c.ellipse(cx + x * s, cy - 1.5 * s, 0.22 * s, 0.1 * s, "#6fbf4a", 0.3)
        side = [(-0.95, 0.35, 0.45)] + ([(0.95, 0.4, 0.5)] if level >= 2 else []) + ([(0.0, 0.75, 0.4)] if level >= 3 else [])
        mounds = [(0, -0.05, 0.85 + 0.12 * level)] + side
        for mx, my, mr in sorted(mounds, key=lambda m: m[1]):
            bx, by = cx + mx * s, cy + my * s + 0.3 * s
            top = by - mr * 1.6 * s
            opoly(c, [(bx - mr * s, by), (bx - 0.18 * mr * s, top), (bx + 0.18 * mr * s, top), (bx + mr * s, by)], sand, 1.5 * k)
            c.poly([(bx - mr * 0.9 * s, by - 2 * k), (bx - 0.15 * mr * s, top + 2 * k), (bx, top + 2 * k), (bx - 0.2 * mr * s, by - 2 * k)],
                   shade(sand, 1.12))
            c.ellipse(bx, by, mr * s, 0.18 * mr * s, shade(sand, 0.85))
            for hy in (0.35, 0.7):
                c.ellipse(bx + 0.1 * mr * s, top + hy * (by - top), 0.1 * mr * s, 0.07 * mr * s, "#3b2a20")
            for _ in range(6):
                c.circle(bx + rnd.uniform(-0.6, 0.6) * mr * s, by - rnd.uniform(0.1, 0.9) * (by - top), 0.025 * s, shade(sand, 0.7))
            if level == 3:
                for hy in (0.5, 0.85):                                              # chitin plates + nerve glow
                    oellipse(c, bx - 0.35 * mr * s, top + hy * (by - top), 0.14 * mr * s, 0.09 * mr * s, "#2e7d6b", 0.3, 1.2 * k)
                c.circle(bx + 0.4 * mr * s, top + 0.6 * (by - top), 0.06 * s, (1, 0.6, 0.8, 0.5))
                c.circle(bx + 0.4 * mr * s, top + 0.6 * (by - top), 0.03 * s, "#f8bbd0")
        for x, y in [(-0.4, 0.9), (0.6, 0.95), (1.2, 0.6), (-1.2, 0.8)]:            # ants carrying things
            draw_ant(c, cx + x * s, cy + y * s, 0.22 * k)
            c.rect(cx + x * s - 0.05 * s, cy + y * s - 0.22 * s, cx + x * s + 0.05 * s, cy + y * s - 0.14 * s, "#c8925a")
    return draw


def spider_spinner(c, cx, cy, s):
    k = s / 64
    grass(c, cx, cy + 0.2 * s, s, 1.5, 1.3)
    posts = [(-1.15, -0.9), (1.15, -0.9), (1.15, 0.95), (-1.15, 0.95)]
    tops = [(cx + x * s, cy + y * s - 1.3 * s) for x, y in posts]
    for (x, y), (tx, ty) in zip(posts[:2], tops[:2]):                               # back posts
        c.line(cx + x * s, cy + y * s, tx, ty, 5 * k, OUT); c.line(cx + x * s, cy + y * s, tx, ty, 3.4 * k, "#8d6e4a")
    hub = (cx, cy - 0.65 * s)
    anchors = tops + [(cx + x * s, cy + y * s) for x, y in posts]
    for ax, ay in anchors:                                                          # radial silk threads
        c.line(hub[0], hub[1], ax, ay, 1.3 * k, (1, 1, 1, 0.85))
    angles = sorted(math.atan2(ay - hub[1], ax - hub[0]) for ax, ay in anchors)
    for ring in range(1, 6):                                                        # spiral rings
        f = ring / 6
        pts = []
        for a in angles:
            ax, ay = next((x, y) for x, y in anchors if abs(math.atan2(y - hub[1], x - hub[0]) - a) < 1e-9)
            pts.append((hub[0] + (ax - hub[0]) * f, hub[1] + (ay - hub[1]) * f))
        for i in range(len(pts)):
            c.line(*pts[i], *pts[(i + 1) % len(pts)], 1.0 * k, (1, 1, 1, 0.75))
    for (x, y), (tx, ty) in zip(posts[2:], tops[2:]):                               # front posts
        c.line(cx + x * s, cy + y * s, tx, ty, 5 * k, OUT); c.line(cx + x * s, cy + y * s, tx, ty, 3.4 * k, "#a07a52")
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 0)]:                                   # top beams
        c.line(*tops[a], *tops[b], 4.5 * k, OUT); c.line(*tops[a], *tops[b], 3 * k, "#a07a52")
    draw_spider(c, hub[0], hub[1], 0.8 * k)
    for x in (-0.6, -0.1, 0.4):                                                     # silk spools in front
        oellipse(c, cx + x * s, cy + 1.05 * s, 0.18 * s, 0.14 * s, "#fbfbff", 0, 1.2 * k)
        c.ellipse(cx + x * s, cy + 1.05 * s, 0.07 * s, 0.05 * s, "#a1887f")


def glass_dome(c, cx, cy, s, r, base_col, inner):
    """Wooden base ring, plants/helix inside (inner callback), glass dome with ribs and highlight."""
    k = s / 64
    oellipse(c, cx, cy + 0.35 * r * s, r * s, 0.55 * r * s, shade(base_col, 0.75), 0, 2 * k)
    c.ellipse(cx, cy + 0.28 * r * s, r * s - 2 * k, 0.5 * r * s, base_col)
    c.ellipse(cx, cy + 0.28 * r * s, r * 0.85 * s, 0.4 * r * s, "#5f8f45")
    inner(c, cx, cy, s)
    c.ellipse(cx, cy - 0.25 * r * s, r * 0.95 * s, r * 0.85 * s, (0.75, 0.92, 1, 0.28))   # glass
    for f in (-0.6, -0.2, 0.2, 0.6):                                                # ribs
        x = cx + f * r * 0.95 * s
        h = r * 0.85 * s * math.sqrt(1 - f * f)
        c.line(x, cy + 0.3 * r * s * math.sqrt(1 - f * f), x, cy - 0.25 * r * s - h * 0.98, 1.6 * k, (0.55, 0.42, 0.28, 0.9))
    for i in range(30):
        a0, a1 = math.pi + math.pi * i / 30, math.pi + math.pi * (i + 1) / 30
        c.line(cx + math.cos(a0) * r * 0.95 * s, cy - 0.25 * r * s + math.sin(a0) * r * 0.85 * s,
               cx + math.cos(a1) * r * 0.95 * s, cy - 0.25 * r * s + math.sin(a1) * r * 0.85 * s, 2 * k, OUT)
    c.ellipse(cx - 0.45 * r * s, cy - 0.7 * r * s, 0.18 * r * s, 0.32 * r * s, (1, 1, 1, 0.45), 0.5)


def genetic_lab(c, cx, cy, s):
    k = s / 64

    def inner(c, cx, cy, s):
        for x in (-0.6, 0.6):
            leaves(c, cx + x * s, cy + 0.35 * s, 1.0 * k, "#4caf50", 3, 0.6, 22)
        helix(c, cx, cy - 1.15 * s, cx, cy + 0.25 * s, 0.22 * s, 1.5, 2.6 * k, "#2e7d32", "#c2185b")
    grass(c, cx, cy + 0.3 * s, s, 1.45, 1.1)
    glass_dome(c, cx, cy, s, 1.3, "#a07a52", inner)


def sequencer(c, cx, cy, s):
    k = s / 64

    def inner(c, cx, cy, s):
        c.circle(cx, cy - 0.9 * s, 1.1 * s, (0.6, 1, 0.8, 0.18))
        for x in (-1.3, -0.6, 0.7, 1.4):
            leaves(c, cx + x * s, cy + 0.6 * s, 1.3 * k, "#43a047", 4, 0.5, 26)
        helix(c, cx, cy - 2.0 * s, cx, cy + 0.4 * s, 0.4 * s, 2, 4 * k, "#7cc35a", "#f06292")
        for x, y in [(-0.9, -0.3), (1.0, -0.6), (-0.5, -1.4), (0.7, -1.7)]:
            c.circle(cx + x * s, cy + y * s, 0.08 * s, (0.8, 1, 0.6, 0.6))
    c.ellipse(cx, cy + 0.4 * s, 2.45 * s, 1.75 * s, (0.17, 0.11, 0.07, 0.6))
    c.ellipse(cx, cy + 0.4 * s, 2.4 * s, 1.7 * s, "#5f8f45")
    for i in range(12):                                                             # petal leaves around the base
        a = i * 2 * math.pi / 12
        oellipse(c, cx + math.cos(a) * 2.0 * s, cy + 0.5 * s + math.sin(a) * 1.3 * s, 0.45 * s, 0.22 * s,
                 "#7bc96f" if i % 2 else "#5fb35a", a, 1.5 * k)
    glass_dome(c, cx, cy, s, 2.1, "#8d6e4a", inner)


def mill(c, cx, cy, s):
    k = s / 64
    grass(c, cx, cy + 0.3 * s, s, 1.5, 1.25, "#8fb85a")
    house(c, cx - 0.95 * s, cx + 0.95 * s, cy + 1.1 * s, 1.3 * s, 0.75 * s, 0.7 * s, "#e8d9b5", "#a0522d")
    c.rect(cx - 0.22 * s, cy + 0.5 * s, cx + 0.22 * s, cy + 1.1 * s, "#7a5a3a")       # door
    hx, hy = cx, cy - 0.65 * s                                                      # sails
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2
        ex, ey = hx + math.cos(a) * 1.55 * s, hy + math.sin(a) * 1.55 * s
        c.line(hx, hy, ex, ey, 4 * k, OUT)
        c.line(hx, hy, ex, ey, 2.4 * k, "#8d6e4a")
        nx, ny = -math.sin(a), math.cos(a)
        p0 = (hx + math.cos(a) * 0.35 * s, hy + math.sin(a) * 0.35 * s)
        p1 = (ex, ey)
        opoly(c, [p0, p1, (p1[0] + nx * 0.32 * s, p1[1] + ny * 0.32 * s), (p0[0] + nx * 0.32 * s, p0[1] + ny * 0.32 * s)],
              "#f5efe0", 1.3 * k)
        for f in (0.35, 0.6, 0.85):
            q = (hx + math.cos(a) * 1.55 * f * s, hy + math.sin(a) * 1.55 * f * s)
            c.line(q[0], q[1], q[0] + nx * 0.32 * s, q[1] + ny * 0.32 * s, 1.0 * k, "#c8b48a")
    oellipse(c, hx, hy, 0.15 * s, 0.15 * s, "#6d4c41", 0, 1.5 * k)
    oellipse(c, cx + 1.15 * s, cy + 1.0 * s, 0.22 * s, 0.28 * s, "#f1e9d8", 0, 1.3 * k)   # flour sack
    draw_wheat(c, cx - 1.2 * s, cy + 0.7 * s, 0.6 * k)


def kitchen(c, cx, cy, s):
    k = s / 64
    grass(c, cx, cy + 0.3 * s, s, 1.5, 1.25, "#8fb85a")
    house(c, cx - 1.1 * s, cx + 1.1 * s, cy + 1.05 * s, 1.0 * s, 0.85 * s, 0.9 * s, "#efe2c4", "#c98a3e")
    opoly(c, [(cx + 0.45 * s, cy - 0.9 * s), (cx + 0.75 * s, cy - 0.9 * s), (cx + 0.75 * s, cy - 1.75 * s),
              (cx + 0.45 * s, cy - 1.75 * s)], "#cfd8c4", 1.5 * k)                  # biocement chimney
    for i, (x, y, r) in enumerate([(0.62, -1.95, 0.14), (0.72, -2.2, 0.18), (0.6, -2.5, 0.22)]):
        c.circle(cx + x * s, cy + y * s, r * s, (0.95, 0.95, 0.95, 0.75 - i * 0.15))
    for x in (-0.6, 0.6):                                                           # warm windows
        c.rect(cx + x * s - 0.22 * s, cy + 0.3 * s, cx + x * s + 0.22 * s, cy + 0.65 * s, OUT)
        c.rect(cx + x * s - 0.19 * s, cy + 0.33 * s, cx + x * s + 0.19 * s, cy + 0.62 * s, "#ffd36a")
        c.line(cx + x * s, cy + 0.33 * s, cx + x * s, cy + 0.62 * s, 1.2 * k, "#8d6e4a")
    c.rect(cx - 0.18 * s, cy + 0.45 * s, cx + 0.18 * s, cy + 1.05 * s, "#7a5a3a")
    draw_pumpkin(c, cx + 1.15 * s, cy + 1.0 * s, 0.6 * k)
    draw_carrot(c, cx - 1.2 * s, cy + 0.85 * s, 0.5 * k)


def chicken_coop(c, cx, cy, s):
    k = s / 64
    grass(c, cx, cy + 0.2 * s, s, 1.5, 1.3, "#9cc35a")
    c.ellipse(cx + 0.5 * s, cy + 0.6 * s, 0.9 * s, 0.6 * s, "#c8a46a")              # scratched run
    for x in (-1.0, -0.2):                                                          # stilts
        c.line(cx + x * s, cy + 0.2 * s, cx + x * s, cy - 0.2 * s, 4 * k, OUT)
    house(c, cx - 1.15 * s, cx - 0.05 * s, cy + 0.0 * s, 0.75 * s, 0.5 * s, 0.6 * s, "#c8925a", "#8d5a2b")
    c.circle(cx - 0.6 * s, cy - 0.45 * s, 0.13 * s, "#3b2a20")                       # entrance
    c.line(cx - 0.45 * s, cy - 0.05 * s, cx + 0.2 * s, cy + 0.45 * s, 4 * k, OUT)   # ramp
    c.line(cx - 0.45 * s, cy - 0.05 * s, cx + 0.2 * s, cy + 0.45 * s, 2.5 * k, "#a07a52")
    fence(c, cx - 0.3 * s, cy - 0.6 * s, cx + 1.35 * s, cy + 1.2 * s, s)
    for x, y in [(0.45, 0.35), (1.0, 0.75), (0.3, 1.0)]:
        draw_chicken(c, cx + x * s, cy + y * s, 0.42 * k)
    draw_egg(c, cx - 0.8 * s, cy + 0.9 * s, 0.3 * k)


def barn(c, cx, cy, s):
    k = s / 64
    grass(c, cx, cy + 0.3 * s, s, 1.5, 1.25, "#8fb85a")
    house(c, cx - 1.15 * s, cx + 1.15 * s, cy + 1.0 * s, 1.15 * s, 0.85 * s, 0.75 * s, "#c0473a", "#5d4037")
    c.rect(cx - 0.5 * s, cy + 0.05 * s, cx + 0.5 * s, cy + 1.0 * s, OUT)             # big door with white X
    c.rect(cx - 0.45 * s, cy + 0.1 * s, cx + 0.45 * s, cy + 1.0 * s, "#a83a2f")
    for a, b in [((-0.45, 0.1), (0.45, 1.0)), ((0.45, 0.1), (-0.45, 1.0))]:
        c.line(cx + a[0] * s, cy + a[1] * s, cx + b[0] * s, cy + b[1] * s, 2.5 * k, "#f5f0e6")
    c.rect(cx - 0.45 * s, cy + 0.1 * s, cx + 0.45 * s, cy + 0.16 * s, "#f5f0e6")
    c.rect(cx - 0.17 * s, cy - 0.55 * s, cx + 0.17 * s, cy - 0.25 * s, "#f5f0e6")    # hay loft
    c.rect(cx - 0.13 * s, cy - 0.51 * s, cx + 0.13 * s, cy - 0.29 * s, "#e3c25a")
    oellipse(c, cx + 1.2 * s, cy + 1.05 * s, 0.32 * s, 0.22 * s, "#e3c25a", 0, 1.3 * k)  # hay bale
    draw_cow(c, cx - 1.05 * s, cy + 0.95 * s, 0.5 * k)


def sheep_pen(c, cx, cy, s):
    k = s / 64
    grass(c, cx, cy + 0.2 * s, s, 1.5, 1.3, "#8cc063")
    opoly(c, [(cx - 1.2 * s, cy - 0.5 * s), (cx - 1.2 * s, cy - 1.3 * s), (cx + 0.2 * s, cy - 1.3 * s),
              (cx + 0.2 * s, cy - 0.5 * s)], "#a07a52", 1.5 * k)                     # lean-to shelter
    opoly(c, [(cx - 1.3 * s, cy - 1.2 * s), (cx + 0.3 * s, cy - 1.2 * s), (cx + 0.3 * s, cy - 1.65 * s),
              (cx - 1.3 * s, cy - 1.65 * s)], "#7cb342", 1.5 * k)
    c.rect(cx - 1.1 * s, cy - 1.15 * s, cx + 0.1 * s, cy - 0.55 * s, "#4a3420")
    fence(c, cx - 1.35 * s, cy - 0.45 * s, cx + 1.35 * s, cy + 1.25 * s, s)
    for x, y in [(-0.75, 0.2), (0.55, 0.1), (-0.05, 0.85)]:
        draw_sheep(c, cx + x * s, cy + y * s, 0.55 * k)
    oellipse(c, cx + 1.0 * s, cy - 0.85 * s, 0.25 * s, 0.17 * s, "#e3c25a", 0, 1.2 * k)


def hive(c, cx, cy, s):
    import random
    rnd = random.Random(8)
    k = s / 64
    opoly(c, [(cx - 1.85 * s, cy - 1.4 * s), (cx + 1.85 * s, cy - 1.4 * s), (cx + 1.85 * s, cy + 1.85 * s),
              (cx - 1.85 * s, cy + 1.85 * s)], "#6b4f33", 2 * k)                    # wooden deck (front edge)
    c.rect(cx - 1.8 * s, cy - 1.75 * s, cx + 1.8 * s, cy + 1.6 * s, OUT)
    c.rect(cx - 1.77 * s, cy - 1.72 * s, cx + 1.77 * s, cy + 1.57 * s, "#a07a52")
    for i in range(1, 10):
        y = cy - 1.72 * s + i * 3.29 * s / 10
        c.line(cx - 1.77 * s, y, cx + 1.77 * s, y, 1.2 * k, "#7a5a3a")
    for hx, hy in [(-1.35, -1.25), (1.35, -1.25), (-1.35, 1.15), (1.35, 1.15)]:      # honeycomb corners
        for dx, dy in [(0, 0), (0.17, 0.1), (-0.17, 0.1), (0, 0.2)]:
            pts = [(cx + (hx + dx) * s + math.cos(a) * 0.11 * s, cy + (hy + dy) * s + math.sin(a) * 0.09 * s)
                   for a in [i * math.pi / 3 for i in range(6)]]
            opoly(c, pts, "#f6b93b", 1.0 * k)
    base_y, top_y = cy + 0.95 * s, cy - 1.75 * s                                    # straw skep (coiled bands)
    n = 9
    for i in range(n):
        f = i / n
        y = base_y - (base_y - top_y) * f
        r = 1.35 * math.sqrt(max(0.02, 1 - f ** 1.6)) * s
        oellipse(c, cx, y, r, 0.33 * s, "#d9a441" if i % 2 else "#c08a2c", 0, 1.5 * k)
        c.ellipse(cx - r * 0.3, y - 0.08 * s, r * 0.45, 0.1 * s, "#ecc56a")
    opoly(c, [(cx - 0.32 * s, base_y + 0.1 * s), (cx - 0.32 * s, base_y - 0.3 * s), (cx, base_y - 0.48 * s),
              (cx + 0.32 * s, base_y - 0.3 * s), (cx + 0.32 * s, base_y + 0.1 * s)], "#3b2a20", 1.5 * k)  # entrance
    for x, y in [(-1.1, -0.9), (1.2, -0.4), (0.7, 1.3), (-0.8, 1.35), (1.5, 0.6)]:
        draw_bee(c, cx + x * s, cy + y * s, 0.3 * k)
    for _ in range(14):
        c.circle(cx + rnd.uniform(-1.6, 1.6) * s, cy + rnd.uniform(-1.6, 1.4) * s, 0.02 * s, "#fff3b0")


def building(ent, icons, name, draw, shadow, w, h, center_y):
    """Entity sprite w x h px (64 px per tile, building centre at x=w/2, y=center_y), its shadow and a 64px icon."""
    for path, fn in ((name + ".png", draw), (name + "-shadow.png", shadow)):
        c = Canvas(w, h, ss=2)
        fn(c, w / 2, center_y, 64)
        c.save(os.path.join(ent, path))
    s = 62 * 64 / max(w, h)                         # whole sprite fits the icon
    c = Canvas(64, 64)
    draw(c, 32, 32 + (center_y - h / 2) / 64 * s, s)
    c.save(os.path.join(icons, name + ".png"))


def main():
    mod = sys.argv[1]
    icons = os.path.join(mod, "graphics", "icons")
    ent = os.path.join(mod, "graphics", "entity")

    crops = {
        "carrot": (draw_carrot, "#f28a1e"),
        "potato": (draw_potato, "#a07a45"),
        "wheat": (draw_wheat, "#e0b83c"),
        "tomato": (draw_tomato, "#e53935"),
        "pumpkin": (draw_pumpkin, "#e07b16"),
        "flax": (draw_flax, "#6fa8dc"),
    }
    simple = {
        "garden-soil": draw_soil, "hay": draw_hay, "egg": draw_egg, "feather": draw_feather,
        "milk": draw_milk, "wool": draw_wool, "flour": draw_flour, "bread": draw_bread,
        "cheese": draw_cheese, "pumpkin-pie": draw_pie, "vegetable-soup": draw_soup,
        "chicken": draw_chicken, "cow": draw_cow, "sheep": draw_sheep, "farm-pack": draw_farm_pack,
        "tower-badge": draw_tower_badge,
        "flax-fiber": draw_fiber, "plank": draw_plank, "resin": draw_resin, "limestone": draw_limestone,
        "dna-sample": draw_dna_sample, "genome-sequence": draw_genome_sequence, "silk": draw_silk,
        "ant": draw_ant, "spider": draw_spider,
        "mushroom": draw_mushroom, "mycelium": draw_mycelium, "nerve-tissue": draw_nerve_tissue,
        "chitin": draw_chitin, "seedling": draw_seedling,
        "bacteria-culture": draw_bacteria_culture, "crispr-kit": draw_crispr_kit, "bee": draw_bee,
        "algae": draw_algae, "reed": draw_reed, "lotus": draw_lotus, "plant-oil": draw_plant_oil,
        "synthetic-genome": draw_synthetic_genome,
        "biocement": draw_biocement, "sugar": draw_sugar, "digester-badge": draw_digester_badge,
    }
    for name, (fn, tint) in crops.items():
        c = Canvas(64, 64); fn(c); c.save(os.path.join(icons, name + ".png"))
        c = Canvas(64, 64); draw_seed_packet(c, fn, tint); c.save(os.path.join(icons, name + "-seeds.png"))
        crop_sprite(plant_draw(name), os.path.join(ent, name + "-plant.png"), 0.8)
    for name, fn in simple.items():
        c = Canvas(64, 64); fn(c); c.save(os.path.join(icons, name + ".png"))
    mound(os.path.join(ent, "growth-mound.png"))
    big_sprout(os.path.join(ent, "building-sprout.png"))
    # Buildings: name, draw, shadow, sprite w, h, building centre row (sizes must match prototypes/looks.lua)
    S3 = (224, 288, 176)
    for name, draw, shadow, size in [
        ("algae-farm", algae_farm, algae_farm_shadow, (224, 224, 112)),
        ("reed-filter", reed_filter, reed_filter_shadow, (256, 320, 200)),
        ("lotus-reactor", lotus_reactor, lotus_reactor_shadow, (384, 384, 200)),
        ("digester", digester, blob_shadow(1.3, 1.0), S3),
        ("fermentation-chamber", fermentation_chamber, blob_shadow(1.2, 0.9, tall=1.2), S3),
        ("mushroom-farm", mushroom_farm, blob_shadow(1.35, 1.1), S3),
        ("ant-workshop-1", ant_workshop(1), blob_shadow(1.3, 0.9, tall=1.0), S3),
        ("ant-workshop-2", ant_workshop(2), blob_shadow(1.35, 0.95, tall=1.3), S3),
        ("ant-workshop-3", ant_workshop(3), blob_shadow(1.4, 1.0, tall=1.4), S3),
        ("spider-spinner", spider_spinner, blob_shadow(1.3, 1.1, tall=1.0), S3),
        ("mill", mill, blob_shadow(1.2, 0.9, tall=1.6), S3),
        ("kitchen", kitchen, blob_shadow(1.3, 0.9, tall=1.3), S3),
        ("chicken-coop", chicken_coop, blob_shadow(1.35, 1.1, tall=0.6), S3),
        ("barn", barn, blob_shadow(1.3, 0.9, tall=1.5), S3),
        ("sheep-pen", sheep_pen, blob_shadow(1.4, 1.1, tall=0.5), S3),
        ("genetic-lab", genetic_lab, blob_shadow(1.3, 1.0, tall=1.2), S3),
        ("sequencer", sequencer, blob_shadow(2.3, 1.7, tall=2.0), (384, 448, 256)),
        ("hive", hive, blob_shadow(1.9, 1.7, tall=1.5), (288, 352, 208)),
    ]:
        building(ent, icons, name, draw, shadow, *size)
    print("graphics written to", mod)


if __name__ == "__main__":
    main()
