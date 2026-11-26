"""
Step 1 of the Advent calendar pipeline: build the photo collage sheet.

Reads all photos from ../Quellfotos, arranges them in a uniform grid
(cell aspect ratio chosen to match the photos' average aspect ratio),
contain-fits each photo into its cell (no crop, no distortion), and
writes ../Adventskalender_Fotos.png plus scripts/layout.json (consumed
by build_doors.py).

See ../CLAUDE.md for the full spec and decision history.
"""
import os
import json
import math
from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
SOURCE_DIR = os.path.join(PROJECT_DIR, "Quellfotos")

DPI = 300
PX_PER_CM = DPI / 2.54

CANVAS_W_CM = 30.0  # landscape: width x height
CANVAS_H_CM = 20.0
MARGIN_CM = 1.0
GAP_CM = 1.0

canvas_w_px = round(CANVAS_W_CM * PX_PER_CM)
canvas_h_px = round(CANVAS_H_CM * PX_PER_CM)
margin_px = MARGIN_CM * PX_PER_CM
gap_px = GAP_CM * PX_PER_CM
usable_w = canvas_w_px - 2 * margin_px
usable_h = canvas_h_px - 2 * margin_px

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".heic")

files = sorted(f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(IMAGE_EXTS))
print(f"Found {len(files)} image files in {SOURCE_DIR}")
assert len(files) == 24, f"Expected 24 photos in Quellfotos/, found {len(files)}: {files}"

images = []
for f in files:
    im = Image.open(os.path.join(SOURCE_DIR, f))
    im = ImageOps.exif_transpose(im).convert("RGB")
    images.append({"name": f, "img": im, "ar": im.width / im.height})

# Geometric-mean aspect ratio across all 24 photos -> used only to pick the
# cols x rows split of 24 whose cell shape best matches the photos' own shape.
avg_ar = math.exp(sum(math.log(im["ar"]) for im in images) / len(images))
print(f"Geometric-mean aspect ratio of the 24 photos: {avg_ar:.3f}")

best = None
for cols in range(1, 25):
    if 24 % cols:
        continue
    rows = 24 // cols
    cell_w = (usable_w - (cols - 1) * gap_px) / cols
    cell_h = (usable_h - (rows - 1) * gap_px) / rows
    if cell_w <= 0 or cell_h <= 0:
        continue
    cell_ar = cell_w / cell_h
    score = abs(math.log(cell_ar / avg_ar))
    if best is None or score < best[0]:
        best = (score, cols, rows, cell_w, cell_h)

_, cols, rows, cell_w, cell_h = best
print(f"Chosen grid: {cols} cols x {rows} rows, cell size "
      f"{cell_w/PX_PER_CM:.2f} x {cell_h/PX_PER_CM:.2f} cm (cell ratio {cell_w/cell_h:.3f})")

# Uniform grid cells, exact 1cm margin and 1cm gap everywhere (by construction).
cells = []
for r in range(rows):
    y = margin_px + r * (cell_h + gap_px)
    for c in range(cols):
        x = margin_px + c * (cell_w + gap_px)
        cells.append((x, y, cell_w, cell_h, c, r))
assert len(cells) == 24

# ---------- Sheet 1: photo collage, contain-fit (no crop, no stretch) ----------
canvas = Image.new("RGB", (canvas_w_px, canvas_h_px), "white")
image_boxes = []  # exact rendered (x, y, w, h) per photo, same order as `images`
for info, (x, y, w, h, c, r) in zip(images, cells):
    img = info["img"]
    scale = min(w / img.width, h / img.height)
    rw, rh = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    resized = img.resize((rw, rh), Image.LANCZOS)
    px = round(x + (w - rw) / 2)
    py = round(y + (h - rh) / 2)
    canvas.paste(resized, (px, py))
    image_boxes.append((px, py, rw, rh))

out1 = os.path.join(PROJECT_DIR, "Adventskalender_Fotos.png")
canvas.save(out1, dpi=(DPI, DPI))
print("Saved", out1)

with open(os.path.join(SCRIPT_DIR, "layout.json"), "w") as f:
    json.dump({
        "canvas_w_px": canvas_w_px,
        "canvas_h_px": canvas_h_px,
        "cols": cols,
        "rows": rows,
        "cells": cells,              # uniform grid cell: x, y, w, h, col, row
        "image_boxes": image_boxes,  # exact photo bounding box: px, py, rw, rh
        "names": [im["name"] for im in images],  # Quellfotos filenames, reading order
    }, f)
print("Saved", os.path.join(SCRIPT_DIR, "layout.json"))
