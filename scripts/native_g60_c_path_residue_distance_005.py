#!/usr/bin/env python3
import csv
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_002 = ROOT / "artifacts/json/source_ledger_and_target_alignment_002.v1.json"
IN_004 = ROOT / "artifacts/json/native_g60_c_path_residue_support_004.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_c_path_residue_distance_005.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_c_path_residue_distance_005.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_c_path_residue_distance_005.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_edges(path):
    edges = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            edges.append((int(row["local_u"]), int(row["local_v"])))
    return edges


def shortest_path(adj, start, goal):
    if start == goal:
        return [start]
    q = deque([start])
    prev = {start: None}
    while q:
        x = q.popleft()
        for y in sorted(adj[x]):
            if y in prev:
                continue
            prev[y] = x
            if y == goal:
                path = [y]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                return list(reversed(path))
            q.append(y)
    return None


def main():
    a002 = load_json(IN_002)
    a004 = load_json(IN_004)
    edges = load_edges(G60_EDGES)

    c_paths = a002["local_cell_target"]["c_paths"]

    adj = defaultdict(set)
    edge_support = defaultdict(list)

    for u, v in edges:
        ru = u % 15
        rv = v % 15
        adj[ru].add(rv)
        adj[rv].add(ru)
        edge_support[tuple(sorted((ru, rv)))].append((u, v))

    residues = sorted(set(range(15)) | set(adj.keys()))

    rows = []
    distance_counts = defaultdict(int)
    per_state = {}

    for state, path in c_paths.items():
        state_rows = []
        for i in range(len(path) - 1):
            a = int(path[i])
            b = int(path[i + 1])
            sp = shortest_path(adj, a, b)
            dist = None if sp is None else len(sp) - 1
            direct_key = tuple(sorted((a, b)))
            direct_support_count = len(edge_support.get(direct_key, []))

            row = {
                "state": state,
                "step": i,
                "from_c": a,
                "to_c": b,
                "residue_distance": dist,
                "residue_shortest_path": sp,
                "direct_support_count": direct_support_count,
                "direct_supported": direct_support_count > 0,
            }
            rows.append(row)
            state_rows.append(row)
            distance_counts[str(dist)] += 1

        per_state[state] = {
            "path": path,
            "distances": [r["residue_distance"] for r in state_rows],
            "shortest_paths": [r["residue_shortest_path"] for r in state_rows],
            "max_distance": max(r["residue_distance"] for r in state_rows if r["residue_distance"] is not None),
            "all_reachable": all(r["residue_distance"] is not None for r in state_rows),
        }

    all_distances = [r["residue_distance"] for r in rows]
    finite_distances = [d for d in all_distances if d is not None]

    checks = {
        "source_ledger_ready": bool(a002.get("ready_for_native_search")),
        "residue_support_004_checks_passed": bool(a004.get("all_checks_pass")),
        "g60_edge_count_is_120": len(edges) == 120,
        "residue_vertex_count_is_15": len(residues) == 15,
        "tested_c_path_step_count_is_12": len(rows) == 12,
        "all_target_residue_steps_reachable": len(finite_distances) == len(rows),
    }

    result = {
        "status": "native_g60_c_path_residue_distance_recorded",
        "audit_id": "005",
        "inputs": {
            "source_ledger_002": str(IN_002),
            "residue_support_004": str(IN_004),
            "g60_edges": str(G60_EDGES),
        },
        "g60_edge_count": len(edges),
        "residue_vertex_count": len(residues),
        "residue_vertices": residues,
        "target_step_count": len(rows),
        "distance_counts": dict(sorted(distance_counts.items())),
        "max_finite_distance": max(finite_distances) if finite_distances else None,
        "rows": rows,
        "per_state": per_state,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "This tests whether C-path transitions that are not direct mod15 residue edges are nevertheless nearby in the "
            "residue quotient graph induced by canonical G60 edges. If all target transitions have small quotient distance, "
            "the C paths may be quotient-walk or closure paths rather than literal edges. If distances are large or unreachable, "
            "the mod15 residue quotient is probably the wrong native support layer."
        ),
        "boundary": (
            "This is only a shortest-path audit in the simple vertex mod15 residue quotient. It does not derive native local-cell "
            "provenance, does not test station provenance fields, lifted masks, or alternate quotient maps, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "state",
            "step",
            "from_c",
            "to_c",
            "residue_distance",
            "residue_shortest_path",
            "direct_supported",
            "direct_support_count",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["step"],
                r["from_c"],
                r["to_c"],
                r["residue_distance"],
                " ".join(str(x) for x in r["residue_shortest_path"]) if r["residue_shortest_path"] else "none",
                "1" if r["direct_supported"] else "0",
                r["direct_support_count"],
            ])

    lines = []
    lines.append("# Native G60 C path residue distance 005")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("When a Project 22 C-path transition is not a direct mod15 residue edge, is it still nearby in the residue quotient graph?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- target_step_count: `" + str(len(rows)) + "`")
    lines.append("- distance_counts: `" + str(result["distance_counts"]) + "`")
    lines.append("- max_finite_distance: `" + str(result["max_finite_distance"]) + "`")
    lines.append("- all_target_residue_steps_reachable: `" + str(checks["all_target_residue_steps_reachable"]) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state, info in per_state.items():
        lines.append("- " + state + ":")
        lines.append("  - path: `" + str(info["path"]) + "`")
        lines.append("  - distances: `" + str(info["distances"]) + "`")
        lines.append("  - shortest_paths: `" + str(info["shortest_paths"]) + "`")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(result["interpretation"])
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(result["boundary"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("all_checks_pass", result["all_checks_pass"])
    print("distance_counts", result["distance_counts"])
    print("max_finite_distance", result["max_finite_distance"])
    print("all_target_residue_steps_reachable", checks["all_target_residue_steps_reachable"])


if __name__ == "__main__":
    main()
