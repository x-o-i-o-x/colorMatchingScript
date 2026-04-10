"""
terrain_color_mapper.py

Reads a color PNG (e.g. from Gaea) and produces 4 filament matrices.
Each matrix is the same size as the input image (1 pixel = 1 cell).

Matrix values:
  0        = this filament is the top layer at this pixel
  1..5     = this filament is this many layers beneath the top
  6        = this filament is not used at this pixel

Requires:
  pip install numpy pillow scikit-image
"""

import numpy as np
from PIL import Image
from skimage import color as skcolor

# ---------------------------------------------------------------------------
# PASTE YOUR GENERATED DATA BLOCK HERE
# ---------------------------------------------------------------------------

FILAMENTS = {
    0: {"name": "F1", "rgb": (0, 0, 0)},
    1: {"name": "F2", "rgb": (0, 134, 214)},
    2: {"name": "F3", "rgb": (255, 255, 255)},
    3: {"name": "F4", "rgb": (0, 174, 66)},
}

LOOKUP = [
    {"top": 0, "bottom": 1, "top_layers": 1, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 1, "top_layers": 2, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 1, "top_layers": 3, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 1, "top_layers": 4, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 1, "top_layers": 5, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 2, "top_layers": 1, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 2, "top_layers": 2, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 2, "top_layers": 3, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 2, "top_layers": 4, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 2, "top_layers": 5, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 3, "top_layers": 1, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 3, "top_layers": 2, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 3, "top_layers": 3, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 3, "top_layers": 4, "result_rgb": (0, 0, 0)},
    {"top": 0, "bottom": 3, "top_layers": 5, "result_rgb": (0, 0, 0)},
    {"top": 1, "bottom": 0, "top_layers": 1, "result_rgb": (0, 48, 77)},
    {"top": 1, "bottom": 0, "top_layers": 2, "result_rgb": (0, 81, 128)},
    {"top": 1, "bottom": 0, "top_layers": 3, "result_rgb": (0, 113, 179)},
    {"top": 1, "bottom": 0, "top_layers": 4, "result_rgb": (0, 134, 214)},
    {"top": 1, "bottom": 0, "top_layers": 5, "result_rgb": (0, 134, 214)},
    {"top": 1, "bottom": 2, "top_layers": 1, "result_rgb": (102, 199, 255)},
    {"top": 1, "bottom": 2, "top_layers": 2, "result_rgb": (0, 162, 255)},
    {"top": 1, "bottom": 2, "top_layers": 3, "result_rgb": (0, 134, 214)},
    {"top": 1, "bottom": 2, "top_layers": 4, "result_rgb": (0, 134, 214)},
    {"top": 1, "bottom": 2, "top_layers": 5, "result_rgb": (0, 134, 214)},
    {"top": 1, "bottom": 3, "top_layers": 1, "result_rgb": (0, 173, 130)},
    {"top": 1, "bottom": 3, "top_layers": 2, "result_rgb": (0, 179, 214)},
    {"top": 1, "bottom": 3, "top_layers": 3, "result_rgb": (0, 134, 214)},
    {"top": 1, "bottom": 3, "top_layers": 4, "result_rgb": (0, 134, 214)},
    {"top": 1, "bottom": 3, "top_layers": 5, "result_rgb": (0, 134, 214)},
    {"top": 2, "bottom": 0, "top_layers": 1, "result_rgb": (51, 51, 51)},
    {"top": 2, "bottom": 0, "top_layers": 2, "result_rgb": (102, 102, 102)},
    {"top": 2, "bottom": 0, "top_layers": 3, "result_rgb": (153, 153, 153)},
    {"top": 2, "bottom": 0, "top_layers": 4, "result_rgb": (204, 204, 204)},
    {"top": 2, "bottom": 0, "top_layers": 5, "result_rgb": (230, 230, 230)},
    {"top": 2, "bottom": 1, "top_layers": 1, "result_rgb": (51, 177, 255)},
    {"top": 2, "bottom": 1, "top_layers": 2, "result_rgb": (204, 236, 255)},
    {"top": 2, "bottom": 1, "top_layers": 3, "result_rgb": (229, 246, 255)},
    {"top": 2, "bottom": 1, "top_layers": 4, "result_rgb": (255, 255, 255)},
    {"top": 2, "bottom": 1, "top_layers": 5, "result_rgb": (255, 255, 255)},
    {"top": 2, "bottom": 3, "top_layers": 1, "result_rgb": (64, 191, 113)},
    {"top": 2, "bottom": 3, "top_layers": 2, "result_rgb": (156, 201, 173)},
    {"top": 2, "bottom": 3, "top_layers": 3, "result_rgb": (189, 219, 201)},
    {"top": 2, "bottom": 3, "top_layers": 4, "result_rgb": (222, 237, 228)},
    {"top": 2, "bottom": 3, "top_layers": 5, "result_rgb": (255, 255, 255)},
    {"top": 3, "bottom": 0, "top_layers": 1, "result_rgb": (0, 51, 20)},
    {"top": 3, "bottom": 0, "top_layers": 2, "result_rgb": (0, 102, 41)},
    {"top": 3, "bottom": 0, "top_layers": 3, "result_rgb": (0, 153, 59)},
    {"top": 3, "bottom": 0, "top_layers": 4, "result_rgb": (0, 174, 66)},
    {"top": 3, "bottom": 0, "top_layers": 5, "result_rgb": (0, 174, 66)},
    {"top": 3, "bottom": 1, "top_layers": 1, "result_rgb": (0, 173, 101)},
    {"top": 3, "bottom": 1, "top_layers": 2, "result_rgb": (0, 173, 87)},
    {"top": 3, "bottom": 1, "top_layers": 3, "result_rgb": (0, 173, 72)},
    {"top": 3, "bottom": 1, "top_layers": 4, "result_rgb": (0, 174, 66)},
    {"top": 3, "bottom": 1, "top_layers": 5, "result_rgb": (0, 174, 66)},
    {"top": 3, "bottom": 2, "top_layers": 1, "result_rgb": (153, 255, 192)},
    {"top": 3, "bottom": 2, "top_layers": 2, "result_rgb": (77, 255, 145)},
    {"top": 3, "bottom": 2, "top_layers": 3, "result_rgb": (0, 255, 98)},
    {"top": 3, "bottom": 2, "top_layers": 4, "result_rgb": (0, 204, 78)},
    {"top": 3, "bottom": 2, "top_layers": 5, "result_rgb": (0, 174, 66)},
]

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

INPUT_PNG        = "color.png"      # path to your Gaea color texture
OUTPUT_NPZ       = "matrices.npz"   # saved output (numpy arrays)
OUTPUT_PREVIEW   = "preview_result.png"   # matched print color per pixel
OUTPUT_DEBUG     = "preview_filaments.png"  # top filament identity per pixel
NOT_USED         = 6               # sentinel value for "not required"

# Colors used in the debug PNG to represent each filament slot.
# These are display colors only — they don't need to match your filament RGBs,
# just be visually distinct. Override if you prefer different debug colors.
DEBUG_COLORS = {
    0: (220,  50,  50),   # red-ish   → slot 0
    1: ( 50, 120, 220),   # blue-ish  → slot 1
    2: ( 40, 180, 120),   # green-ish → slot 2
    3: (240, 160,  30),   # amber     → slot 3
}

# ---------------------------------------------------------------------------
# CORE
# ---------------------------------------------------------------------------

def rgb_to_lab(rgb_tuple):
    """Convert a single (R,G,B) 0-255 tuple to CIELAB."""
    arr = np.array(rgb_tuple, dtype=np.float32).reshape(1, 1, 3) / 255.0
    return skcolor.rgb2lab(arr).reshape(3)


def delta_e(lab1, lab2):
    """Euclidean distance in LAB space (approx. CIE76)."""
    return np.sqrt(np.sum((lab1 - lab2) ** 2))


def build_lookup_lab(lookup, filaments):
    """
    Pre-convert every lookup entry's result_rgb to LAB.
    Also add one 'solid' entry per filament (top_layers=5, no bottom)
    so a pure solid color can always be matched.

    Returns a list of dicts, each with keys:
        top, bottom (or None), top_layers, result_lab
    """
    entries = []

    # Solid filament entries (no shine-through)
    for fid, fdata in filaments.items():
        entries.append({
            "top":        fid,
            "bottom":     None,
            "top_layers": 5,
            "result_rgb": fdata["rgb"],
            "result_lab": rgb_to_lab(fdata["rgb"]),
        })

    # Combination entries from lookup table
    for row in lookup:
        entries.append({
            "top":        row["top"],
            "bottom":     row["bottom"],
            "top_layers": row["top_layers"],
            "result_rgb": row["result_rgb"],
            "result_lab": rgb_to_lab(row["result_rgb"]),
        })

    return entries


def find_best_match(pixel_lab, lookup_lab):
    """
    Return the lookup entry whose result_lab is closest to pixel_lab
    in perceptual (LAB) color space.
    """
    best_entry = None
    best_dist  = float("inf")

    for entry in lookup_lab:
        d = delta_e(pixel_lab, entry["result_lab"])
        if d < best_dist:
            best_dist  = d
            best_entry = entry

    return best_entry, best_dist


def process_image(input_path, filaments, lookup):
    """
    Main pipeline.

    Returns:
        matrices  : dict {filament_id: 2D numpy array of uint8}
        match_info: 2D array of dicts (for the report)
    """
    img  = Image.open(input_path).convert("RGB")
    data = np.array(img, dtype=np.uint8)          # shape (H, W, 3)
    H, W = data.shape[:2]

    print(f"Image size: {W} x {H} ({W*H:,} pixels)")

    # Pre-build LAB lookup once (not per pixel)
    lookup_lab = build_lookup_lab(lookup, filaments)

    # Convert entire image to LAB in one vectorised call
    img_float = data.astype(np.float32) / 255.0   # (H, W, 3)
    img_lab   = skcolor.rgb2lab(img_float)         # (H, W, 3)

    # Initialise all matrices to NOT_USED
    num_filaments = len(filaments)
    matrices = {
        fid: np.full((H, W), NOT_USED, dtype=np.uint8)
        for fid in filaments
    }

    # Store best-match metadata for the report and preview images
    match_errors  = np.zeros((H, W), dtype=np.float32)
    match_tops    = np.zeros((H, W), dtype=np.uint8)
    match_bots    = np.full((H, W), 255, dtype=np.uint8)  # 255 = no bottom
    match_depths  = np.zeros((H, W), dtype=np.uint8)
    # RGB of the matched lookup entry — used for the result preview PNG
    match_rgb_out = np.zeros((H, W, 3), dtype=np.uint8)

    # Pre-stack lookup into arrays for fast distance calculation
    result_labs = np.array([e["result_lab"] for e in lookup_lab])  # (N, 3)

    print("Matching pixels...")
    for y in range(H):
        if y % 100 == 0:
            print(f"  row {y}/{H}", end="\r")

        for x in range(W):
            pixel_lab = img_lab[y, x]              # (3,)

            # Vectorised distance to all lookup entries at once
            diffs = result_labs - pixel_lab        # (N, 3)
            dists = np.sqrt(np.sum(diffs ** 2, axis=1))  # (N,)
            best_idx = int(np.argmin(dists))
            best = lookup_lab[best_idx]

            top    = best["top"]
            bottom = best["bottom"]
            depth  = best["top_layers"]

            # Write into filament matrices
            matrices[top][y, x] = 0               # top layer = depth 0

            if bottom is not None:
                matrices[bottom][y, x] = depth    # bottom at actual depth

            # Store metadata
            match_errors[y, x]  = float(dists[best_idx])
            match_tops[y, x]    = top
            match_bots[y, x]    = bottom if bottom is not None else 255
            match_depths[y, x]  = depth
            match_rgb_out[y, x] = best["result_rgb"]

    print(f"\nDone. Mean LAB error: {match_errors.mean():.2f}  "
          f"Max LAB error: {match_errors.max():.2f}")

    meta = {
        "errors":    match_errors,
        "tops":      match_tops,
        "bots":      match_bots,
        "depths":    match_depths,
        "rgb_out":   match_rgb_out,   # (H, W, 3) — matched print color
    }
    return matrices, meta


def save_matrices(matrices, meta, output_path):
    """Save all matrices and metadata to a single .npz file."""
    payload = {}
    for fid, mat in matrices.items():
        payload[f"filament_{fid}"] = mat
    for key, arr in meta.items():
        payload[f"meta_{key}"] = arr
    np.savez_compressed(output_path, **payload)
    print(f"Saved to {output_path}")


def save_preview_result(meta, output_path):
    """
    PNG 1 — result color preview.
    Each pixel shows the result_rgb of the best-matched lookup entry,
    i.e. the color this pixel should actually print as.
    """
    img = Image.fromarray(meta["rgb_out"], mode="RGB")
    img.save(output_path)
    print(f"Result preview saved to {output_path}")


def save_preview_debug(meta, filaments, debug_colors, output_path):
    """
    PNG 2 — top filament identity map.
    Each pixel is colored by which filament slot sits on top,
    using the debug_colors palette. Useful for checking swap geography.
    """
    H, W  = meta["tops"].shape
    canvas = np.zeros((H, W, 3), dtype=np.uint8)

    for fid in filaments:
        mask = meta["tops"] == fid
        canvas[mask] = debug_colors[fid]

    img = Image.fromarray(canvas, mode="RGB")
    img.save(output_path)
    print(f"Debug preview saved to  {output_path}")


def print_report(matrices, meta, filaments):
    """Print a human-readable summary of the output matrices."""
    H, W = list(matrices.values())[0].shape
    total = H * W

    print("\n" + "=" * 60)
    print("FILAMENT MATRIX REPORT")
    print("=" * 60)
    print(f"Image size   : {W} x {H}")
    print(f"Total pixels : {total:,}")
    print()

    for fid, mat in matrices.items():
        name  = filaments[fid]["name"]
        used  = int(np.sum(mat < NOT_USED))
        pct   = 100.0 * used / total

        print(f"Filament {fid} ({name})")
        print(f"  Used at     : {used:,} pixels ({pct:.1f}%)")

        for d in range(6):
            count = int(np.sum(mat == d))
            if count > 0:
                label = "top layer" if d == 0 else f"{d} layer(s) deep"
                print(f"  depth {d} ({label:15s}): {count:,}")
        print()

    print("Color match quality (LAB delta-E):")
    errors = meta["errors"]
    print(f"  Mean  : {errors.mean():.2f}")
    print(f"  Median: {float(np.median(errors)):.2f}")
    print(f"  95th %%: {float(np.percentile(errors, 95)):.2f}")
    print(f"  Max   : {errors.max():.2f}")
    print()
    print("Note: LAB delta-E < 10 is generally a good perceptual match.")
    print("      Values > 20 suggest the target color is poorly covered")
    print("      by your current filament combinations.")
    print("=" * 60)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    matrices, meta = process_image(INPUT_PNG, FILAMENTS, LOOKUP)
    print_report(matrices, meta, FILAMENTS)
    save_matrices(matrices, meta, OUTPUT_NPZ)
    save_preview_result(meta, OUTPUT_PREVIEW)
    save_preview_debug(meta, FILAMENTS, DEBUG_COLORS, OUTPUT_DEBUG)

    # Quick preview: print a small corner of filament 0's matrix
    mat0 = matrices[0]
    print(f"\nFilament 0 matrix (top-left 8x8 corner):")
    print(mat0[:8, :8])
