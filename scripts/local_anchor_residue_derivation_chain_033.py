#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_023 = ROOT / "artifacts/json/native_g60_anchor_rank_selector_theorem_023.v1.json"
IN_032 = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"

OUT_JSON = ROOT / "artifacts/json/local_anchor_residue_derivation_chain_033.v1.json"
OUT_CSV = ROOT / "artifacts/csv/local_anchor_residue_derivation_chain_033.v1.csv"
OUT_NOTE = ROOT / "notes/local_anchor_residue_derivation_chain_033.md"

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


def eval_bit_law(law, b, r):
    coeff = law["coefficients"]
    return (
        int(coeff["p0"])
        + int(coeff["pb"]) * b
        + int(coeff["pr"]) * r
        + int(coeff["pbr"]) * b * r
    )


def relay_hits_by_state(a011):
    out = {s: set() for s in STATES}
    for row in a011["rows"]:
        state = row.get("state")
        if state not in out:
            continue
        hits = sorted({int(h["hit"]) for h in row.get("unlifted_hits", [])})
        out[state].update(hits)
    return out


def generate_free_candidates(relay, free_size, expected_overlap, c_values):
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
    a023 = load_json(IN_023)
    a032 = load_json(IN_032)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if not a023.get("theorem_pass"):
        raise SystemExit("023 theorem_pass is not true")
    if not a032.get("theorem_candidate_pass"):
        raise SystemExit("032 theorem_candidate_pass is not true")

    laws = a032["compact_bit_laws"]
    sum_law = laws["sum_free"]
    min_law = laws["min_free"]
    size_law = laws["free_size"]

    relay_by_state = relay_hits_by_state(a011)

    rows = []
    per_state = {}

    for state in STATES:
        b, r = bits(state)
        relay = set(relay_by_state[state])
        c_values = set(C_VALUES[state])
        expected_overlap = expected_overlap_markers(b, r)

        target_sum = eval_bit_law(sum_law, b, r)
        target_min = eval_bit_law(min_law, b, r)
        free_size = eval_bit_law(size_law, b, r)

        candidates = generate_free_candidates(relay, free_size, expected_overlap, c_values)
        selected = [
            c for c in candidates
            if sum(c) == target_sum and min(c) == target_min
        ]

        generated_free = set(selected[0]) if len(selected) == 1 else set()
        generated_anchor = set(relay).union(generated_free)

        observed_anchor = set(int(x) for x in a020["per_state"][state]["anchor_residue_set"])
        observed_cycle = a020["per_state"][state].get("observed_cycle")

        rec = {
            "state": state,
            "shell_bit": b,
            "rank_bit": r,
            "relay_block": sorted(relay),
            "c_values": sorted(c_values),
            "expected_c_overlap": sorted(expected_overlap),
            "free_size_target": free_size,
            "sum_free_target": target_sum,
            "min_free_target": target_min,
            "free_candidate_count": len(candidates),
            "selected_free_block_count": len(selected),
            "selected_free_block": sorted(generated_free),
            "generated_anchor_residue_set": sorted(generated_anchor),
            "observed_anchor_residue_set": sorted(observed_anchor),
            "generated_matches_observed_anchor_set": generated_anchor == observed_anchor,
            "observed_cycle_from_020": observed_cycle,
        }
        per_state[state] = rec
        rows.append(rec)

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "rank_selector_023_theorem_pass": bool(a023.get("theorem_pass")),
        "free_block_scalar_032_theorem_candidate_pass": bool(a032.get("theorem_candidate_pass")),
        "all_states_select_one_free_block": all(per_state[s]["selected_free_block_count"] == 1 for s in STATES),
        "all_generated_anchor_sets_match_observed": all(
            per_state[s]["generated_matches_observed_anchor_set"] for s in STATES
        ),
    }

    result = {
        "status": "local_anchor_residue_derivation_chain_recorded",
        "audit_id": "033",
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "candidate_census_fixed_020": str(IN_020),
            "anchor_rank_selector_023": str(IN_023),
            "free_block_scalar_selector_032": str(IN_032),
        },
        "chain": [
            "state bits determine expected C-overlap and scalar free-block targets",
            "artifact 011 supplies same-state relay blocks",
            "artifact 032 selects the unique free block",
            "relay block union selected free block generates the anchor residue set",
            "generated anchor residue set matches the anchor residue set used by artifact 020",
            "artifact 023 then conditionally selects the observed anchor path from that generated residue set",
        ],
        "scalar_laws": {
            "sum_free": sum_law,
            "min_free": min_law,
            "free_size": size_law,
        },
        "per_state": per_state,
        "checks": checks,
        "theorem_candidate_pass": all(checks.values()),
        "interpretation": (
            "This composes the relay layer and free-block scalar selector into a generated anchor residue set. "
            "The generated anchor residue set matches the residue set required by the existing anchor path rank selector in all four states."
        ),
        "boundary": (
            "This is a local anchor residue derivation chain, not full Gap A closure. The relay blocks still come from the "
            "unlifted relay cover rather than uniquely selected relay mediators, the scalar laws still need native/provenance interpretation, "
            "and the full role-labeled shared_B universe is not derived."
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
            "relay_block",
            "selected_free_block",
            "generated_anchor_residue_set",
            "observed_anchor_residue_set",
            "match",
        ])
        for row in rows:
            w.writerow([
                row["state"],
                json.dumps(row["relay_block"]),
                json.dumps(row["selected_free_block"]),
                json.dumps(row["generated_anchor_residue_set"]),
                json.dumps(row["observed_anchor_residue_set"]),
                "1" if row["generated_matches_observed_anchor_set"] else "0",
            ])

    lines = []
    lines.append("# Local anchor residue derivation chain 033")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_candidate_pass: `" + str(result["theorem_candidate_pass"]) + "`")
    lines.append("")
    lines.append("## Chain")
    lines.append("")
    for item in result["chain"]:
        lines.append("- " + item)
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - relay_block: `" + str(p["relay_block"]) + "`")
        lines.append("  - selected_free_block: `" + str(p["selected_free_block"]) + "`")
        lines.append("  - generated_anchor_residue_set: `" + str(p["generated_anchor_residue_set"]) + "`")
        lines.append("  - observed_anchor_residue_set: `" + str(p["observed_anchor_residue_set"]) + "`")
        lines.append("  - generated_matches_observed_anchor_set: `" + str(p["generated_matches_observed_anchor_set"]) + "`")
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
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "relay", p["relay_block"],
            "free", p["selected_free_block"],
            "anchor", p["generated_anchor_residue_set"],
            "match", p["generated_matches_observed_anchor_set"],
        )


if __name__ == "__main__":
    main()
