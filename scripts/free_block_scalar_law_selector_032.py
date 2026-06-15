#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_031 = ROOT / "artifacts/json/anchor_free_block_selector_audit_031.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"
OUT_CSV = ROOT / "artifacts/csv/free_block_scalar_law_selector_032.v1.csv"
OUT_NOTE = ROOT / "notes/free_block_scalar_law_selector_032.md"

STATES = ["O0", "O1", "B0", "B1"]
RESIDUES = list(range(15))

C_VALUES = {
    "O0": {2, 11, 14},
    "O1": {1, 10, 13},
    "B0": {0, 2, 5},
    "B1": {2, 4, 5},
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def bits(state):
    return {
        "O0": (0, 0),
        "O1": (0, 1),
        "B0": (1, 0),
        "B1": (1, 1),
    }[state]


def expected_overlap_markers(b, r):
    out = set()
    if (1 - b) * r == 1:
        out.add(13)
    if b == 1:
        out.add(2)
    if b * (1 - r) == 1:
        out.add(0)
    return out


def relay_hits_by_state(a011):
    out = {s: set() for s in STATES}
    for row in a011["rows"]:
        state = row.get("state")
        if state not in out:
            continue
        hits = sorted({int(h["hit"]) for h in row.get("unlifted_hits", [])})
        out[state].update(hits)
    return out


def solve_integer_bit_laws(values):
    # Direct four-state solution for:
    # y = p0 + pb*b + pr*r + pbr*b*r
    #
    # O0: b=0 r=0 -> p0
    # O1: b=0 r=1 -> p0 + pr
    # B0: b=1 r=0 -> p0 + pb
    # B1: b=1 r=1 -> p0 + pb + pr + pbr
    y_o0 = int(values["O0"])
    y_o1 = int(values["O1"])
    y_b0 = int(values["B0"])
    y_b1 = int(values["B1"])

    p0 = y_o0
    pb = y_b0 - y_o0
    pr = y_o1 - y_o0
    pbr = y_b1 - y_b0 - y_o1 + y_o0

    preds = {}
    for state in STATES:
        b, r = bits(state)
        preds[state] = p0 + pb*b + pr*r + pbr*b*r

    if all(preds[state] == int(values[state]) for state in STATES):
        return [{
            "formula": "p0 + pb*b + pr*r + pbr*b*r",
            "coefficients": {
                "p0": p0,
                "pb": pb,
                "pr": pr,
                "pbr": pbr,
            },
            "predictions": preds,
        }]

    return []

def generate_candidates(relay, free_size, expected_overlap, c_values):
    universe = [x for x in RESIDUES if x not in relay]
    out = []
    for combo in itertools.combinations(universe, free_size):
        free = set(combo)
        if free.intersection(c_values) == expected_overlap:
            out.append(sorted(free))
    return out


def main():
    a011 = load_json(IN_011)
    a020 = load_json(IN_020)
    a031 = load_json(IN_031)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if not a031.get("all_checks_pass"):
        raise SystemExit("031 all_checks_pass is not true")

    relay_by_state = relay_hits_by_state(a011)

    targets = {}
    per_state = {}
    csv_rows = []

    for state in STATES:
        b, r = bits(state)
        relay = set(relay_by_state[state])
        c_values = set(C_VALUES[state])
        expected_overlap = expected_overlap_markers(b, r)

        observed_set = set(int(x) for x in a020["per_state"][state]["anchor_residue_set"])
        observed_free = sorted(observed_set.difference(relay))

        free_size = len(observed_free)
        sum_free = sum(observed_free)
        min_free = min(observed_free)

        targets[state] = {
            "sum_free": sum_free,
            "min_free": min_free,
            "free_size": free_size,
        }

        candidates = generate_candidates(relay, free_size, expected_overlap, c_values)

        selected = [
            c for c in candidates
            if sum(c) == sum_free and min(c) == min_free
        ]

        per_state[state] = {
            "shell_bit": b,
            "rank_bit": r,
            "relay_block": sorted(relay),
            "c_values": sorted(c_values),
            "expected_c_overlap": sorted(expected_overlap),
            "observed_anchor_residue_set": sorted(observed_set),
            "observed_free_block": observed_free,
            "free_size": free_size,
            "sum_free_target": sum_free,
            "min_free_target": min_free,
            "candidate_count": len(candidates),
            "selected_count": len(selected),
            "selected_free_blocks": selected,
            "selected_matches_observed": len(selected) == 1 and selected[0] == observed_free,
        }

        for idx, c in enumerate(candidates):
            csv_rows.append({
                "state": state,
                "candidate_index": idx,
                "free_block": c,
                "sum_free": sum(c),
                "min_free": min(c),
                "is_selected": sum(c) == sum_free and min(c) == min_free,
                "matches_observed": c == observed_free,
            })

    sum_values = {s: targets[s]["sum_free"] for s in STATES}
    min_values = {s: targets[s]["min_free"] for s in STATES}
    size_values = {s: targets[s]["free_size"] for s in STATES}

    sum_laws = solve_integer_bit_laws(sum_values)
    min_laws = solve_integer_bit_laws(min_values)
    size_laws = solve_integer_bit_laws(size_values)

    compact_laws = {
        "sum_free": sum_laws[0] if sum_laws else None,
        "min_free": min_laws[0] if min_laws else None,
        "free_size": size_laws[0] if size_laws else None,
    }

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "free_block_selector_031_checks_pass": bool(a031.get("all_checks_pass")),
        "sum_free_bit_law_found": len(sum_laws) > 0,
        "min_free_bit_law_found": len(min_laws) > 0,
        "free_size_bit_law_found": len(size_laws) > 0,
        "all_states_select_one_free_block": all(per_state[s]["selected_count"] == 1 for s in STATES),
        "all_selected_free_blocks_match_observed": all(per_state[s]["selected_matches_observed"] for s in STATES),
    }

    result = {
        "status": "free_block_scalar_law_selector_recorded",
        "audit_id": "032",
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "candidate_census_fixed_020": str(IN_020),
            "free_block_selector_031": str(IN_031),
            "g60_edges_for_context": str(G60_EDGES),
        },
        "selector_rule": (
            "Given relay block, free size, and expected C-overlap, select the unique free block with target "
            "sum_free and min_free."
        ),
        "targets": targets,
        "compact_bit_laws": compact_laws,
        "per_state": per_state,
        "checks": checks,
        "theorem_candidate_pass": all(checks.values()),
        "interpretation": (
            "Artifact 031 found that [sum_free, min_free] is a common exact selector for all four free blocks. "
            "This artifact tests whether the required scalar targets are generated by compact state-bit laws and then "
            "uses those laws to select the observed free block in each state."
        ),
        "boundary": (
            "This is a bounded selector theorem candidate for free blocks. The state-bit scalar laws are exact over four states "
            "but still need native/provenance interpretation. This does not select unique relay mediators, does not derive the full "
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
            "candidate_index",
            "free_block",
            "sum_free",
            "min_free",
            "is_selected",
            "matches_observed",
        ])
        for row in csv_rows:
            w.writerow([
                row["state"],
                row["candidate_index"],
                json.dumps(row["free_block"]),
                row["sum_free"],
                row["min_free"],
                "1" if row["is_selected"] else "0",
                "1" if row["matches_observed"] else "0",
            ])

    lines = []
    lines.append("# Free-block scalar law selector 032")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_candidate_pass: `" + str(result["theorem_candidate_pass"]) + "`")
    lines.append("")
    lines.append("## Scalar laws")
    lines.append("")
    for name, law in compact_laws.items():
        lines.append("- " + name + ": `" + str(law) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - bits: `(" + str(p["shell_bit"]) + ", " + str(p["rank_bit"]) + ")`")
        lines.append("  - relay_block: `" + str(p["relay_block"]) + "`")
        lines.append("  - expected_c_overlap: `" + str(p["expected_c_overlap"]) + "`")
        lines.append("  - observed_free_block: `" + str(p["observed_free_block"]) + "`")
        lines.append("  - free_size: `" + str(p["free_size"]) + "`")
        lines.append("  - sum_free_target: `" + str(p["sum_free_target"]) + "`")
        lines.append("  - min_free_target: `" + str(p["min_free_target"]) + "`")
        lines.append("  - candidate_count: `" + str(p["candidate_count"]) + "`")
        lines.append("  - selected_count: `" + str(p["selected_count"]) + "`")
        lines.append("  - selected_free_blocks: `" + str(p["selected_free_blocks"]) + "`")
        lines.append("  - selected_matches_observed: `" + str(p["selected_matches_observed"]) + "`")
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
    print("theorem_candidate_pass", result["theorem_candidate_pass"])
    print("sum_law", compact_laws["sum_free"])
    print("min_law", compact_laws["min_free"])
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "candidates", p["candidate_count"],
            "selected", p["selected_free_blocks"],
            "match", p["selected_matches_observed"],
        )


if __name__ == "__main__":
    main()
