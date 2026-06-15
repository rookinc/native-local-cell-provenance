#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_012 = ROOT / "source/project22_artifacts/json/lift_twist_anchor_node_path_geometry_012.v1.json"
IN_014 = ROOT / "artifacts/json/c_path_cover_paper_boundary_audit_014.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_node_path_edge_support_015.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_node_path_edge_support_015.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_node_path_edge_support_015.md"

STATES = {"O0", "O1", "B0", "B1"}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_edges(path):
    edges = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            u = int(row["local_u"])
            v = int(row["local_v"])
            edges.add(tuple(sorted((u, v))))
    return edges


def is_int_pair(x):
    return isinstance(x, list) and len(x) == 2 and all(isinstance(y, int) for y in x)


def is_pair_path(x):
    return isinstance(x, list) and len(x) >= 3 and all(is_int_pair(y) for y in x)


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def find_anchor_paths(a012):
    found = {}
    for d in walk(a012):
        state = d.get("state")
        if state not in STATES:
            continue

        candidates = []
        for k, v in d.items():
            if is_pair_path(v):
                score = 0
                lk = str(k).lower()
                if "anchor" in lk:
                    score += 3
                if "closed" in lk:
                    score += 5
                if "path" in lk:
                    score += 5
                if v[0] == v[-1]:
                    score += 3
                candidates.append((score, k, v))

        if candidates:
            candidates.sort(key=lambda x: (-x[0], str(x[1])))
            found[state] = {
                "source_key": candidates[0][1],
                "closed_path": candidates[0][2],
            }

    missing = sorted(STATES.difference(found.keys()))
    if missing:
        raise SystemExit("missing anchor paths for states: " + str(missing))
    return found


def pair_internal_edge(pair, edges):
    return tuple(sorted(pair)) in edges


def cross_edges(pair_a, pair_b, edges):
    out = []
    for u in pair_a:
        for v in pair_b:
            if u == v:
                continue
            e = tuple(sorted((int(u), int(v))))
            if e in edges:
                out.append([int(u), int(v)])
    return out


def main():
    a012 = load_json(IN_012)
    a014 = load_json(IN_014)
    edges = load_edges(G60_EDGES)

    if not a012.get("theorem_pass"):
        raise SystemExit("Project22 012 theorem_pass is not true")
    if not a014.get("boundary_pass"):
        raise SystemExit("014 boundary_pass is not true")

    paths = find_anchor_paths(a012)

    rows = []
    per_state = {}

    for state in ["O0", "O1", "B0", "B1"]:
        rec = paths[state]
        path = rec["closed_path"]

        internal = []
        for idx, pair in enumerate(path):
            internal.append({
                "pair_index": idx,
                "pair": pair,
                "internal_edge_supported": pair_internal_edge(pair, edges),
            })

        steps = []
        for idx in range(len(path) - 1):
            pair_a = path[idx]
            pair_b = path[idx + 1]
            xs = cross_edges(pair_a, pair_b, edges)
            step = {
                "state": state,
                "step": idx,
                "from_pair": pair_a,
                "to_pair": pair_b,
                "cross_edge_count": len(xs),
                "cross_edges": xs,
                "step_supported": len(xs) > 0,
            }
            rows.append(step)
            steps.append(step)

        per_state[state] = {
            "source_key": rec["source_key"],
            "closed_path": path,
            "internal_pair_support": internal,
            "step_support": steps,
            "all_steps_supported": all(x["step_supported"] for x in steps),
            "any_steps_supported": any(x["step_supported"] for x in steps),
            "supported_step_count": sum(1 for x in steps if x["step_supported"]),
            "total_step_count": len(steps),
            "internal_supported_count": sum(1 for x in internal if x["internal_edge_supported"]),
            "internal_total_count": len(internal),
        }

    total_steps = len(rows)
    supported_steps = sum(1 for x in rows if x["step_supported"])

    checks = {
        "project22_012_theorem_pass": bool(a012.get("theorem_pass")),
        "paper_boundary_014_pass": bool(a014.get("boundary_pass")),
        "g60_edge_count_is_120": len(edges) == 120,
        "state_count_is_4": sorted(paths.keys()) == ["B0", "B1", "O0", "O1"],
        "total_anchor_path_step_count_is_12": total_steps == 12,
        "all_states_have_three_anchor_steps": all(per_state[s]["total_step_count"] == 3 for s in per_state),
    }

    result = {
        "status": "native_g60_anchor_node_path_edge_support_recorded",
        "audit_id": "015",
        "inputs": {
            "project22_anchor_path_012": str(IN_012),
            "paper_boundary_014": str(IN_014),
            "g60_edges": str(G60_EDGES),
        },
        "g60_edge_count": len(edges),
        "total_anchor_path_step_count": total_steps,
        "supported_anchor_path_step_count": supported_steps,
        "unsupported_anchor_path_step_count": total_steps - supported_steps,
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "all_anchor_pair_steps_supported": supported_steps == total_steps,
        "interpretation": (
            "This tests whether the inherited Project 22 closed anchor node paths are literal pair-walks in canonical G60. "
            "A supported pair step means at least one native G60 edge crosses between consecutive node pairs. "
            "If support is partial or absent, the anchor paths are likely not simple native G60 pair-walks and require a "
            "different provenance layer such as station fields, lifted masks, or quotient-pair geometry."
        ),
        "boundary": (
            "This is only a literal G60 edge-support audit for inherited anchor node paths. It does not derive anchor paths "
            "or lift masks from native provenance, does not select unique relay mediators, does not derive the full role-labeled "
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
            "from_pair",
            "to_pair",
            "step_supported",
            "cross_edge_count",
            "cross_edges",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["step"],
                " ".join(str(x) for x in r["from_pair"]),
                " ".join(str(x) for x in r["to_pair"]),
                "1" if r["step_supported"] else "0",
                r["cross_edge_count"],
                json.dumps(r["cross_edges"], sort_keys=True),
            ])

    lines = []
    lines.append("# Native G60 anchor node path edge support 015")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Are the Project 22 closed anchor node paths literal pair-walks in canonical G60?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- all_checks_pass: `" + str(result["all_checks_pass"]) + "`")
    lines.append("- total_anchor_path_step_count: `" + str(total_steps) + "`")
    lines.append("- supported_anchor_path_step_count: `" + str(supported_steps) + "`")
    lines.append("- unsupported_anchor_path_step_count: `" + str(total_steps - supported_steps) + "`")
    lines.append("- all_anchor_pair_steps_supported: `" + str(result["all_anchor_pair_steps_supported"]) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in ["O0", "O1", "B0", "B1"]:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - closed_path: `" + str(p["closed_path"]) + "`")
        lines.append("  - supported_step_count: `" + str(p["supported_step_count"]) + "/" + str(p["total_step_count"]) + "`")
        lines.append("  - internal_supported_count: `" + str(p["internal_supported_count"]) + "/" + str(p["internal_total_count"]) + "`")
        for step in p["step_support"]:
            lines.append(
                "  - step "
                + str(step["step"])
                + " `"
                + str(step["from_pair"])
                + " -> "
                + str(step["to_pair"])
                + "`: cross_edge_count `"
                + str(step["cross_edge_count"])
                + "`, edges `"
                + str(step["cross_edges"])
                + "`"
            )
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
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
    print("total_anchor_path_step_count", total_steps)
    print("supported_anchor_path_step_count", supported_steps)
    print("unsupported_anchor_path_step_count", total_steps - supported_steps)
    print("all_anchor_pair_steps_supported", result["all_anchor_pair_steps_supported"])


if __name__ == "__main__":
    main()
