"""Skeleton graph contraction: pixel skeleton → node/edge graph."""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

import numpy as np

from .csgi import CSGIEdge, CSGIGraph, CSGINode


class SkeletonContractor:
    """Contracts a skeleton image into a CSGi graph."""

    def __init__(
        self,
        letter_hijaiyyah: str = "",
        letter_name: str = "",
        release_id: str = "",
    ) -> None:
        self.letter = letter_hijaiyyah
        self.name = letter_name
        self.release = release_id

    def contract(self, skeleton: np.ndarray) -> CSGIGraph:
        """
        Contract skeleton pixels into a graph.

        Nodes: pixels with degree != 2 (endpoints and junctions)
        Edges: polylines connecting nodes through degree-2 pixels
        """
        rows, cols = skeleton.shape
        nodes: List[CSGINode] = []
        edges: List[CSGIEdge] = []
        node_map: Dict[Tuple[int, int], int] = {}
        node_id = 0

        # ── Step 1: find all skeleton pixels and compute degrees ──
        pixel_degree: Dict[Tuple[int, int], int] = {}
        all_points: List[Tuple[int, int]] = []

        for y in range(rows):
            for x in range(cols):
                if skeleton[y, x] == 0:
                    continue
                all_points.append((int(y), int(x)))
                count = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols:
                            if skeleton[ny, nx] > 0:
                                count += 1
                pixel_degree[(int(y), int(x))] = count

        # ── Step 2: identify nodes (degree != 2) ─────────────────
        for (y, x), deg in pixel_degree.items():
            if deg != 2:
                node = CSGINode(
                    id=int(node_id),
                    x=int(x),
                    y=int(y),
                    degree=int(deg),
                )
                nodes.append(node)
                node_map[(y, x)] = node_id
                node_id += 1

        # ── Step 3: trace edges between nodes ────────────────────
        visited_edges: Set[Tuple[int, int]] = set()
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

                    # Trace path
                    path: List[Tuple[int, int]] = [(sx, sy), (nx, ny)]
                    current = (ny, nx)
                    prev = (sy, sx)
                    reached_node = False

                    while True:
                        if current in node_map and current != start_pos:
                            reached_node = True
                            break

                        if current not in pixel_degree:
                            break

                        cy, cx = current
                        found_next = False

                        for ddy in (-1, 0, 1):
                            for ddx in (-1, 0, 1):
                                if ddy == 0 and ddx == 0:
                                    continue
                                nny = int(cy + ddy)
                                nnx = int(cx + ddx)
                                if (nny, nnx) == prev:
                                    continue
                                if (nny, nnx) in pixel_degree:
                                    path.append((nnx, nny))
                                    prev = current
                                    current = (nny, nnx)
                                    found_next = True
                                    break
                            if found_next:
                                break

                        if not found_next:
                            break

                    if reached_node and current in node_map:
                        end_nid = node_map[current]
                        edge_key = (
                            min(start_nid, end_nid),
                            max(start_nid, end_nid),
                        )
                        if edge_key not in visited_edges:
                            visited_edges.add(edge_key)
                            edge = CSGIEdge(
                                id=int(edge_id),
                                u=int(start_nid),
                                v=int(end_nid),
                                points=[(int(px), int(py)) for px, py in path],
                            )
                            edges.append(edge)
                            edge_id += 1

        # ── Handle empty case ────────────────────────────────────
        if not nodes and all_points:
            y, x = all_points[0]
            nodes.append(CSGINode(id=0, x=int(x), y=int(y), degree=0))

        return CSGIGraph(
            letter=self.letter,
            name=self.name,
            nodes=nodes,
            edges=edges,
            adjacency="8-neighborhood",
            release_id=self.release,
        )
