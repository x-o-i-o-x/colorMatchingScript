"""
main.py

Entry point for the terrain color mapper script.
"""

from terrain_color_mapper import (
    TerrainColorMapper,
    FILAMENTS,
    LOOKUP,
    INPUT_PNG,
    OUTPUT_NPZ,
    OUTPUT_PREVIEW,
    OUTPUT_DEBUG,
)

if __name__ == "__main__":
    mapper = TerrainColorMapper(FILAMENTS, LOOKUP)
    mapper.process_image(INPUT_PNG)
    mapper.print_report()
    mapper.save_matrices(OUTPUT_NPZ)
    mapper.save_preview_result(OUTPUT_PREVIEW)
    mapper.save_preview_debug(OUTPUT_DEBUG)

    # Quick preview: print a small corner of filament 0's matrix
    mat0 = mapper.get_matrices()[0]
    print(f"\nFilament 0 matrix (top-left 8x8 corner):")
    print(mat0[:8, :8])