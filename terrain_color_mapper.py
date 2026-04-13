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
OUTPUT_NPZ           = "matrices.npz"   # saved output (numpy arrays)
OUTPUT_USED_COLOR   = "used_color_image.png"   # matched print color per pixel
OUTPUT_TOP_LAYER    = "top_layer_image.png"  # top filament identity per pixel
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

class TerrainColorMapper:
    def __init__(self, filaments, lookup):
        self.filaments = filaments
        self.lookup = lookup
        self.lookup_lab = self._build_lookup_lab(self.lookup, self.filaments)
        self.matrices = None
        self.meta = None

    def _rgb_to_lab(self, rgb_tuple):
        """Convert a single (R,G,B) 0-255 tuple to CIELAB."""
        arr = np.array(rgb_tuple, dtype=np.float32).reshape(1, 1, 3) / 255.0
        return skcolor.rgb2lab(arr).reshape(3)

    def _build_lookup_lab(self, lookup, filaments):
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
                "result_lab": self._rgb_to_lab(fdata["rgb"]),
            })

        # Combination entries from lookup table
        for row in lookup:
            entries.append({
                "top":        row["top"],
                "bottom":     row["bottom"],
                "top_layers": row["top_layers"],
                "result_rgb": row["result_rgb"],
                "result_lab": self._rgb_to_lab(row["result_rgb"]),
            })

        return entries

    def process_image(self, input_path):
        """
        Main pipeline.

        Sets self.matrices and self.meta
        """
        img  = Image.open(input_path).convert("RGB")
        data = np.array(img, dtype=np.uint8)          # shape (H, W, 3)
        H, W = data.shape[:2]

        print(f"Image size: {W} x {H} ({W*H:,} pixels)")

        # lookup_lab is pre-built in __init__

        # Convert entire image to LAB in one vectorised call
        img_float = data.astype(np.float32) / 255.0   # (H, W, 3)
        img_lab   = skcolor.rgb2lab(img_float)         # (H, W, 3)

        # Initialise all matrices to NOT_USED
        num_filaments = len(self.filaments)
        matrices = {
            fid: np.full((H, W), NOT_USED, dtype=np.uint8)
            for fid in self.filaments
        }

        # Store best-match metadata for the report and preview images
        match_errors  = np.zeros((H, W), dtype=np.float32)
        match_tops    = np.zeros((H, W), dtype=np.uint8)
        match_bots    = np.full((H, W), 255, dtype=np.uint8)  # 255 = no bottom
        match_depths  = np.zeros((H, W), dtype=np.uint8)
        # RGB of the matched lookup entry — used for the result preview PNG
        match_rgb_out = np.zeros((H, W, 3), dtype=np.uint8)

        # Pre-stack lookup into arrays for fast distance calculation
        result_labs = np.array([e["result_lab"] for e in self.lookup_lab])  # (N, 3)

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
                best = self.lookup_lab[best_idx]

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
        self.matrices = matrices
        self.meta = meta

    def save_matrices(self, output_path):
        """Save all matrices and metadata to a single .npz file."""
        payload = {}
        for fid, mat in self.matrices.items():
            payload[f"filament_{fid}"] = mat
        for key, arr in self.meta.items():
            payload[f"meta_{key}"] = arr
        np.savez_compressed(output_path, **payload)
        print(f"Saved to {output_path}")

    def save_used_color_image(self, output_path):
        """
        PNG 1 — result color preview.
        Each pixel shows the result_rgb of the best-matched lookup entry,
        i.e. the color this pixel should actually print as.
        """
        img = Image.fromarray(self.meta["rgb_out"], mode="RGB")
        img.save(output_path)
        print(f"Used color image saved to {output_path}")

    def save_top_layer_image(self, output_path):
        """
        PNG 2 — top filament identity map.
        Each pixel is colored by which filament slot sits on top,
        using the debug_colors palette. Useful for checking swap geography.
        """
        H, W  = self.meta["tops"].shape
        canvas = np.zeros((H, W, 3), dtype=np.uint8)

        for fid in self.filaments:
            mask = self.meta["tops"] == fid
            canvas[mask] = DEBUG_COLORS[fid]

        img = Image.fromarray(canvas, mode="RGB")
        img.save(output_path)
        print(f"Top layer image saved to {output_path}")

    def get_used_color_image(self):
        """Return the used color image as a PIL Image object."""
        return Image.fromarray(self.meta["rgb_out"], mode="RGB")

    def get_top_layer_image(self):
        """Return the top layer image as a PIL Image object."""
        H, W = self.meta["tops"].shape
        canvas = np.zeros((H, W, 3), dtype=np.uint8)
        for fid in self.filaments:
            mask = self.meta["tops"] == fid
            canvas[mask] = DEBUG_COLORS[fid]
        return Image.fromarray(canvas, mode="RGB")

    def print_report(self):
        """Print a human-readable summary of the output matrices."""
        H, W = list(self.matrices.values())[0].shape
        total = H * W

        print("\n" + "=" * 60)
        print("FILAMENT MATRIX REPORT")
        print("=" * 60)
        print(f"Image size   : {W} x {H}")
        print(f"Total pixels : {total:,}")
        print()

        for fid, mat in self.matrices.items():
            name  = self.filaments[fid]["name"]
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
        errors = self.meta["errors"]
        print(f"  Mean  : {errors.mean():.2f}")
        print(f"  Median: {float(np.median(errors)):.2f}")
        print(f"  95th %%: {float(np.percentile(errors, 95)):.2f}")
        print(f"  Max   : {errors.max():.2f}")
        print()
        print("Note: LAB delta-E < 10 is generally a good perceptual match.")
        print("      Values > 20 suggest the target color is poorly covered")
        print("      by your current filament combinations.")
        print("=" * 60)

    def get_matrices(self):
        return self.matrices

    def get_meta(self):
        return self.meta


# ---------------------------------------------------------------------------
