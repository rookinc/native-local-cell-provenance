#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_012 = ROOT / "source/project22_artifacts/json/lift_twist_anchor_node_path_geometry_012.v1.json"
IN_015 = ROOT / "artifacts/json/native_g60_anchor_node_path_edge_support_015.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_node_path_residue_pair_support_016.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_node_path_residue_pair_support_016.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_node_path_residue_pair_support_016.md"

STATES = {"O0", "O1", "B0", "B1"}


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


def pair_residues(pair):
    return sorted({int(x) % 15 for x in pair})


def main():
    a012 = load_json(IN_012)
    a015 = load_json(IN_015)
    g60_edges = load_edges(G60_EDGES)

    if not a012.get("theorem_pass"):
        raise SystemExit("Project22 012 theorem_pass is not true")
    if not a015.get("all_checks_pass"):
        raise SystemExit("015 all_checks_pass is not true")

    residue_support = {}
    for u, v in g60_edges:
        ru = u % 15
        rv = v % 15
        key = tuple(sorted((ru, rv)))
        residue_support.setdefault(key, []).append((u, v))

    paths = find_anchor_paths(a012)

    rows = []
    per_state = {}

    for state in ["O0", "O1", "B0", "B1"]:
        path = paths[state]["closed_path"]
        state_rows = []

        for step in range(len(path) - 1):
            from_pair = path[step]
            to_pair = path[step + 1]
            from_res = pair_residues(from_pair)
            to_res = pair_residues(to_pair)

            hits = []
            for a in from_res:
                for b in to_res:
                    key = tuple(sorted((a, b)))
                    examples = residue_support.get(key, [])
                    if examples:
                        hits.append({
                            "from_residue": a,
                            "to_residue": b,
                            "support_count": len(examples),
                            "examples": examples[:8],
                        })

            row = {
                "state": state,
                "step": step,
                "from_pair": from_pair,
                "to_pair": to_pair,
                "from_residues": from_res,
                "to_residues": to_res,
                "residue_cross_support_count": sum(h["support_count"] for h in hits),
                "residue_cross_hit_count": len(hits),
                "residue_pair_supported": len(hits) > 0,
                "hits": hits,
            }
            rows.append(row)
            state_rows.append(row)

        per_state[state] = {
            "closed_path": path,
            "step_count": len(state_rows),
            "supported_step_count": sum(1 for x in state_rows if x["residue_pair_supported"]),
            "all_steps_supported": all(x["residue_pair_supported"] for x in state_rows),
            "any_steps_supported": any(x["residue_pair_supported"] for x in state_rows),
            "steps": state_rows,
        }

    total_steps = len(rows)
    supported_steps = sum(1 for x in rows if x["residue_pair_supported"])

    checks = {
        "project22_012_theorem_pass": bool(a012.get("theorem_pass")),
        "literal_anchor_support_015_checks_pass": bool(a015.get("all_checks_pass")),
        "g60_edge_count_is_120": len(g60_edges) == 120,
        "state_count_is_4": sorted(paths.keys()) == ["B0", "B1", "O0", "O1"],
        "total_anchor_pair_step_count_is_12": total_steps == 12,
    }

    result = {
        "status": "native_g60_anchor_node_path_residue_pair_support_recorded",
        "audit_id": "016",
        "inputs": {
            "project22_anchor_path_012": str(IN_012),
            "literal_anchor_support_015": str(IN_015),
            "g60_edges": str(G60_EDGES),
        },
        "total_anchor_pair_step_count": total_steps,
        "supported_residue_pair_step_count": supported_steps,
        "unsupported_residue_pair_step_count": total_steps - supported_steps,
        "all_anchor_residue_pair_steps_supported": supported_steps == total_steps,
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "This tests whether the Project 22 closed anchor node paths become supported after projecting G60 vertices "
            "to mod15 residue pairs. If support rises relative to artifact 015, the anchor paths may be quotient-pair paths "
            "rather than literal G60 pair-walks."
        ),
        "boundary": (
            "This is only a mod15 residue-pair support audit. It does not derive anchor paths or lift masks from native "
            "provenance, does not test station fields, does not select unique relay mediators, does not derive the full "
            "role-labeled shared_B universe, and does not close Gap A."
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
            "from_residues",
            "to_residues",
            "residue_pair_supported",
            "residue_cross_hit_count",
            "residue_cross_support_count",
            "hits",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["step"],
                " ".join(str(x) for x in r["from_pair"]),
                " ".join(str(x) for x in r["to_pair"]),
                " ".join(str(x) for x in r["from_residues"]),
                " ".join(str(x) for x in r["to_residues"]),
                "1" if r["residue_pair_supported"] else "0",
                r["residue_cross_hit_count"],
                r["residue_cross_support_count"],
                json.dumps(r["hits"], sort_keys=True),
            ])

    lines = []
    lines.append("# Native G60 anchor node path residue-pair support 016")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Are the Project 22 closed anchor node paths supported as mod15 residue-pair walks?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- all_checks_pass: `" + str(result["all_checks_pass"]) + "`")
    lines.append("- total_anchor_pair_step_count: `" + str(total_steps) + "`")
    lines.append("- supported_residue_pair_step_count: `" + str(supported_steps) + "`")
    lines.append("- unsupported_residue_pair_step_count: `" + str(total_steps - supported_steps) + "`")
    lines.append("- all_anchor_residue_pair_steps_supported: `" + str(result["all_anchor_residue_pair_steps_supported"]) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in ["O0", "O1", "B0", "B1"]:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - closed_path: `" + str(p["closed_path"]) + "`")
        lines.append("  - supported_step_count: `" + str(p["supported_step_count"]) + "/" + str(p["step_count"]) + "`")
        for step in p["steps"]:
            lines.append(
                "  - step "
                + str(step["step"])
                + " residues `"
                + str(step["from_residues"])
                + " -> "
                + str(step["to_residues"])
                + "`: supported `"
                + str(step["residue_pair_supported"])
                + "`, hit_count `"
                + str(step["residue_cross_hit_count"])
                + "`, support_count `"
                + str(step["residue_cross_support_count"])
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
    print("total_anchor_pair_step_count", total_steps)
    print("supported_residue_pair_step_count", supported_steps)
    print("unsupported_residue_pair_step_count", total_steps - supported_steps)
    print("all_anchor_residue_pair_steps_supported", result["all_anchor_residue_pair_steps_supported"])


if __name__ == "__main__":
    main()
