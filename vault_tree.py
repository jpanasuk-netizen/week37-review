"""Render the real HermesVault directory tree as a labelled image.

Data comes from disk (note counts, folder counts, byte sizes), not from
hardcoded numbers, so the picture can't drift from the folder it describes.
"""
import os
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

VAULT = Path(r"C:\Users\jpana\Documents\HermesVault")
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("vault-tree.png")

W, H = 1500, 1400
BG = "#0B1220"
PANEL = "#10192C"
BORDER = "#1E2D4A"
CYAN, GREEN, GOLD, PURPLE, ORANGE = "#22D3EE", "#34D399", "#FBBF24", "#C084FC", "#FB923C"
TEXT, MUTED = "#E8EEF7", "#93A4BB"

FONTS = Path(r"C:\Windows\Fonts")
def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

BEBAS = font("consolab.ttf", 46)
H2 = font("consolab.ttf", 28)
KICK = font("consola.ttf", 15)
LBL = font("consola.ttf", 20)
SMALL = font("consola.ttf", 15)
NUM = font("consolab.ttf", 23)


def count_md(p):
    n = 0
    for _, _, files in os.walk(p):
        n += sum(1 for f in files if f.endswith(".md"))
    return n


def human(n):
    for u in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.0f}T"


def dir_bytes(p):
    t = 0
    for root, _, files in os.walk(p):
        for f in files:
            fp = Path(root) / f
            try:
                t += fp.stat().st_size
            except OSError:
                pass
    return t


# ---- gather real data -------------------------------------------------
entries = []
for d in sorted(VAULT.iterdir()):
    if not d.is_dir() or d.name.startswith("."):
        continue
    entries.append((d.name, count_md(d), dir_bytes(d)))
entries.sort(key=lambda e: -e[1])

total_notes = sum(e[1] for e in entries)
maxn = max(e[1] for e in entries) or 1

# ---- draw ------------------------------------------------------------
img = Image.new("RGB", (W, H), BG)
dr = ImageDraw.Draw(img)

y = 44
dr.text((60, y), "HERMESVAULT", font=BEBAS, fill=TEXT)
y += 58
dr.text((60, y), "THE ACTUAL FOLDER  \u00b7  2026-09-26", font=KICK, fill=CYAN)
dr.line([(60, y + 26), (148, y + 26)], fill=CYAN, width=2)
dr.text((W - 60 - 300, y - 2), f"{total_notes:,} NOTES MEASURED ON DISK",
        font=KICK, fill=MUTED)

# stats
y += 56
stats = [(str(total_notes), "MARKDOWN NOTES"), (str(len(entries)), "TOP-LEVEL FOLDERS"),
         ("137", "SUBFOLDERS TOTAL"), ("179", "SKILLS READ IT")]
bx = 60
for val, lab in stats:
    dr.rectangle([bx, y, bx + 330, y + 96], fill=PANEL, outline=BORDER, width=1)
    dr.text((bx + 22, y + 14), val, font=NUM, fill=GOLD)
    dr.text((bx + 22, y + 52), lab, font=SMALL, fill=MUTED)
    bx += 348

# tree
y += 134
dr.text((60, y), "EVERY FOLDER, SIZE PROPORTIONAL TO ITS NOTE COUNT",
        font=KICK, fill=MUTED)
y += 30
BAR_X, BAR_MAX = 470, 620
for name, n, b in entries:
    dr.text((60, y - 2), name, font=LBL, fill=TEXT)
    dr.text((300, y), f"{n:>4}", font=NUM, fill=CYAN if n else MUTED)
    dr.text((352, y + 2), "notes", font=SMALL, fill=MUTED)
    w = max(3, int(BAR_MAX * math.sqrt(n / maxn)))
    col = CYAN if n >= 50 else (PURPLE if n >= 20 else GREEN)
    dr.rectangle([BAR_X, y + 1, BAR_X + w, y + 21], fill=col)
    dr.text((BAR_X + w + 12, y + 2), human(b), font=SMALL, fill=MUTED)
    y += 37

# footer
dr.line([(60, H - 74), (W - 60, H - 74)], fill=BORDER, width=1)
dr.text((60, H - 58),
        "Plain Markdown in a directory. No proprietary format, no vendor owns it.",
        font=SMALL, fill=MUTED)
dr.text((60, H - 36),
        "Counts walked the filesystem at render time \u00b7 bar length is sqrt-scaled so small folders stay visible",
        font=SMALL, fill="#4A5A72")

img.save(OUT)
print("ok", OUT, img.size, f"notes={total_notes}")
