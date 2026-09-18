#!/usr/bin/env python3
"""BioVirus — still plates for the animated backgrounds.

Each plate is the static base of one fx/scenes/*.qml scene: it is what the
background switcher thumbnails, and what you are left looking at when
`biovirus off` kills the motion. So the furniture here is deliberately dead
still — the scene supplies everything that moves.

Everything is drawn twice: once sharp, once blurred and ADDED. Compositing a
blurred copy on top of near-black only dilutes it; adding it is what actually
puts light on the plate.

Re-render:  python3 make-plates.py [--colors <colors.toml>] [--prefix <name>] [outdir]
Default outdir is ../backgrounds relative to this file.
"""

import os
import re
import sys
from math import cos, hypot, pi, sin
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 2880, 1800

# Defaults are the biovirus palette; --colors <colors.toml> swaps them so the
# same plates can be rendered for a sibling theme (biovirus-contagion et al.)
# without forking this file.
BG = (0x04, 0x08, 0x0A)
BG_DARK = (0x01, 0x03, 0x04)
GRID = (0x0B, 0x1A, 0x14)
GREEN = (0x4B, 0xFF, 0xA5)
MUTED = (0x2E, 0x8F, 0x63)
CYAN = (0x4B, 0xE0, 0xFF)
RED = (0xFF, 0x4D, 0x5E)
ORANGE = (0xFF, 0x8F, 0x4D)

# colors.toml key -> module-level constant.
COLOR_KEYS = {
    "background": "BG",
    "darker_background": "BG_DARK",
    "lighter_background": "GRID",
    "accent": "GREEN",
    "muted": "MUTED",
    "cyan": "CYAN",
    "red": "RED",
    "orange": "ORANGE",
}


def load_colors(path):
    """Override the palette from an Omarchy colors.toml."""
    pat = re.compile(r'^\s*([a-z_]+)\s*=\s*"#([0-9a-fA-F]{6})"')
    found = {}
    with open(path) as fh:
        for line in fh:
            m = pat.match(line)
            if m and m.group(1) in COLOR_KEYS:
                h = m.group(2)
                found[COLOR_KEYS[m.group(1)]] = (
                    int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    globals().update(found)
    print(f"palette from {path}: {', '.join(sorted(found))}")

FONT_CANDIDATES = [
    "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf",
    "/usr/share/fonts/ttf-ia-writer/iAWriterMonoS-Regular.ttf",
    "/usr/share/fonts/noto/NotoSansMono-Light.ttf",
    "/usr/share/fonts/liberation/LiberationMono-Regular.ttf",
]


def font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rgba(color, alpha):
    return (color[0], color[1], color[2], int(alpha))


def ground(focus=(0.5, 0.5), spread=0.85):
    """Radial fade from BG at the focus down to BG_DARK at the corners.

    Built at 96x60 and upscaled: a per-pixel loop over 5.2M pixels is pointless
    when the gradient has no detail to lose.
    """
    sw, sh = 96, 60
    small = Image.new("RGB", (sw, sh))
    px = small.load()
    fx, fy = focus[0] * sw, focus[1] * sh
    far = hypot(max(fx, sw - fx), max(fy, sh - fy)) * spread
    for y in range(sh):
        for x in range(sw):
            t = min(1.0, hypot(x - fx, y - fy) / far)
            t = t * t * (3 - 2 * t)  # smoothstep, so the falloff has no seam
            px[x, y] = tuple(int(BG[i] + (BG_DARK[i] - BG[i]) * t) for i in range(3))
    return small.resize((W, H), Image.BICUBIC).convert("RGBA")


def ink(img, draw_fn, bloom=20, gain=0.75):
    """Draw sharp, then add a blurred copy as light. Returns a new image."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    out = Image.alpha_composite(img, layer)
    if bloom:
        blurred = layer.filter(ImageFilter.GaussianBlur(bloom))
        alpha = blurred.getchannel("A").point(lambda v: int(v * gain))
        # Premultiply so the add carries the shape's own falloff.
        lit = Image.composite(blurred.convert("RGB"),
                              Image.new("RGB", (W, H), (0, 0, 0)), alpha)
        out = ImageChops.add(out.convert("RGB"), lit).convert("RGBA")
    return out


def haze(img, draw_fn, blur, gain=0.55):
    """Soft light only — no sharp pass. Depth blobs and background glow."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    blurred = layer.filter(ImageFilter.GaussianBlur(blur))
    alpha = blurred.getchannel("A").point(lambda v: int(v * gain))
    lit = Image.composite(blurred.convert("RGB"),
                          Image.new("RGB", (W, H), (0, 0, 0)), alpha)
    return ImageChops.add(img.convert("RGB"), lit).convert("RGBA")


def grid_layer(step=120, tick=9, alpha=150):
    """The crosshair lattice carried over from biovirus-containment."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step, H, step):
        for x in range(step, W, step):
            d.line([(x - tick, y), (x + tick, y)], fill=rgba(GRID, alpha))
            d.line([(x, y - tick), (x, y + tick)], fill=rgba(GRID, alpha))
    return layer


def scanline_layer(spacing=3, alpha=18):
    """A hint of CRT grid so an FX-off desktop still reads as BioVirus."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, H, spacing):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    return layer


def vignette(strength=0.38):
    sw, sh = 96, 60
    small = Image.new("L", (sw, sh))
    px = small.load()
    cx, cy = sw / 2, sh / 2
    far = hypot(cx, cy)
    for y in range(sh):
        for x in range(sw):
            t = min(1.0, hypot(x - cx, y - cy) / far)
            px[x, y] = int(255 * (1 - strength * t * t))
    return small.resize((W, H), Image.BICUBIC).convert("RGB")


def ring(d, cx, cy, r, color, alpha, width=3):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba(color, alpha), width=width)


PREFIX = "biovirus"


def finish(img, name, outdir):
    name = f"{PREFIX}-{name}"
    img = Image.alpha_composite(img, scanline_layer())
    img = ImageChops.multiply(img.convert("RGB"), vignette())
    path = os.path.join(outdir, name)
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path}")


# ── plates ──────────────────────────────────────────────────────────────────


def plate_virions(outdir):
    """Out-of-focus capsids and one measured reference specimen."""
    img = ground(focus=(0.62, 0.44))
    img = Image.alpha_composite(img, grid_layer())

    # Depth: big soft silhouettes sit behind everything the scene will draw.
    def blobs(d):
        for cx, cy, r, a in [
            (0.20 * W, 0.68 * H, 300, 70),
            (0.80 * W, 0.28 * H, 380, 55),
            (0.50 * W, 0.88 * H, 240, 48),
        ]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(MUTED, a))

    img = haze(img, blobs, 110, gain=0.5)

    # The one crisp piece of furniture: a spiked reference capsid, unmoving.
    def reference(d):
        cx, cy, r = 0.62 * W, 0.44 * H, 300
        ring(d, cx, cy, r, GREEN, 120, 3)
        ring(d, cx, cy, r * 0.70, MUTED, 90, 2)
        ring(d, cx, cy, r * 0.34, MUTED, 60, 2)
        for i in range(64):
            a = 2 * pi * i / 64
            x0, y0 = cx + cos(a) * r, cy + sin(a) * r
            x1, y1 = cx + cos(a) * (r + 30), cy + sin(a) * (r + 30)
            d.line([(x0, y0), (x1, y1)], fill=rgba(GREEN, 95), width=3)
            d.ellipse([x1 - 5, y1 - 5, x1 + 5, y1 + 5], fill=rgba(GREEN, 110))

    img = ink(img, reference, bloom=28, gain=0.85)

    def furniture(d):
        x, y = 0.08 * W, 0.90 * H
        d.line([(x, y), (x + 300, y)], fill=rgba(MUTED, 170), width=3)
        for tx in (x, x + 150, x + 300):
            d.line([(tx, y - 10), (tx, y + 10)], fill=rgba(MUTED, 170), width=3)
        d.text((x, y + 20), "200 nm", font=font(28), fill=rgba(MUTED, 190))
        d.text((x, 0.06 * H), "SPECIMEN  //  TEM 120 kV", font=font(30),
               fill=rgba(MUTED, 160))

    img = ink(img, furniture, bloom=10, gain=0.5)
    finish(img, "virions.png", outdir)


def plate_mitosis(outdir):
    """A colony plate: quiet cells, one caught mid-pinch."""
    img = ground(focus=(0.40, 0.52), spread=0.95)
    img = Image.alpha_composite(img, grid_layer(step=160, tick=7, alpha=120))

    def dish(d):
        cx, cy = 0.40 * W, 0.52 * H
        ring(d, cx, cy, 760, MUTED, 70, 3)
        ring(d, cx, cy, 720, MUTED, 40, 2)

    img = ink(img, dish, bloom=22, gain=0.6)

    cells = [
        (0.28, 0.34, 150), (0.58, 0.28, 105), (0.20, 0.68, 120),
        (0.64, 0.70, 135), (0.45, 0.84, 85), (0.75, 0.48, 70),
    ]

    def bodies(d):
        for fx, fy, r in cells:
            cx, cy = fx * W, fy * H
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(MUTED, 26))

    img = haze(img, bodies, 60, gain=0.55)

    def membranes(d):
        for fx, fy, r in cells:
            cx, cy = fx * W, fy * H
            ring(d, cx, cy, r, GREEN, 95, 3)
            n = r * 0.30
            d.ellipse([cx - n, cy - n, cx + n, cy + n], fill=rgba(MUTED, 70))
        # The pinch: two lobes that have not quite let go of each other. Kept
        # dimmer than the printed cells around it — Mitosis.qml animates real
        # divisions on top, and a bright frozen one competes with them.
        cx, cy, r = 0.40 * W, 0.50 * H, 175
        for dx in (-r * 0.60, r * 0.60):
            ring(d, cx + dx, cy, r, GREEN, 70, 2)
            n = r * 0.28
            d.ellipse([cx + dx - n, cy - n, cx + dx + n, cy + n], fill=rgba(GREEN, 32))

    img = ink(img, membranes, bloom=26, gain=0.8)

    def label(d):
        d.text((0.08 * W, 0.06 * H), "CULTURE  //  T+ 00:00:00", font=font(30),
               fill=rgba(MUTED, 160))

    img = ink(img, label, bloom=10, gain=0.5)
    finish(img, "mitosis.png", outdir)


def plate_sequencer(outdir):
    """Lanes waiting for the helix, over a dead electropherogram baseline."""
    img = ground(focus=(0.68, 0.42))
    img = Image.alpha_composite(img, grid_layer(step=140, tick=8, alpha=130))

    lane_top, lane_bot = 0.09 * H, 0.62 * H

    def lanes(d):
        # Vertical guides the helix winds between.
        for i in range(5):
            x = (0.56 + i * 0.085) * W
            d.line([(x, lane_top), (x, lane_bot)], fill=rgba(MUTED, 95), width=3)
        # Ladder down the left of the lane block, numbered every sixth tick.
        x0 = 0.53 * W
        f = font(22)
        for i in range(31):
            y = lane_top + i * ((lane_bot - lane_top) / 30)
            major = i % 6 == 0
            d.line([(x0 - (34 if major else 16), y), (x0, y)],
                   fill=rgba(MUTED, 190 if major else 110), width=3 if major else 2)
            if major:
                d.text((x0 - 110, y - 14), f"{i * 50:>4}", font=f, fill=rgba(MUTED, 150))
        d.line([(x0, lane_top), (x0, lane_bot)], fill=rgba(MUTED, 150), width=3)

    img = ink(img, lanes, bloom=16, gain=0.6)

    def panel(d):
        # Instrument frame around the readout. Everything here is a fraction of
        # the plate because Sequencer.qml positions its live text off the SAME
        # fractions — hardcode a pixel offset and the two drift apart.
        x0, y0, x1, y1 = 0.06 * W, 0.115 * H, 0.44 * W, 0.62 * H
        d.rectangle([x0, y0, x1, y1], outline=rgba(MUTED, 90), width=2)
        d.line([(x0, y0 + 0.026 * H), (x1, y0 + 0.026 * H)], fill=rgba(MUTED, 70), width=2)
        d.text((x0 + 0.008 * W, y0 + 0.007 * H), "BASE CALL", font=font(24),
               fill=rgba(MUTED, 170))
        # The panel body and the Q figure are left empty on purpose: the scene
        # types into them, and a printed placeholder would show through.

    img = ink(img, panel, bloom=12, gain=0.5)

    def header(d):
        d.text((0.08 * W, 0.055 * H), "SEQUENCER  //  LANE 01-05", font=font(30),
               fill=rgba(MUTED, 170))

    img = ink(img, header, bloom=10, gain=0.4)

    def trace(d):
        # Four flat channel baselines across the bottom third, a few dead peaks.
        base = 0.90 * H
        channels = [(GREEN, 0), (CYAN, 1), (ORANGE, 2), (RED, 3)]
        rng = Random(0xB10)  # fixed seed: the plate must render identically every time
        for color, idx in channels:
            y = base - idx * 62
            d.line([(0.06 * W, y), (0.94 * W, y)], fill=rgba(color, 70), width=2)
            x = 0.08 * W
            while x < 0.93 * W:
                if rng.random() < 0.62:
                    h = rng.uniform(14, 52)
                    half = rng.uniform(9, 19)
                    d.polygon([(x - half, y), (x, y - h), (x + half, y)],
                              fill=rgba(color, 45))
                x += rng.uniform(38, 96)
        d.text((0.06 * W, base + 24), "CHANNEL  A  C  G  T", font=font(24),
               fill=rgba(MUTED, 140))

    img = ink(img, trace, bloom=18, gain=0.6)
    finish(img, "sequencer.png", outdir)


def plate_outbreak(outdir):
    """Facility grid with the nodes cold — the scene lights them up."""
    img = ground(focus=(0.50, 0.50), spread=1.05)

    lattice = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lattice)
    for x in range(0, W, 90):
        d.line([(x, 0), (x, H)], fill=rgba(GRID, 190))
    for y in range(0, H, 90):
        d.line([(0, y), (W, y)], fill=rgba(GRID, 190))
    for x in range(0, W, 450):
        d.line([(x, 0), (x, H)], fill=rgba(MUTED, 45), width=2)
    for y in range(0, H, 450):
        d.line([(0, y), (W, y)], fill=rgba(MUTED, 45), width=2)
    img = Image.alpha_composite(img, lattice)

    nodes = [(0.24, 0.34), (0.47, 0.58), (0.68, 0.28), (0.79, 0.66), (0.38, 0.78)]

    def vectors(d):
        for i in range(len(nodes) - 1):
            x0, y0 = nodes[i][0] * W, nodes[i][1] * H
            x1, y1 = nodes[i + 1][0] * W, nodes[i + 1][1] * H
            d.line([(x0, y0), (x1, y1)], fill=rgba(MUTED, 70), width=2)

    img = ink(img, vectors, bloom=14, gain=0.5)

    def markers(d):
        for i, (fx, fy) in enumerate(nodes):
            cx, cy = fx * W, fy * H
            hot = i == 1
            color = RED if hot else GREEN
            ring(d, cx, cy, 46, color, 150 if hot else 90, 3)
            ring(d, cx, cy, 120, color, 70 if hot else 45, 2)
            ring(d, cx, cy, 210, color, 34 if hot else 20, 2)
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=rgba(color, 200))
        cx, cy = nodes[1][0] * W, nodes[1][1] * H
        d.text((cx + 140, cy - 20), "INDEX CASE", font=font(30), fill=rgba(ORANGE, 190))

    img = ink(img, markers, bloom=26, gain=0.8)

    def header(d):
        # Not another "CONTAINMENT BREACH": Outbreak.qml puts HudFrame's own
        # breach header directly above this line, and two of them read as a bug.
        d.text((0.08 * W, 0.06 * H), "SECTOR 07  //  VECTOR MAP", font=font(30),
               fill=rgba(RED, 150))

    img = ink(img, header, bloom=12, gain=0.6)
    finish(img, "outbreak.png", outdir)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = sys.argv[1:]
    if "--prefix" in args:
        i = args.index("--prefix")
        globals()["PREFIX"] = args[i + 1]
        del args[i:i + 2]
    if "--colors" in args:
        i = args.index("--colors")
        load_colors(args[i + 1])
        del args[i:i + 2]
    outdir = args[0] if args else os.path.join(here, "..", "backgrounds")
    outdir = os.path.abspath(outdir)
    os.makedirs(outdir, exist_ok=True)
    plate_virions(outdir)
    plate_mitosis(outdir)
    plate_sequencer(outdir)
    plate_outbreak(outdir)


if __name__ == "__main__":
    main()
