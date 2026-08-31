#!/usr/bin/env python3
"""
CSGi Pipeline — Canonical Skeleton Graph Interface
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from hijaiyyah.core.codex_entry import CodexEntry  # noqa: E402
from hijaiyyah.core.master_table import MASTER_TABLE  # noqa: E402

try:
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    HAS_IMAGING = True
except ImportError:
    HAS_IMAGING = False
    np = None  # type: ignore[assignment]
    Image = None  # type: ignore[assignment]
    ndimage = None  # type: ignore[assignment]


# ── Zhang-Suen thinning ─────────────────────────────────────────

def zhang_suen_thin(image: Any) -> Any:
    """Zhang-Suen thinning. Input/output: numpy uint8 arrays."""
    skel = image.copy().astype(np.uint8)
    rows, cols = skel.shape
    changed = True

    while changed:
        changed = False
        for step in (0, 1):
            marked: List[Tuple[int, int]] = []
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    if skel[i, j] == 0:
                        continue
                    p2 = int(skel[i-1, j])
                    p3 = int(skel[i-1, j+1])
                    p4 = int(skel[i, j+1])
                    p5 = int(skel[i+1, j+1])
                    p6 = int(skel[i+1, j])
                    p7 = int(skel[i+1, j-1])
                    p8 = int(skel[i, j-1])
                    p9 = int(skel[i-1, j-1])
                    neighbors = [p2, p3, p4, p5, p6, p7, p8, p9]
                    B = sum(neighbors)
                    if B < 2 or B > 6:
                        continue
                    A = sum(
                        1 for k in range(8)
                        if neighbors[k] == 0 and neighbors[(k+1) % 8] == 1
                    )
                    if A != 1:
                        continue
                    if step == 0:
                        if p2 * p4 * p6 != 0 or p4 * p6 * p8 != 0:
                            continue
                    else:
                        if p2 * p4 * p8 != 0 or p2 * p6 * p8 != 0:
                            continue
                    marked.append((i, j))
            for mi, mj in marked:
                skel[mi, mj] = 0
                changed = True
    return skel


# ── Graph data types ─────────────────────────────────────────────

@dataclass
class GraphNode:
    id: int
    x: int
    y: int
    degree: int

    def to_dict(self) -> Dict[str, int]:
        return {"id": self.id, "x": self.x, "y": self.y, "degree": self.degree}


@dataclass
class GraphEdge:
    id: int
    u: int
    v: int
    points: List[Tuple[int, int]] = field(default_factory=list)
    length: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "u": self.u, "v": self.v,
            "length": self.length,
            "points": [list(p) for p in self.points],
        }


@dataclass
class CSGiResult:
    letter: str
    name: str
    index: int
    adjacency: str = "8-neighborhood"
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    body_pixels: int = 0
    skeleton_pixels: int = 0
    nuqtah_components: int = 0
    processing_time_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "csgi_version": "1.0",
            "letter": self.letter,
            "name": self.name,
            "index": self.index,
            "adjacency": self.adjacency,
            "stats": {
                "body_pixels": self.body_pixels,
                "skeleton_pixels": self.skeleton_pixels,
                "nuqtah_components": self.nuqtah_components,
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "processing_time_ms": round(self.processing_time_ms, 2),
            },
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "error": self.error,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# ── Graph construction ───────────────────────────────────────────

def build_skeleton_graph(skeleton: Any) -> Tuple[List[GraphNode], List[GraphEdge]]:
    """Convert skeleton array to graph. Returns (nodes, edges)."""
    rows, cols = skeleton.shape
    nodes: List[GraphNode] = []
    node_map: Dict[Tuple[int, int], int] = {}
    edges: List[GraphEdge] = []

    pixel_degree: Dict[Tuple[int, int], int] = {}
    skeleton_points: List[Tuple[int, int]] = []

    for y in range(rows):
        for x in range(cols):
            if skeleton[y, x] == 0:
                continue
            skeleton_points.append((int(y), int(x)))
            count = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < rows and 0 <= nx < cols and skeleton[ny, nx] > 0:
                        count += 1
            pixel_degree[(int(y), int(x))] = count

    node_id = 0
    for (y, x), deg in pixel_degree.items():
        if deg != 2:
            nodes.append(GraphNode(id=node_id, x=x, y=y, degree=deg))
            node_map[(y, x)] = node_id
            node_id += 1

    visited: set = set()
    edge_id = 0

    for start_pos, start_nid in node_map.items():
        sy, sx = start_pos
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                ny, nx = int(sy + dy), int(sx + dx)
                if (ny, nx) not in pixel_degree:
                    continue

                path = [(sx, sy), (nx, ny)]
                current = (ny, nx)
                prev = (sy, sx)

                while True:
                    if current in node_map and current != start_pos:
                        break
                    cy, cx = current
                    found = False
                    for ddy in (-1, 0, 1):
                        for ddx in (-1, 0, 1):
                            if ddy == 0 and ddx == 0:
                                continue
                            nny, nnx = int(cy + ddy), int(cx + ddx)
                            if (nny, nnx) == prev or (nny, nnx) not in pixel_degree:
                                continue
                            path.append((nnx, nny))
                            prev = current
                            current = (nny, nnx)
                            found = True
                            break
                        if found:
                            break
                    if not found:
                        break

                if current in node_map:
                    end_nid = node_map[current]
                    key = (min(start_nid, end_nid), max(start_nid, end_nid))
                    if key not in visited:
                        visited.add(key)
                        edges.append(GraphEdge(
                            id=edge_id, u=start_nid, v=end_nid,
                            points=path, length=len(path) - 1,
                        ))
                        edge_id += 1

    if not nodes and skeleton_points:
        y, x = skeleton_points[0]
        nodes.append(GraphNode(id=0, x=x, y=y, degree=0))

    return nodes, edges


# ── Pipeline ─────────────────────────────────────────────────────

def process_letter(
    entry: CodexEntry,
    glyph_dir: Optional[str] = None,
) -> CSGiResult:
    """Run full CSGi pipeline on one letter."""
    result = CSGiResult(letter=entry.char, name=entry.name, index=entry.index)

    if not HAS_IMAGING:
        result.error = "Missing: numpy, Pillow, scipy"
        return result

    if glyph_dir:
        glyph_path = Path(glyph_dir) / f"{entry.index}.png"
    else:
        glyph_path = _ROOT / "data" / "kfgqpc" / "glyphs" / f"{entry.index}.png"

    if not glyph_path.exists():
        result.error = f"Not found: {glyph_path}"
        return result

    t0 = time.perf_counter()

    try:
        img = Image.open(str(glyph_path)).convert("L")
        arr = np.array(img)
        binary = (arr < 128).astype(np.uint8)

        # ndimage.label returns (labeled_array, num_features)
        label_output: Any = ndimage.label(binary)
        labeled = label_output[0]
        num_features = int(label_output[1])

        if num_features > 1:
            sizes_arr: Any = ndimage.sum(binary, labeled, range(1, num_features + 1))
            sizes = [float(s) for s in sizes_arr]
            largest = int(np.argmax(sizes)) + 1
            body = (labeled == largest).astype(np.uint8)
            result.nuqtah_components = num_features - 1
        else:
            body = binary
            result.nuqtah_components = 0

        result.body_pixels = int(np.sum(body))
        skeleton = zhang_suen_thin(body)
        result.skeleton_pixels = int(np.sum(skeleton))

        nodes, edges = build_skeleton_graph(skeleton)

        # Prune short branches
        endpoints = {n.id for n in nodes if n.degree == 1}
        edges = [e for e in edges if not (e.length <= 3 and (e.u in endpoints or e.v in endpoints))]

        result.nodes = nodes
        result.edges = edges

    except Exception as e:
        result.error = str(e)

    result.processing_time_ms = (time.perf_counter() - t0) * 1000
    return result


def process_all(glyph_dir: Optional[str] = None, verbose: bool = True) -> List[CSGiResult]:
    """Process all 28 letters."""
    results: List[CSGiResult] = []
    entries = MASTER_TABLE.all_entries()

    if verbose:
        print(f"CSGi Pipeline — {len(entries)} letters")
        print("=" * 60)

    for i, entry in enumerate(entries):
        r = process_letter(entry, glyph_dir)
        if verbose:
            status = "OK" if r.error is None else f"ERR: {r.error}"
            print(
                f"  [{i+1:2d}/{len(entries)}] {entry.char} ({entry.name:<8s}) "
                f"n={len(r.nodes):<3d} e={len(r.edges):<3d} "
                f"{r.processing_time_ms:6.1f}ms  {status}"
            )
        results.append(r)

    if verbose:
        ok = sum(1 for r in results if r.error is None)
        ms = sum(r.processing_time_ms for r in results)
        print(f"  Done: {ok}/{len(entries)} OK, {ms:.0f}ms total")

    return results


# ── CLI ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="CSGi Pipeline")
    parser.add_argument("--letter", "-l", type=str)
    parser.add_argument("--index", "-i", type=int)
    parser.add_argument("--output", "-o", type=str)
    parser.add_argument("--glyph-dir", "-g", type=str)
    parser.add_argument("--verify", "-v", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", "-q", action="store_true")
    args = parser.parse_args()

    if not HAS_IMAGING:
        print("ERROR: pip install numpy Pillow scipy")
        sys.exit(1)

    if args.letter:
        entry = MASTER_TABLE.get_by_char(args.letter)
        if entry is None:
            print(f"Unknown letter: {args.letter}")
            sys.exit(1)
        print(process_letter(entry, args.glyph_dir).to_json())
        return

    if args.index:
        entry = MASTER_TABLE.get_by_index(args.index)
        if entry is None:
            print(f"Invalid index: {args.index}")
            sys.exit(1)
        print(process_letter(entry, args.glyph_dir).to_json())
        return

    results = process_all(args.glyph_dir, not args.quiet)

    if args.verify:
        print("\nVERIFY: CSGi vs Master Table")
        for r in results:
            if r.error:
                continue
            entry = MASTER_TABLE.get_by_char(r.letter)
            if entry is None:
                continue
            mt_an = entry.vector[14]
            match = "✓" if r.nuqtah_components == mt_an else "✗"
            print(f"  {r.letter} dots={r.nuqtah_components} MT={mt_an} {match}")

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False))

    if args.output:
        out = Path(args.output)
        out.mkdir(parents=True, exist_ok=True)
        for r in results:
            p = out / f"{r.index:02d}_{r.name.lower()}.json"
            p.write_text(r.to_json(), encoding="utf-8")
        if not args.quiet:
            print(f"Saved to {out}/")


if __name__ == "__main__":
    main()
