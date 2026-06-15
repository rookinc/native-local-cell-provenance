#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_002 = ROOT / "artifacts/json/source_ledger_and_target_alignment_002.v1.json"
IN_003 = ROOT / "artifacts/json/native_g60_c_path_literal_test_003.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_c_path_residue_support_004.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_c_path_residue_support_004.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_c_path_residue_support_004.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_edges(path):
    edges = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            u = int(row["local_u"])
            v = int(row["local_v"])
            edges.append((u, v))
    return edges


def main():
    a002 = load_json(IN_002)
    a003 = load_json(IN_003)
    edges = load_edges(G60_EDGES)

    c_paths = a002["local_cell_target"]["c_paths"]

    residue_edges = defaultdict(list)
    undirected_residue_edges = defaultdict(list)

    for u, v in edges:
        ru = u % 15
        rv = v % 15
        residue_edges[(ru, rv)].append((u, v))
        residue_edges[(rv, ru)].append((v, u))
        key = tuple(sorted((ru, rv)))
        undirected_residue_edges[key].append((u, v))

    rows = []
    per_state = {}

    for state, path in c_paths.items():
        flags_directed = []
        flags_undirected = []
        support_counts_directed = []
        support_counts_undirected = []

        for i in range(len(path) - 1):
            a = int(path[i])
            b = int(path[i + 1])

            directed_support = residue_edges.get((a, b), [])
            undirected_support = undirected_residue_edges.get(tuple(sorted((a, b))), [])

            directed_ok = len(directed_support) > 0
            undirected_ok = len(undirected_support) > 0

            flags_directed.append(directed_ok)
            flags_undirected.append(undirected_ok)
            support_counts_directed.append(len(directed_support))
            support_counts_undirected.append(len(undirected_support))

            rows.append({
                "state": state,
                "step": i,
                "from_c": a,
                "to_c": b,
                "directed_residue_support_count": len(directed_support),
                "undirected_residue_support_count": len(undirected_support),
                "directed_residue_supported": directed_ok,
                "undirected_residue_supported": undirected_ok,
                "directed_examples": directed_support[:6],
                "undirected_examples": undirected_support[:6],
            })

        per_state[state] = {
            "path": path,
            "directed_flags": flags_directed,
            "undirected_flags": flags_undirected,
            "directed_support_counts": support_counts_directed,
            "undirected_support_counts": support_counts_undirected,
            "all_directed_supported": all(flags_directed),
            "all_undirected_supported": all(flags_undirected),
            "any_directed_supported": any(flags_directed),
            "any_undirected_supported": any(flags_undirected),
        }

    total_steps = len(rows)
    directed_supported_count = sum(1 for r in rows if r["directed_residue_supported"])
    undirected_supported_count = sum(1 for r in rows if r["undirected_residue_supported"])

    checks = {
        "source_ledger_ready": bool(a002.get("ready_for_native_search")),
        "literal_test_003_checks_passed": bool(a003.get("all_checks_pass")),
        "literal_test_003_found_zero_literal_edges": a003.get("total_literal_g60_edges") == 0,
        "g60_edge_count_is_120": len(edges) == 120,
        "tested_c_path_edge_count_is_12": total_steps == 12,
    }

    result = {
        "status": "native_g60_c_path_residue_support_recorded",
        "audit_id": "004",
        "inputs": {
            "source_ledger_002": str(IN_002),
            "literal_test_003": str(IN_003),
            "g60_edges": str(G60_EDGES),
        },
        "g60_edge_count": len(edges),
        "total_tested_c_path_steps": total_steps,
        "directed_residue_supported_count": directed_supported_count,
        "undirected_residue_supported_count": undirected_supported_count,
        "directed_residue_support_fraction": directed_supported_count / total_steps if total_steps else None,
        "undirected_residue_support_fraction": undirected_supported_count / total_steps if total_steps else None,
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "all_c_paths_directed_residue_supported": all(x["all_directed_supported"] for x in per_state.values()),
        "all_c_paths_undirected_residue_supported": all(x["all_undirected_supported"] for x in per_state.values()),
        "any_c_path_directed_residue_supported": any(x["any_directed_supported"] for x in per_state.values()),
        "any_c_path_undirected_residue_supported": any(x["any_undirected_supported"] for x in per_state.values()),
        "interpretation": (
            "This tests whether Project 22 C-path transitions are supported after projecting native G60 vertices "
            "to residues mod 15. Positive support would suggest the C paths are quotient-visible rather than literal "
            "vertex-adjacency paths. Negative support would push the search toward station provenance or transition overlays."
        ),
        "boundary": (
            "This is only a residue-projection support test using vertex mod 15. It does not prove native local-cell "
            "provenance, does not test all possible quotient maps or station fields, does not derive the full role-labeled "
            "shared_B universe, and does not close Gap A."
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
            "directed_residue_supported",
            "directed_residue_support_count",
            "undirected_residue_supported",
            "undirected_residue_support_count",
            "directed_examples",
            "undirected_examples",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["step"],
                r["from_c"],
                r["to_c"],
                "1" if r["directed_residue_supported"] else "0",
                r["directed_residue_support_count"],
                "1" if r["undirected_residue_supported"] else "0",
                r["undirected_residue_support_count"],
                " ".join(str(x) for x in r["directed_examples"]),
                " ".join(str(x) for x in r["undirected_examples"]),
            ])

    lines = []
    lines.append("# Native G60 C path residue support 004")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Do the Project 22 C-path steps appear as residue-class transitions after projecting native G60 vertices mod 15?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- total_tested_c_path_steps: `" + str(total_steps) + "`")
    lines.append("- directed_residue_supported_count: `" + str(directed_supported_count) + "`")
    lines.append("- undirected_residue_supported_count: `" + str(undirected_supported_count) + "`")
    lines.append("- all_c_paths_directed_residue_supported: `" + str(result["all_c_paths_directed_residue_supported"]) + "`")
    lines.append("- all_c_paths_undirected_residue_supported: `" + str(result["all_c_paths_undirected_residue_supported"]) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state, info in per_state.items():
        lines.append("- " + state + ": path `" + str(info["path"]) + "`")
        lines.append("  - directed_flags: `" + str(info["directed_flags"]) + "`")
        lines.append("  - directed_support_counts: `" + str(info["directed_support_counts"]) + "`")
        lines.append("  - undirected_flags: `" + str(info["undirected_flags"]) + "`")
        lines.append("  - undirected_support_counts: `" + str(info["undirected_support_counts"]) + "`")
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
    print("total_tested_c_path_steps", total_steps)
    print("directed_residue_supported_count", directed_supported_count)
    print("undirected_residue_supported_count", undirected_supported_count)
    print("all_c_paths_directed_residue_supported", result["all_c_paths_directed_residue_supported"])
    print("all_c_paths_undirected_residue_supported", result["all_c_paths_undirected_residue_supported"])


if __name__ == "__main__":
    main()
