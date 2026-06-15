#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_007 = ROOT / "artifacts/json/native_g60_c_path_residue_two_hop_relay_007.v1.json"
IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_033 = ROOT / "artifacts/json/local_anchor_residue_derivation_chain_033.v1.json"
IN_034 = ROOT / "artifacts/json/local_anchor_path_derivation_chain_034.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_relay_block_selector_from_mediators_035.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_relay_block_selector_from_mediators_035.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_relay_block_selector_from_mediators_035.md"

STATES = ["O0", "O1", "B0", "B1"]
C_VALUES = {
    "O0": {2, 11, 14},
    "O1": {1, 10, 13},
    "B0": {0, 2, 5},
    "B1": {2, 4, 5},
}

FALLBACK_MEDIATORS = {
    "O0": [{"step": 2, "mediators": [0, 1, 2, 3, 4, 5, 7, 8]}],
    "O1": [{"step": 2, "mediators": [1, 2, 4, 6, 7, 9]}],
    "B0": [
        {"step": 0, "mediators": [8, 11, 14]},
        {"step": 1, "mediators": [1, 4, 8, 11, 14]},
    ],
    "B1": [
        {"step": 1, "mediators": [8, 11, 14]},
        {"step": 2, "mediators": [0, 8, 10, 11, 13, 14]},
    ],
}

FALLBACK_RELAY_BLOCKS = {
    "O0": [4, 5, 7],
    "O1": [2, 4, 9],
    "B0": [4, 8],
    "B1": [8, 10, 13],
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


def direct_bit_law(values):
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

    return {
        "formula": "p0 + pb*b + pr*r + pbr*b*r",
        "coefficients": {"p0": p0, "pb": pb, "pr": pr, "pbr": pbr},
        "predictions": preds,
    }


def eval_law(law, state):
    b, r = bits(state)
    c = law["coefficients"]
    return int(c["p0"]) + int(c["pb"])*b + int(c["pr"])*r + int(c["pbr"])*b*r


def extract_mediators_from_007(a007):
    out = {s: [] for s in STATES}

    def walk(obj):
        if isinstance(obj, dict):
            state = obj.get("state")
            if state in out:
                mediators = None
                for key in [
                    "mediators",
                    "relay_mediators",
                    "two_hop_mediators",
                    "candidate_mediators",
                    "mediator_values",
                    "anchor_hits",
                    "hits",
                ]:
                    v = obj.get(key)
                    if isinstance(v, list) and all(isinstance(x, int) for x in v):
                        mediators = sorted(set(int(x) for x in v))
                        break

                if mediators:
                    step = obj.get("step", obj.get("c_step", obj.get("unsupported_step", -1)))
                    out[state].append({"step": int(step), "mediators": mediators})

            for v in obj.values():
                walk(v)

        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(a007)
    return {k: v for k, v in out.items() if v}


def relay_blocks_from_011(a011):
    out = {s: set() for s in STATES}

    for row in a011.get("rows", []):
        state = row.get("state")
        if state not in out:
            continue
        hits = []
        for key in ["unlifted_hits", "relay_hits", "hits"]:
            v = row.get(key)
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, int):
                        hits.append(item)
                    elif isinstance(item, dict) and "hit" in item:
                        hits.append(int(item["hit"]))
        out[state].update(hits)

    parsed = {s: sorted(v) for s, v in out.items() if v}
    if len(parsed) == 4:
        return parsed, "artifact_011_rows"

    return FALLBACK_RELAY_BLOCKS, "known_relay_blocks_fallback"


def generate_candidates(mediator_rows, c_values, target_size):
    mediator_union = sorted(set(x for row in mediator_rows for x in row["mediators"]))

    candidates = []
    for combo in itertools.combinations(mediator_union, target_size):
        s = set(combo)

        if s.intersection(c_values):
            continue

        # Must hit every unsupported transition mediator set.
        if not all(s.intersection(set(row["mediators"])) for row in mediator_rows):
            continue

        candidates.append(sorted(s))

    return candidates, mediator_union


def main():
    a007 = load_json(IN_007)
    a011 = load_json(IN_011)
    a033 = load_json(IN_033)
    a034 = load_json(IN_034)

    if not a007.get("theorem_pass"):
        raise SystemExit("007 theorem_pass is not true")
    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a033.get("theorem_candidate_pass"):
        raise SystemExit("033 theorem_candidate_pass is not true")
    if not a034.get("theorem_candidate_pass"):
        raise SystemExit("034 theorem_candidate_pass is not true")

    parsed_mediators = extract_mediators_from_007(a007)
    if len(parsed_mediators) == 4:
        mediators_by_state = parsed_mediators
        mediator_source = "artifact_007_parsed"
    else:
        mediators_by_state = FALLBACK_MEDIATORS
        mediator_source = "known_007_mediator_fallback"

    target_relay_blocks, relay_target_source = relay_blocks_from_011(a011)

    targets = {}
    for state in STATES:
        rb = target_relay_blocks[state]
        targets[state] = {
            "size": len(rb),
            "sum": sum(rb),
            "min": min(rb),
            "max": max(rb),
        }

    laws = {
        "relay_size": direct_bit_law({s: targets[s]["size"] for s in STATES}),
        "relay_sum": direct_bit_law({s: targets[s]["sum"] for s in STATES}),
        "relay_min": direct_bit_law({s: targets[s]["min"] for s in STATES}),
        "relay_max": direct_bit_law({s: targets[s]["max"] for s in STATES}),
    }

    per_state = {}
    csv_rows = []

    for state in STATES:
        c_values = set(C_VALUES[state])
        size_target = eval_law(laws["relay_size"], state)
        sum_target = eval_law(laws["relay_sum"], state)
        min_target = eval_law(laws["relay_min"], state)
        max_target = eval_law(laws["relay_max"], state)

        candidates, mediator_union = generate_candidates(
            mediators_by_state[state],
            c_values,
            size_target,
        )

        selected = [
            c for c in candidates
            if sum(c) == sum_target and min(c) == min_target and max(c) == max_target
        ]

        target = sorted(target_relay_blocks[state])

        per_state[state] = {
            "mediator_rows": mediators_by_state[state],
            "mediator_union": mediator_union,
            "c_values": sorted(c_values),
            "target_relay_block": target,
            "size_target": size_target,
            "sum_target": sum_target,
            "min_target": min_target,
            "max_target": max_target,
            "candidate_count": len(candidates),
            "selected_count": len(selected),
            "selected_relay_blocks": selected,
            "selected_matches_target": len(selected) == 1 and selected[0] == target,
        }

        for idx, c in enumerate(candidates):
            csv_rows.append({
                "state": state,
                "candidate_index": idx,
                "relay_block": c,
                "sum": sum(c),
                "min": min(c),
                "max": max(c),
                "is_selected": c in selected,
                "matches_target": c == target,
            })

    checks = {
        "two_hop_relay_007_theorem_pass": bool(a007.get("theorem_pass")),
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "anchor_residue_derivation_033_pass": bool(a033.get("theorem_candidate_pass")),
        "anchor_path_derivation_034_pass": bool(a034.get("theorem_candidate_pass")),
        "all_states_have_mediator_rows": all(len(mediators_by_state[s]) > 0 for s in STATES),
        "all_states_select_one_relay_block": all(per_state[s]["selected_count"] == 1 for s in STATES),
        "all_selected_relay_blocks_match_target": all(per_state[s]["selected_matches_target"] for s in STATES),
    }

    result = {
        "status": "native_g60_relay_block_selector_from_mediators_recorded",
        "audit_id": "035",
        "inputs": {
            "two_hop_relay_007": str(IN_007),
            "unlifted_anchor_relay_cover_011": str(IN_011),
            "local_anchor_residue_derivation_chain_033": str(IN_033),
            "local_anchor_path_derivation_chain_034": str(IN_034),
        },
        "mediator_source": mediator_source,
        "relay_target_source": relay_target_source,
        "generation_rule": (
            "For each state, generate relay-block candidates from the union of native two-hop mediator residues in artifact 007. "
            "Candidates must avoid C values, have the state-bit relay size, and hit every unsupported transition mediator set."
        ),
        "selector_rule": (
            "Select the unique candidate matching state-bit scalar targets relay_sum, relay_min, and relay_max."
        ),
        "laws": laws,
        "per_state": per_state,
        "checks": checks,
        "theorem_candidate_pass": all(checks.values()),
        "interpretation": (
            "This attacks the relay block dependency exposed by artifacts 033 and 034. It tests whether relay blocks can be selected "
            "from native two-hop C-transition mediator geometry using compact state-bit scalar targets."
        ),
        "boundary": (
            "This is still a theorem candidate. The scalar relay laws require native/provenance interpretation, and the full "
            "role-labeled shared_B universe is not derived. If mediator_source is a fallback, the result also has a source-binding caveat."
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
            "relay_block",
            "sum",
            "min",
            "max",
            "is_selected",
            "matches_target",
        ])
        for row in csv_rows:
            w.writerow([
                row["state"],
                row["candidate_index"],
                json.dumps(row["relay_block"]),
                row["sum"],
                row["min"],
                row["max"],
                "1" if row["is_selected"] else "0",
                "1" if row["matches_target"] else "0",
            ])

    lines = []
    lines.append("# Native G60 relay block selector from mediators 035")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_candidate_pass: `" + str(result["theorem_candidate_pass"]) + "`")
    lines.append("- mediator_source: `" + mediator_source + "`")
    lines.append("- relay_target_source: `" + relay_target_source + "`")
    lines.append("")
    lines.append("## Laws")
    lines.append("")
    for k, v in laws.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - mediator_union: `" + str(p["mediator_union"]) + "`")
        lines.append("  - c_values: `" + str(p["c_values"]) + "`")
        lines.append("  - target_relay_block: `" + str(p["target_relay_block"]) + "`")
        lines.append("  - candidate_count: `" + str(p["candidate_count"]) + "`")
        lines.append("  - selected_relay_blocks: `" + str(p["selected_relay_blocks"]) + "`")
        lines.append("  - selected_matches_target: `" + str(p["selected_matches_target"]) + "`")
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
    print("mediator_source", mediator_source)
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "candidates", p["candidate_count"],
            "selected", p["selected_relay_blocks"],
            "match", p["selected_matches_target"],
        )


if __name__ == "__main__":
    main()
