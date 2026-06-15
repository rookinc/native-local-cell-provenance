#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_008 = ROOT / "artifacts/json/native_g60_c_relay_anchor_mediation_008.v1.json"
IN_012 = ROOT / "source/project22_artifacts/json/lift_twist_anchor_node_path_geometry_012.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_path_mediator_position_009.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_path_mediator_position_009.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_path_mediator_position_009.md"

STATES = {"O0", "O1", "B0", "B1"}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def is_int_pair(x):
    return (
        isinstance(x, list)
        and len(x) == 2
        and all(isinstance(y, int) for y in x)
    )


def is_pair_path(x):
    return (
        isinstance(x, list)
        and len(x) >= 3
        and all(is_int_pair(y) for y in x)
    )


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
        raise SystemExit("missing anchor closed paths for states: " + str(missing))

    return found


def residue_positions(path):
    out = {}
    for pair_index, pair in enumerate(path):
        for node_index, node in enumerate(pair):
            residue = int(node) % 15
            out.setdefault(residue, []).append({
                "pair_index": pair_index,
                "node_index": node_index,
                "node": int(node),
                "pair": [int(pair[0]), int(pair[1])],
            })
    return out


def main():
    a008 = load_json(IN_008)
    a012 = load_json(IN_012)

    if not a008.get("theorem_pass"):
        raise SystemExit("008 theorem_pass is not true")
    if not a012.get("theorem_pass"):
        raise SystemExit("Project22 012 theorem_pass is not true")

    anchor_paths = find_anchor_paths(a012)

    path_profiles = {}
    for state, rec in anchor_paths.items():
        path = rec["closed_path"]
        pos = residue_positions(path)
        path_profiles[state] = {
            "source_key": rec["source_key"],
            "closed_path": path,
            "closed_path_residue_set": sorted(pos.keys()),
            "residue_positions": pos,
        }

    rows = []
    state_transition_profiles = {}

    for r in a008["rows"]:
        state = r["state"]
        hits = [int(x) for x in r["anchor_mediator_hits"]]
        pos = path_profiles[state]["residue_positions"]

        hit_records = []
        hit_pair_indices = []
        hit_node_pairs = []

        for h in hits:
            positions = pos.get(h, [])
            for p in positions:
                hit_records.append({
                    "hit": h,
                    "pair_index": p["pair_index"],
                    "node_index": p["node_index"],
                    "node": p["node"],
                    "pair": p["pair"],
                })
                hit_pair_indices.append(p["pair_index"])
                hit_node_pairs.append(p["pair"])

        unique_hit_pair_indices = sorted(set(hit_pair_indices))
        all_hits_on_path = all(h in pos for h in hits)

        out = {
            "state": state,
            "shell_bit": int(r["shell_bit"]),
            "rank_bit": int(r["rank_bit"]),
            "step": int(r["step"]),
            "from_c": int(r["from_c"]),
            "to_c": int(r["to_c"]),
            "anchor_hits": hits,
            "all_hits_on_closed_anchor_path": all_hits_on_path,
            "unique_hit_pair_indices": unique_hit_pair_indices,
            "hit_records": hit_records,
        }
        rows.append(out)

        state_transition_profiles[state + "_step" + str(r["step"])] = out

    all_hits_on_closed_path = all(r["all_hits_on_closed_anchor_path"] for r in rows)

    path_residue_matches = {}
    for r in a008["rows"]:
        state = r["state"]
        expected = sorted(int(x) for x in r["anchor_residues"])
        actual = path_profiles[state]["closed_path_residue_set"]
        path_residue_matches[state] = expected == actual

    checks = {
        "anchor_mediation_008_theorem_pass": bool(a008.get("theorem_pass")),
        "project22_012_theorem_pass": bool(a012.get("theorem_pass")),
        "state_anchor_paths_found": sorted(anchor_paths.keys()) == ["B0", "B1", "O0", "O1"],
        "unsupported_transition_count_is_6": len(rows) == 6,
        "all_anchor_hits_on_closed_anchor_path": all_hits_on_closed_path,
        "all_closed_path_residue_sets_match_anchor_residue_sets": all(path_residue_matches.values()),
    }

    result = {
        "status": "native_g60_anchor_path_mediator_position_recorded",
        "audit_id": "009",
        "inputs": {
            "anchor_mediation_008": str(IN_008),
            "project22_anchor_path_012": str(IN_012),
        },
        "path_profiles": path_profiles,
        "rows": rows,
        "state_transition_profiles": state_transition_profiles,
        "path_residue_matches": path_residue_matches,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "claim": (
            "Every same-state anchor mediator hit from artifact 008 lies on the same state's closed Project 22 anchor node path "
            "from artifact 012. The closed path residue sets match the Project 22 anchor residue sets."
        ),
        "interpretation": (
            "The anchor mediation of missing C relays is not merely set-level anchor overlap. The mediator hits sit on the closed "
            "anchor node-path geometry of the same local state. This strengthens the coupling between C-side relay closure and "
            "anchor-side path geometry."
        ),
        "boundary": (
            "This positions mediator hits on known Project 22 closed anchor paths. It does not select a unique mediator in every case, "
            "does not derive the closed anchor paths from native G60 provenance, does not test station fields or lifted masks, "
            "does not derive the full role-labeled shared_B edge universe, and does not close Gap A."
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
            "shell_bit",
            "rank_bit",
            "step",
            "from_c",
            "to_c",
            "anchor_hits",
            "all_hits_on_closed_anchor_path",
            "unique_hit_pair_indices",
            "hit_records",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["shell_bit"],
                r["rank_bit"],
                r["step"],
                r["from_c"],
                r["to_c"],
                " ".join(str(x) for x in r["anchor_hits"]),
                "1" if r["all_hits_on_closed_anchor_path"] else "0",
                " ".join(str(x) for x in r["unique_hit_pair_indices"]),
                json.dumps(r["hit_records"], sort_keys=True),
            ])

    lines = []
    lines.append("# Native G60 anchor path mediator position 009")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Do the same-state anchor mediator hits from artifact 008 sit on the closed Project 22 anchor node paths?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- all_anchor_hits_on_closed_anchor_path: `" + str(all_hits_on_closed_path) + "`")
    lines.append("- path_residue_matches: `" + str(path_residue_matches) + "`")
    lines.append("")
    lines.append("## Closed path profiles")
    lines.append("")
    for state in ["O0", "O1", "B0", "B1"]:
        p = path_profiles[state]
        lines.append("- " + state + ":")
        lines.append("  - source_key: `" + str(p["source_key"]) + "`")
        lines.append("  - closed_path: `" + str(p["closed_path"]) + "`")
        lines.append("  - residue_set: `" + str(p["closed_path_residue_set"]) + "`")
    lines.append("")
    lines.append("## Mediator positions")
    lines.append("")
    for r in rows:
        lines.append(
            "- "
            + r["state"]
            + " step "
            + str(r["step"])
            + ": `"
            + str(r["from_c"])
            + " -> "
            + str(r["to_c"])
            + "`, anchor hits `"
            + str(r["anchor_hits"])
            + "`, pair indices `"
            + str(r["unique_hit_pair_indices"])
            + "`"
        )
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Claim")
    lines.append("")
    lines.append(result["claim"])
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
    print("theorem_pass", result["theorem_pass"])
    print("all_anchor_hits_on_closed_anchor_path", all_hits_on_closed_path)
    print("path_residue_matches", path_residue_matches)


if __name__ == "__main__":
    main()
