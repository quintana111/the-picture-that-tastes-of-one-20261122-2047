#!/usr/bin/env python3
"""the-picture-that-tastes-of-one-20261122-2047 — one ingredient: ramen.

A steaming bowl of ramen, drawn entirely in code with PIL + numpy.
Deterministic: fixed geometry, no randomness, no timestamps, no network.
Reads nothing from disk except the Python interpreter; writes entry.png
to $OUT (default: entry.png next to this file).

Subject: one bowl of ramen — glossy golden broth, jammy soft egg,
chili-oil swirl, spring-onion rings, chashu, nori, and chopsticks
lifting a tangle of noodles. Warm light, dark warm background, no text.
"""
import hashlib
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1024, 1024


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def radial_bg(size, centre, inner, outer):
    """Vertical+radial warm gradient background, numpy, deterministic."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    dx = (xx - centre[0]) / (w * 0.62)
    dy = (yy - centre[1]) / (h * 0.62)
    d = np.clip(np.sqrt(dx * dx + dy * dy), 0.0, 1.0)
    d = d * d * (3.0 - 2.0 * d)  # smoothstep
    arr = np.zeros((h, w, 3), dtype=np.float64)
    for i in range(3):
        arr[:, :, i] = inner[i] + (outer[i] - inner[i]) * d
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def ellipse_gradient(size, box, inner, outer):
    """Soft radial gradient inside an ellipse, on its own RGBA layer."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    dx = (xx - w / 2.0) / (w / 2.0)
    dy = (yy - h / 2.0) / (h / 2.0)
    d = np.clip(np.sqrt(dx * dx + dy * dy), 0.0, 1.0)
    d = d * d * (3.0 - 2.0 * d)
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    for i in range(3):
        arr[:, :, i] = (inner[i] + (outer[i] - inner[i]) * d).astype(np.uint8)
    arr[:, :, 3] = 255
    small = Image.fromarray(arr, "RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, w - 1, h - 1], fill=255)
    layer.paste(small, (x0, y0), mask)
    return layer


def wavy_noodle(draw, x0, y0, x1, y1, amp, waves, color, width):
    """One wavy noodle strand as a polyline of a sine wave."""
    pts = []
    n = 90
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + amp * np.sin(t * waves * 2.0 * np.pi)
        pts.append((x, y))
    draw.line(pts, fill=color, width=width, joint="curve")


def steam_wisp(layer_draw, cx, top, bottom, sway, width, alpha):
    """A single rising steam wisp: an S-curved thick translucent line."""
    pts = []
    n = 60
    for i in range(n + 1):
        t = i / n
        y = bottom - (bottom - top) * t
        x = cx + sway * np.sin(t * 2.6 * np.pi + 0.6)
        pts.append((x, y))
    layer_draw.line(pts, fill=(255, 250, 240, alpha), width=width, joint="curve")


def ring(draw, cx, cy, r, fill, hole, outline=None):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline,
                 width=2 if outline else 1)
    draw.ellipse([cx - hole, cy - hole, cx + hole, cy + hole],
                 fill=(0, 0, 0, 0))


def render():
    # ---- background: dark warm room, glowing behind the bowl ----
    img = radial_bg((W, H), (512, 430), (74, 44, 22), (16, 10, 6))
    d = ImageDraw.Draw(img, "RGBA")

    # warm halo behind the bowl
    halo = ellipse_gradient((W, H), (150, 60, 874, 860), (150, 92, 40),
                            (16, 10, 6))
    halo = halo.filter(ImageFilter.GaussianBlur(90))
    img.paste(halo, (0, 0), halo)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- wooden table, lower third ----
    table = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(table)
    for i, y in enumerate(range(700, H, 1)):
        t = (y - 700) / (H - 700)
        td.line([(0, y), (W, y)], fill=lerp((96, 58, 30), (52, 30, 16), t))
    # table grain: long soft darker streaks
    for gy, gw, ga in [(742, 3, 60), (800, 2, 50), (856, 4, 55), (920, 2, 45),
                       (968, 3, 50), (770, 2, 40), (890, 2, 40)]:
        td.line([(0, gy), (W, gy)], fill=(30, 17, 9, ga), width=gw)
    # table edge highlight where the light hits
    td.line([(0, 700), (W, 700)], fill=(190, 120, 60, 110), width=3)
    img.paste(table, (0, 0), table)
    d = ImageDraw.Draw(img, "RGBA")

    # soft shadow under the bowl
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([150, 800, 874, 900], fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26))
    img.paste(shadow, (0, 0), shadow)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- bowl body: deep lacquered bowl, red rim ----
    # outer body (front face)
    d.pieslice([172, 540, 852, 860], start=0, end=180, fill=(24, 16, 14))
    # body shading: darker at the bottom, warm sheen on the left
    body_shade = ellipse_gradient((W, H), (172, 540, 852, 860),
                                  (58, 34, 26), (14, 8, 7))
    img.paste(body_shade, (0, 0), body_shade)
    d = ImageDraw.Draw(img, "RGBA")
    d.pieslice([172, 540, 852, 860], start=0, end=180, outline=(8, 5, 4), width=3)
    # glossy vertical sheen on the bowl front
    sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.ellipse([250, 620, 330, 820], fill=(255, 190, 120, 26))
    sd.ellipse([700, 620, 760, 810], fill=(255, 190, 120, 14))
    sheen = sheen.filter(ImageFilter.GaussianBlur(18))
    img.paste(sheen, (0, 0), sheen)
    d = ImageDraw.Draw(img, "RGBA")
    # foot ring at the base
    d.pieslice([430, 800, 594, 860], start=0, end=180, fill=(10, 6, 5))
    d.arc([430, 800, 594, 860], start=0, end=180, fill=(120, 60, 30), width=3)

    # rim: thick red lacquer ring around the broth
    d.ellipse([168, 468, 856, 656], fill=(176, 38, 26))
    d.ellipse([188, 482, 836, 644], fill=(140, 26, 18))
    # rim highlight (light from upper left)
    d.arc([180, 474, 844, 650], start=180, end=330, fill=(255, 120, 80), width=7)
    d.arc([180, 474, 844, 650], start=10, end=90, fill=(90, 16, 10), width=5)

    # ---- broth: golden, glossy, with chili-oil swirls ----
    broth = ellipse_gradient((W, H), (196, 486, 828, 640),
                             (238, 164, 62), (168, 96, 28))
    img.paste(broth, (0, 0), broth)
    d = ImageDraw.Draw(img, "RGBA")
    # chili-oil swirls: deep red translucent ribbons on the broth
    oil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(oil)
    for (cx, cy, rx, ry, a0, a1, wd) in [
            (330, 560, 90, 30, 200, 330, 10), (620, 548, 110, 28, 20, 160, 9),
            (512, 600, 120, 26, 150, 300, 8), (430, 534, 70, 22, 300, 120, 7),
            (700, 606, 80, 24, 250, 60, 8)]:
        od.arc([cx - rx, cy - ry, cx + rx, cy + ry], start=a0, end=a1,
               fill=(178, 40, 12, 150), width=wd)
    oil = oil.filter(ImageFilter.GaussianBlur(4))
    img.paste(oil, (0, 0), oil)
    d = ImageDraw.Draw(img, "RGBA")
    # broth gloss: big soft specular highlight
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.ellipse([250, 494, 470, 542], fill=(255, 230, 170, 110))
    gd.ellipse([560, 604, 700, 630], fill=(255, 210, 140, 60))
    gloss = gloss.filter(ImageFilter.GaussianBlur(10))
    img.paste(gloss, (0, 0), gloss)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- noodles: a tangle of wavy strands across the broth ----
    noodle_cols = [(246, 205, 120), (232, 186, 96), (252, 220, 150),
                   (222, 172, 84)]
    strands = [
        (250, 560, 760, 556, 9, 5), (260, 580, 740, 576, 8, 6),
        (280, 540, 720, 544, 10, 4), (300, 596, 700, 592, 7, 6),
        (240, 572, 780, 568, 11, 5), (320, 548, 680, 552, 8, 5),
        (270, 588, 730, 584, 9, 7), (350, 536, 650, 540, 7, 4),
    ]
    for i, (x0, y0, x1, y1, amp, waves) in enumerate(strands):
        wavy_noodle(d, x0, y0, x1, y1, amp, waves, (150, 100, 40), 9)
        wavy_noodle(d, x0, y0 - 2, x1, y1 - 2, amp, waves,
                    noodle_cols[i % len(noodle_cols)], 6)

    # ---- nori sheet standing at the back ----
    d.rounded_rectangle([610, 452, 700, 542], radius=10,
                        fill=(18, 38, 22), outline=(8, 20, 12), width=3)
    d.line([(626, 460), (626, 534)], fill=(52, 96, 58, 160), width=2)
    d.line([(648, 460), (648, 534)], fill=(52, 96, 58, 140), width=2)
    d.line([(672, 460), (672, 534)], fill=(52, 96, 58, 120), width=2)

    # ---- chashu slices: pink rounds with a darker seared rim ----
    for (cx, cy, r) in [(300, 570, 52), (392, 588, 46)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 118, 96),
                  outline=(140, 70, 56), width=4)
        d.ellipse([cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12],
                  fill=(222, 158, 132))
        d.ellipse([cx - 14, cy - 10, cx + 14, cy + 10], fill=(240, 190, 165))
        d.ellipse([cx - r + 6, cy - r + 4, cx - r + 22, cy - r + 16],
                  fill=(255, 220, 200, 160))

    # ---- soft egg halves: white with jammy orange yolk ----
    for (cx, cy) in [(668, 566), (742, 586)]:
        # white
        d.ellipse([cx - 46, cy - 34, cx + 46, cy + 34], fill=(248, 240, 222),
                  outline=(214, 196, 170), width=2)
        # yolk: deep orange, glossy
        d.ellipse([cx - 26, cy - 22, cx + 26, cy + 22], fill=(240, 138, 26),
                  outline=(200, 96, 14), width=3)
        d.ellipse([cx - 22, cy - 18, cx + 22, cy + 18], fill=(248, 164, 48))
        # jammy centre + gloss dot
        d.ellipse([cx - 12, cy - 10, cx + 12, cy + 10], fill=(252, 186, 80))
        d.ellipse([cx - 18, cy - 18, cx - 6, cy - 8],
                  fill=(255, 226, 160, 220))

    # ---- spring-onion rings scattered over the broth ----
    onions = [(350, 545, 11), (470, 540, 10), (560, 600, 11), (470, 596, 9),
              (620, 604, 10), (300, 596, 9), (530, 548, 10), (700, 556, 9),
              (410, 566, 8), (580, 566, 8)]
    for (cx, cy, r) in onions:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(52, 138, 58),
                  outline=(28, 92, 34), width=2)
        d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
                  fill=(150, 210, 110))
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(220, 245, 190))

    # ---- chopsticks lifting noodles, upper right ----
    # lifted noodle tangle hanging from the chopsticks
    lift = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lift)
    for i, (x0, y0, x1, y1, amp, waves) in enumerate([
            (700, 420, 630, 566, 16, 3), (726, 416, 660, 562, 14, 3),
            (752, 422, 696, 558, 16, 4), (678, 428, 612, 562, 13, 3),
            (714, 412, 646, 554, 15, 4)]):
        wavy_noodle(ld, x0, y0, x1, y1, amp, waves, (150, 100, 40), 9)
        wavy_noodle(ld, x0, y0 - 2, x1, y1 - 2, amp, waves,
                    noodle_cols[i % len(noodle_cols)], 6)
    img.paste(lift, (0, 0), lift)
    d = ImageDraw.Draw(img, "RGBA")
    # chopstick tips pinching the noodles, then the sticks up-right
    for (dx, dy) in [(0, 0), (28, -14)]:
        d.line([(690 + dx, 436 + dy), (930 + dx, 286 + dy)],
               fill=(96, 52, 26), width=14)
        d.line([(690 + dx, 436 + dy), (930 + dx, 286 + dy)],
               fill=(150, 88, 44), width=7)
        d.line([(690 + dx, 436 + dy), (760 + dx, 392 + dy)],
               fill=(70, 38, 18), width=14)
    # small broth drip falling from the lifted noodles
    d.ellipse([636, 580, 652, 596], fill=(238, 164, 62))

    # ---- steam: soft white wisps rising above the bowl ----
    steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for (cx, top, bottom, sway, wd, al) in [
            (380, 300, 520, 26, 26, 70), (470, 260, 520, 30, 30, 85),
            (560, 280, 520, 24, 26, 75), (650, 310, 520, 28, 24, 65),
            (300, 340, 520, 20, 20, 55), (720, 350, 510, 18, 20, 50)]:
        steam_wisp(sd, cx, top, bottom, sway, wd, al)
    steam = steam.filter(ImageFilter.GaussianBlur(14))
    img.paste(steam, (0, 0), steam)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- vignette: darken the corners so the bowl pops ----
    vg = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vg)
    vd.ellipse([-220, -180, W + 220, H + 180], fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(120))
    black = Image.new("RGB", (W, H), (8, 4, 2))
    img = Image.composite(img, black, vg)
    return img


if __name__ == "__main__":
    out = os.environ.get(
        "OUT",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"),
    )
    img = render()
    img.save(out, "PNG", optimize=True)
    data = open(out, "rb").read()
    print(f"{out} {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
