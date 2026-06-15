#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_017 = ROOT / "artifacts/json/native_g60_anchor_path_quotient_pair_theorem_017.v1.json"
IN_018 = ROOT / "artifacts/json/native_g60_anchor_lift_mask_sheet_selector_018.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_candidate_feature_audit_021.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_candidate_feature_audit_021.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_candidate_feature_audit_021.md"

STATES = ["O0", "O1", "B0", "B1"]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_cycle(cycle):
    return sorted({int(x) for pair in cycle for x in pair})


def pair_sizes(cycle):
    return [len(pair) for pair in cycle]


def cycle_support_shape(cycle, support_sum):
    return {
        "pair_sizes": pair_sizes(cycle),
        "residue_count": len(flatten_cycle(cycle)),
        "support_sum": support_sum,
    }


def main():
    a011 = load_json(IN_011)
    a017 = load_json(IN_017)
    a018 = load_json(IN_018)
    a020 = load_json(IN_020)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a017.get("theorem_pass"):
        raise SystemExit("017 theorem_pass is not true")
    if not a018.get("theorem_pass"):
        raise SystemExit("018 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")

    relay_hits_by_state = {s: set() for s in STATES}
    unique_relay_hits_by_state = {s: set() for s in STATES}

    for row in a011["rows"]:
        state = row["state"]
        hits = [int(h["hit"]) for h in row["unlifted_hits"]]
        for h in hits:
            relay_hits_by_state[state].add(h)
        if len(hits) == 1:
            unique_relay_hits_by_state[state].add(hits[0])

    observed_by_state = {}
    for state in STATES:
        observed_by_state[state] = a020["per_state"][state]["observed_cycle"]

    rows = []
    per_state = {}

    for state in STATES:
        candidates = [r for r in a020["rows"] if r["state"] == state]
        observed_cycle = observed_by_state[state]
        observed_flat = set(flatten_cycle(observed_cycle))
        relay_hits = relay_hits_by_state[state]
        unique_hits = unique_relay_hits_by_state[state]

        state_rows = []

        for c in candidates:
            cycle = c["cycle"]
            flat = set(flatten_cycle(cycle))
            support_sum = int(c["support_sum_best_orientation"])

            relay_hit_overlap = sorted(flat.intersection(relay_hits))
            unique_relay_hit_overlap = sorted(flat.intersection(unique_hits))
            observed_residue_overlap = sorted(flat.intersection(observed_flat))

            features = {
                "state": state,
                "candidate_index": int(c["candidate_index"]),
                "cycle": cycle,
                "support_sum": support_sum,
                "orientation_count": int(c["orientation_count"]),
                "rank_by_best_support_sum_desc": int(c["rank_by_best_support_sum_desc"]),
                "matches_observed_cycle": bool(c["matches_observed_cycle"]),
                "residue_count": len(flat),
                "pair_size_signature": "-".join(str(x) for x in pair_sizes(cycle)),
                "relay_hit_overlap_count": len(relay_hit_overlap),
                "relay_hit_overlap": relay_hit_overlap,
                "unique_relay_hit_overlap_count": len(unique_relay_hit_overlap),
                "unique_relay_hit_overlap": unique_relay_hit_overlap,
                "observed_residue_overlap_count": len(observed_residue_overlap),
                "observed_residue_overlap": observed_residue_overlap,
                "equals_observed_residue_set": flat == observed_flat,
                "contains_all_unique_relay_hits": unique_hits.issubset(flat),
                "contains_any_unique_relay_hit": len(unique_relay_hit_overlap) > 0,
            }
            rows.append(features)
            state_rows.append(features)

        observed = [r for r in state_rows if r["matches_observed_cycle"]][0]

        exact_single_feature_selectors = []
        feature_names = [
            "support_sum",
            "orientation_count",
            "rank_by_best_support_sum_desc",
            "relay_hit_overlap_count",
            "unique_relay_hit_overlap_count",
            "observed_residue_overlap_count",
            "contains_all_unique_relay_hits",
            "contains_any_unique_relay_hit",
        ]

        for fname in feature_names:
            observed_value = observed[fname]
            matches = [r for r in state_rows if r[fname] == observed_value]
            if len(matches) == 1 and matches[0]["matches_observed_cycle"]:
                exact_single_feature_selectors.append({
                    "feature": fname,
                    "observed_value": observed_value,
                })

        per_state[state] = {
            "candidate_count": len(state_rows),
            "observed_candidate_index": observed["candidate_index"],
            "observed_rank_by_best_support_sum_desc": observed["rank_by_best_support_sum_desc"],
            "observed_support_sum": observed["support_sum"],
            "relay_hits": sorted(relay_hits),
            "unique_relay_hits": sorted(unique_hits),
            "observed_features": observed,
            "exact_single_feature_selectors": exact_single_feature_selectors,
        }

    total_candidates = len(rows)
    observed_found_all = all(
        any(r["matches_observed_cycle"] for r in rows if r["state"] == state)
        for state in STATES
    )

    states_with_single_feature_selector = [
        state for state, rec in per_state.items()
        if rec["exact_single_feature_selectors"]
    ]

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "anchor_quotient_pair_017_theorem_pass": bool(a017.get("theorem_pass")),
        "lift_mask_sheet_018_theorem_pass": bool(a018.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "total_candidate_count_matches_020": total_candidates == a020.get("total_canonical_candidate_count"),
        "all_observed_cycles_found": observed_found_all,
    }

    result = {
        "status": "native_g60_anchor_candidate_feature_audit_recorded",
        "audit_id": "021",
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "anchor_quotient_pair_theorem_017": str(IN_017),
            "lift_mask_sheet_selector_018": str(IN_018),
            "candidate_census_fixed_020": str(IN_020),
        },
        "total_candidate_count": total_candidates,
        "per_state": per_state,
        "rows": rows,
        "states_with_single_feature_selector": states_with_single_feature_selector,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "This audits simple candidate-level features after the corrected census. It looks for whether support rank, "
            "relay-hit overlap, or unique relay-hit overlap already singles out the observed anchor path. A positive result "
            "would suggest a selector direction; a negative result means path selection requires a richer station or provenance feature."
        ),
        "boundary": (
            "This is a feature audit over candidates from artifact 020. It does not derive anchor residue sets, does not prove "
            "a path selector theorem unless exact selector features are found and later validated, does not test station fields, "
            "does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A."
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
            "matches_observed_cycle",
            "support_sum",
            "orientation_count",
            "rank_by_best_support_sum_desc",
            "relay_hit_overlap_count",
            "unique_relay_hit_overlap_count",
            "observed_residue_overlap_count",
            "contains_all_unique_relay_hits",
            "contains_any_unique_relay_hit",
            "cycle",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["candidate_index"],
                "1" if r["matches_observed_cycle"] else "0",
                r["support_sum"],
                r["orientation_count"],
                r["rank_by_best_support_sum_desc"],
                r["relay_hit_overlap_count"],
                r["unique_relay_hit_overlap_count"],
                r["observed_residue_overlap_count"],
                "1" if r["contains_all_unique_relay_hits"] else "0",
                "1" if r["contains_any_unique_relay_hit"] else "0",
                json.dumps(r["cycle"]),
            ])

    lines = []
    lines.append("# Native G60 anchor candidate feature audit 021")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Do simple candidate-level features select the observed anchor paths from the corrected census?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- all_checks_pass: `" + str(result["all_checks_pass"]) + "`")
    lines.append("- total_candidate_count: `" + str(total_candidates) + "`")
    lines.append("- states_with_single_feature_selector: `" + str(states_with_single_feature_selector) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - candidate_count: `" + str(p["candidate_count"]) + "`")
        lines.append("  - observed_candidate_index: `" + str(p["observed_candidate_index"]) + "`")
        lines.append("  - observed_rank_by_best_support_sum_desc: `" + str(p["observed_rank_by_best_support_sum_desc"]) + "`")
        lines.append("  - observed_support_sum: `" + str(p["observed_support_sum"]) + "`")
        lines.append("  - relay_hits: `" + str(p["relay_hits"]) + "`")
        lines.append("  - unique_relay_hits: `" + str(p["unique_relay_hits"]) + "`")
        lines.append("  - exact_single_feature_selectors: `" + str(p["exact_single_feature_selectors"]) + "`")
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
    print("total_candidate_count", total_candidates)
    print("states_with_single_feature_selector", states_with_single_feature_selector)
    for state in STATES:
        p = per_state[state]
        print(state, "selectors", p["exact_single_feature_selectors"])


if __name__ == "__main__":
    main()
