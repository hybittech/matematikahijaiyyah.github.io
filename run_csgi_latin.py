"""
CSGI Extraction for Latin Alphabet & Digit PNGs
================================================
Runs the Zhang-Suen skeletonizer + SkeletonContractor
on all PNG images in:
  - data/Alphabet latin lowercase/
  - data/Alphabet latin uppercase/
  - data/Angka digit/

Outputs JSON results to data/csgi_output/
"""

import json
import os
import sys

import numpy as np
from PIL import Image

# Add project root to path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

# Imports follow the sys.path bootstrap above, so E402 is expected here.
from hijaiyyah.skeleton.contractor import SkeletonContractor  # noqa: E402
from hijaiyyah.skeleton.skeletonizer import zhang_suen_thinness  # noqa: E402

# ── Letter mappings ──────────────────────────────────────────────
LOWERCASE = list("abcdefghijklmnopqrstuvwxyz")
UPPERCASE = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITS = list("0123456789")


def load_binary_image(path: str) -> np.ndarray:
    """Load PNG and convert to binary (1=foreground, 0=background)."""
    img = Image.open(path).convert("L")
    arr = np.array(img)
    # Threshold: dark pixels = foreground (1), light = background (0)
    binary = (arr < 128).astype(np.uint8)
    return binary


def process_folder(folder: str, labels: list, category: str, output_dir: str):
    """Process all PNGs in a folder, outputting CSGI JSON."""
    results = []
    cat_dir = os.path.join(output_dir, category)
    os.makedirs(cat_dir, exist_ok=True)

    for i in range(1, len(labels) + 1):
        png_path = os.path.join(folder, f"{i}.png")
        if not os.path.exists(png_path):
            print(f"  [SKIP] {png_path} not found")
            continue

        label = labels[i - 1]
        print(f"  [{i:2d}/{len(labels)}] {label} ...", end=" ", flush=True)

        # Load and binarize
        binary = load_binary_image(png_path)

        # Skeletonize (Zhang-Suen)
        skeleton = zhang_suen_thinness(binary)

        # Contract to CSGI graph
        contractor = SkeletonContractor(
            letter_hijaiyyah=label,
            letter_name=f"{category}_{label}",
            release_id="CSGI-LATIN-v1.0",
        )
        graph = contractor.contract(skeleton)

        # Stats
        n_nodes = len(graph.nodes)
        n_edges = len(graph.edges)
        skel_pixels = int(np.sum(skeleton))

        print(f"nodes={n_nodes}, edges={n_edges}, skel_px={skel_pixels}")

        # Save individual JSON
        json_path = os.path.join(cat_dir, f"{label}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(graph.to_json(indent=2))

        results.append({
            "label": label,
            "category": category,
            "image": f"{i}.png",
            "image_size": list(binary.shape),
            "skeleton_pixels": skel_pixels,
            "nodes": n_nodes,
            "edges": n_edges,
        })

    return results


def main():
    data_dir = os.path.join(ROOT, "data")
    output_dir = os.path.join(data_dir, "csgi_output")
    os.makedirs(output_dir, exist_ok=True)

    all_results = []

    # ── Lowercase ─────────────────────────────────────────────────
    print("=" * 60)
    print("CSGI EXTRACTION — Latin Lowercase (a–z)")
    print("=" * 60)
    folder = os.path.join(data_dir, "Alphabet latin lowercase")
    results = process_folder(folder, LOWERCASE, "lowercase", output_dir)
    all_results.extend(results)

    # ── Uppercase ─────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("CSGI EXTRACTION — Latin Uppercase (A–Z)")
    print("=" * 60)
    folder = os.path.join(data_dir, "Alphabet latin uppercase")
    results = process_folder(folder, UPPERCASE, "uppercase", output_dir)
    all_results.extend(results)

    # ── Digits ────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("CSGI EXTRACTION — Digits (0–9)")
    print("=" * 60)
    folder = os.path.join(data_dir, "Angka digit")
    results = process_folder(folder, DIGITS, "digits", output_dir)
    all_results.extend(results)

    # ── Summary ───────────────────────────────────────────────────
    summary_path = os.path.join(output_dir, "summary.json")
    summary = {
        "csgi_version": "1.0",
        "pipeline": "Zhang-Suen → SkeletonContractor → CSGIGraph",
        "total_glyphs": len(all_results),
        "categories": {
            "lowercase": sum(1 for r in all_results if r["category"] == "lowercase"),
            "uppercase": sum(1 for r in all_results if r["category"] == "uppercase"),
            "digits": sum(1 for r in all_results if r["category"] == "digits"),
        },
        "results": all_results,
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"COMPLETE — {len(all_results)} glyphs processed")
    print(f"Output: {output_dir}")
    print(f"Summary: {summary_path}")
    print("=" * 60)

    # ── Print table ───────────────────────────────────────────────
    print()
    print(f"{'Label':<8} {'Category':<12} {'Nodes':>6} {'Edges':>6} {'SkelPx':>8}")
    print("-" * 42)
    for r in all_results:
        print(
            f"{r['label']:<8} {r['category']:<12} "
            f"{r['nodes']:>6} {r['edges']:>6} {r['skeleton_pixels']:>8}"
        )


if __name__ == "__main__":
    main()
