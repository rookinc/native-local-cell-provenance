#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_002 = ROOT / "artifacts/json/source_ledger_and_target_alignment_002.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_c_path_literal_test_003.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_c_path_literal_test_003.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_c_path_literal_test_003.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_edges(path):
    edges = set()
    vertices = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            u = int(row["local_u"])
            v = int(row["local_v"])
            a, b = sorted((u, v))
            edges.add((a, b))
            vertices.add(u)
            vertices.add(v)
    return edges, vertices


def has_edge(edges, u, v):
    a, b = sorted((u, v))
    return (a, b) in edges


def main():
    a002 = load_json(IN_002)
    edges, vertices = load_edges(G60_EDGES)

    c_paths = a002["local_cell_target"]["c_paths"]

    rows = []
    per_state = {}

    for state, path in c_paths.items():
        path_edges = []
        literal_flags = []
        for i in range(len(path) - 1):
            u = int(path[i])
            v = int(path[i + 1])
            ok = has_edge(edges, u, v)
            literal_flags.append(ok)
            path_edges.append({
                "state": state,
                "step": i,
                "u": u,
                "v": v,
                "literal_g60_edge": ok,
            })
            rows.append(path_edges[-1])

        per_state[state] = {
            "path": path,
            "edge_count": len(literal_flags),
            "literal_edge_count": sum(1 for x in literal_flags if x),
            "all_edges_literal": all(literal_flags),
            "any_edge_literal": any(literal_flags),
            "literal_flags": literal_flags,
        }

    total_tested_edges = len(rows)
    total_literal_edges = sum(1 for r in rows if r["literal_g60_edge"])

    checks = {
        "source_ledger_ready": bool(a002.get("ready_for_native_search")),
        "g60_payload_exists": G60_EDGES.exists(),
        "g60_edge_count_is_120": len(edges) == 120,
        "g60_vertex_count_is_60": len(vertices) == 60,
        "tested_c_path_edge_count_is_12": total_tested_edges == 12,
    }

    result = {
        "status": "native_g60_c_path_literal_test_recorded",
        "audit_id": "003",
        "inputs": {
            "source_ledger_002": str(IN_002),
            "g60_edges": str(G60_EDGES),
        },
        "g60_edge_count": len(edges),
        "g60_vertex_count": len(vertices),
        "total_tested_c_path_edges": total_tested_edges,
        "total_literal_g60_edges": total_literal_edges,
        "literal_fraction": total_literal_edges / total_tested_edges if total_tested_edges else None,
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "literal_c_paths_all_pass": all(x["all_edges_literal"] for x in per_state.values()),
        "literal_c_paths_any_support": any(x["any_edge_literal"] for x in per_state.values()),
        "interpretation": (
            "This tests whether the Project 22 C paths are literal paths in the copied canonical G60 local edge payload. "
            "A failure here does not refute the local cell; it means the C paths are likely quotient-visible, transition-overlay, "
            "or provenance-field paths rather than literal G60 adjacency paths."
        ),
        "boundary": (
            "This is only a literal-edge test against the copied G60 local edge payload. It does not test quotient paths, "
            "station provenance paths, lifted masks, or the full role-labeled shared_B universe, and it does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["state", "step", "u", "v", "literal_g60_edge"])
        for r in rows:
            w.writerow([r["state"], r["step"], r["u"], r["v"], "1" if r["literal_g60_edge"] else "0"])

    lines = []
    lines.append("# Native G60 C path literal test 003")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Do the Project 22 C paths appear as literal paths in the copied canonical G60 local edge payload?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- g60_edge_count: `" + str(len(edges)) + "`")
    lines.append("- g60_vertex_count: `" + str(len(vertices)) + "`")
    lines.append("- total_tested_c_path_edges: `" + str(total_tested_edges) + "`")
    lines.append("- total_literal_g60_edges: `" + str(total_literal_edges) + "`")
    lines.append("- literal_c_paths_all_pass: `" + str(result["literal_c_paths_all_pass"]) + "`")
    lines.append("- literal_c_paths_any_support: `" + str(result["literal_c_paths_any_support"]) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state, info in per_state.items():
        lines.append("- " + state + ": path `" + str(info["path"]) + "`, literal_flags `" + str(info["literal_flags"]) + "`, all_edges_literal `" + str(info["all_edges_literal"]) + "`")
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
    print("g60_edge_count", len(edges))
    print("g60_vertex_count", len(vertices))
    print("total_tested_c_path_edges", total_tested_edges)
    print("total_literal_g60_edges", total_literal_edges)
    print("literal_c_paths_all_pass", result["literal_c_paths_all_pass"])
    print("literal_c_paths_any_support", result["literal_c_paths_any_support"])


if __name__ == "__main__":
    main()
