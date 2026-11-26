"""
Step 2 of the Advent calendar pipeline: build the door overlay sheet.

Reads scripts/layout.json (written by build_calendar.py) and
../Hintegrund.jpg, and writes ../Adventskalender_Tuerchen.png: a sheet
the exact same size as Adventskalender_Fotos.png, with a gold door
frame drawn exactly around each photo's rendered position, a randomly
shuffled number 1-24 per door, and a randomly chosen open/hinge side
per door.

See ../CLAUDE.md for the full spec and decision history.
"""
import os
import json
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

with open(os.path.join(SCRIPT_DIR, "layout.json")) as f:
    layout = json.load(f)

W, H = layout["canvas_w_px"], layout["canvas_h_px"]
boxes = layout["image_boxes"]  # exact photo bounding box: px, py, rw, rh
DPI = 300
PX_PER_CM = DPI / 2.54

RANDOM_SEED = 42  # change to reshuffle door numbers / hinge sides

# ---------- Background: map directly onto the canvas (no crop, no rotate) ----------
bg = Image.open(os.path.join(PROJECT_DIR, "Hintegrund.jpg")).convert("RGB")
bg_resized = bg.resize((W, H), Image.LANCZOS)

overlay = Image.new("RGB", (W, H), (10, 8, 20))
canvas = Image.blend(bg_resized, overlay, 0.40)
canvas = canvas.filter(ImageFilter.GaussianBlur(radius=1.5))
draw = ImageDraw.Draw(canvas, "RGBA")

FONT_DIR = r"C:\Windows\Fonts"
def font(path, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, path), size)

GOLD = (212, 175, 55)
GOLD_SOFT = (212, 175, 55, 235)

random.seed(RANDOM_SEED)
numbers = list(range(1, 25))
random.shuffle(numbers)

hinge_left = [random.random() < 0.5 for _ in range(24)]
random.shuffle(hinge_left)

LINE_W = max(1, round(0.045 * PX_PER_CM * 10 * 0.2))  # 20% of the original line weight

# One fixed, uniform font size for every number (not scaled per door).
avg_min_side = sum(min(w, h) for (_, _, w, h) in boxes) / len(boxes)
fsize = max(12, round(avg_min_side * 0.34))
fnt = font("OLDENGL.TTF", fsize)  # Old English Text MT: closest available stand-in for "Chaucer"

for (x, y, w, h), num, left in zip(boxes, numbers, hinge_left):
    x0, y0, x1, y1 = x, y, x + w, y + h

    # top + bottom: always drawn
    draw.line([(x0, y0), (x1, y0)], fill=GOLD_SOFT, width=LINE_W)
    draw.line([(x0, y1), (x1, y1)], fill=GOLD_SOFT, width=LINE_W)

    # left/right: exactly one drawn, chosen at random per door (the other
    # side is the door's implicit open/hinge side)
    if left:
        draw.line([(x0, y0), (x0, y1)], fill=GOLD_SOFT, width=LINE_W)
    else:
        draw.line([(x1, y0), (x1, y1)], fill=GOLD_SOFT, width=LINE_W)

    # number, fixed size, centered on the photo's own bounding box
    text = str(num)
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = x + w / 2 - tw / 2 - bbox[0]
    ty = y + h / 2 - th / 2 - bbox[1]
    draw.text((tx + 1.5, ty + 1.5), text, font=fnt, fill=(0, 0, 0, 110))
    draw.text((tx, ty), text, font=fnt, fill=GOLD + (255,))

out2 = os.path.join(PROJECT_DIR, "Adventskalender_Tuerchen.png")
canvas.convert("RGB").save(out2, dpi=(DPI, DPI))
print("Saved", out2)
print(f"Font size: {fsize}px ({fsize/PX_PER_CM*10:.1f}mm)")

with open(os.path.join(SCRIPT_DIR, "numbers.json"), "w") as f:
    json.dump({"names": layout["names"], "numbers": numbers, "hinge_left": hinge_left}, f, indent=2)
print("Saved", os.path.join(SCRIPT_DIR, "numbers.json"))
