#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_017 = ROOT / "artifacts/json/native_g60_anchor_path_quotient_pair_theorem_017.v1.json"
IN_018 = ROOT / "artifacts/json/native_g60_anchor_lift_mask_sheet_selector_018.v1.json"
IN_019 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_019.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_path_candidate_census_fixed_020.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_path_candidate_census_fixed_020.md"

STATES = ["O0", "O1", "B0", "B1"]


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


def support_key(a, b):
    return tuple(sorted((int(a), int(b))))


def residue_pair(pair):
    return tuple(sorted({int(x) % 15 for x in pair}))


def rotations_and_reversals(cycle):
    cycle = tuple(tuple(x) for x in cycle)
    n = len(cycle)
    out = []
    for i in range(n):
        r = cycle[i:] + cycle[:i]
        out.append(r)
        out.append(tuple(reversed(r)))
    return out


def canonical_cycle(cycle):
    return min(rotations_and_reversals(cycle))


def step_supported(pair_a, pair_b, residue_support):
    for a in pair_a:
        for b in pair_b:
            if support_key(a, b) in residue_support:
                return True
    return False


def step_support_count(pair_a, pair_b, residue_support):
    total = 0
    for a in pair_a:
        for b in pair_b:
            total += len(residue_support.get(support_key(a, b), []))
    return total


def all_labeled_partitions(items, sizes):
    # Returns ordered blocks matching the exact ordered size profile.
    # This intentionally does not try to quotient by block-size symmetries.
    items = tuple(sorted(items))

    def rec(remaining, sizes_left):
        if not sizes_left:
            if not remaining:
                yield []
            return

        size = sizes_left[0]
        for combo in itertools.combinations(remaining, size):
            block = tuple(sorted(combo))
            rest = tuple(x for x in remaining if x not in block)
            for tail in rec(rest, sizes_left[1:]):
                yield [block] + tail

    seen = set()
    for parts in rec(items, list(sizes)):
        key = tuple(parts)
        if key not in seen:
            seen.add(key)
            yield parts


def main():
    a017 = load_json(IN_017)
    a018 = load_json(IN_018)
    a019 = load_json(IN_019)
    edges = load_edges(G60_EDGES)

    if not a017.get("theorem_pass"):
        raise SystemExit("017 theorem_pass is not true")
    if not a018.get("theorem_pass"):
        raise SystemExit("018 theorem_pass is not true")

    residue_support = {}
    for u, v in edges:
        key = support_key(u % 15, v % 15)
        residue_support.setdefault(key, []).append((u, v))

    rows = []
    per_state = {}

    for state in STATES:
        prof = a017["per_state"][state]
        closed_path = prof["closed_path"]
        observed_cycle = tuple(residue_pair(pair) for pair in closed_path[:-1])
        observed_canon = canonical_cycle(observed_cycle)
        anchor_set = sorted({x for pair in observed_cycle for x in pair})
        size_profile = [len(pair) for pair in observed_cycle]

        candidates_by_canon = {}
        labeled_candidate_count = 0
        supported_labeled_count = 0

        for parts in all_labeled_partitions(anchor_set, size_profile):
            labeled_candidate_count += 1

            if not all(step_supported(parts[i], parts[(i + 1) % 3], residue_support) for i in range(3)):
                continue

            supported_labeled_count += 1
            canon = canonical_cycle(parts)

            support_counts = [
                step_support_count(parts[i], parts[(i + 1) % 3], residue_support)
                for i in range(3)
            ]

            rec = candidates_by_canon.setdefault(canon, {
                "cycle": [list(x) for x in canon],
                "support_sum_best_orientation": None,
                "support_sum_values": [],
                "orientation_count": 0,
                "matches_observed_cycle": canon == observed_canon,
            })

            rec["orientation_count"] += 1
            rec["support_sum_values"].append(sum(support_counts))
            if rec["support_sum_best_orientation"] is None or sum(support_counts) > rec["support_sum_best_orientation"]:
                rec["support_sum_best_orientation"] = sum(support_counts)

        candidates = list(candidates_by_canon.values())
        candidates.sort(key=lambda c: (-c["support_sum_best_orientation"], c["cycle"]))

        for idx, c in enumerate(candidates):
            c["candidate_index"] = idx
            c["rank_by_best_support_sum_desc"] = idx + 1

        observed = [c for c in candidates if c["matches_observed_cycle"]]
        observed_found = len(observed) == 1
        observed_rank = observed[0]["rank_by_best_support_sum_desc"] if observed_found else None
        observed_support_sum = observed[0]["support_sum_best_orientation"] if observed_found else None

        per_state[state] = {
            "anchor_residue_set": anchor_set,
            "size_profile": size_profile,
            "observed_cycle": [list(x) for x in observed_canon],
            "labeled_candidate_count": labeled_candidate_count,
            "supported_labeled_candidate_count": supported_labeled_count,
            "canonical_candidate_count": len(candidates),
            "observed_found": observed_found,
            "observed_rank_by_best_support_sum_desc": observed_rank,
            "observed_support_sum_best_orientation": observed_support_sum,
            "candidate_examples_first_20": candidates[:20],
        }

        for c in candidates:
            rows.append({
                "state": state,
                "candidate_index": c["candidate_index"],
                "cycle": c["cycle"],
                "support_sum_best_orientation": c["support_sum_best_orientation"],
                "orientation_count": c["orientation_count"],
                "matches_observed_cycle": c["matches_observed_cycle"],
                "rank_by_best_support_sum_desc": c["rank_by_best_support_sum_desc"],
            })

    checks = {
        "anchor_quotient_pair_017_theorem_pass": bool(a017.get("theorem_pass")),
        "lift_mask_sheet_018_theorem_pass": bool(a018.get("theorem_pass")),
        "g60_edge_count_is_120": len(edges) == 120,
        "all_observed_cycles_found": all(per_state[s]["observed_found"] for s in STATES),
        "b0_observed_cycle_found": bool(per_state["B0"]["observed_found"]),
        "all_states_have_candidates": all(per_state[s]["canonical_candidate_count"] > 0 for s in STATES),
        "old_019_b0_miss_recorded": a019["per_state"]["B0"]["observed_found"] is False,
    }

    result = {
        "status": "native_g60_anchor_path_candidate_census_fixed_recorded",
        "audit_id": "020",
        "inputs": {
            "anchor_quotient_pair_theorem_017": str(IN_017),
            "lift_mask_sheet_selector_018": str(IN_018),
            "prior_census_019": str(IN_019),
            "g60_edges": str(G60_EDGES),
        },
        "total_canonical_candidate_count": len(rows),
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "observed_unique_in_all_states": all(per_state[s]["canonical_candidate_count"] == 1 for s in STATES),
        "interpretation": (
            "This fixes the anchor-path candidate census by enumerating ordered/labeled partitions with the exact observed "
            "size profile before quotienting cycles by rotation and reversal. The prior B0 miss in artifact 019 is treated "
            "as a census enumeration issue, because artifact 016 already proved the observed B0 residue-pair steps are supported."
        ),
        "boundary": (
            "This is still a candidate census over observed anchor residue sets and pair-size profiles. It does not derive "
            "the anchor residue sets themselves, does not derive why the exact anchor paths are selected, does not test station "
            "fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, and does not close Gap A."
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
            "cycle",
            "support_sum_best_orientation",
            "orientation_count",
            "matches_observed_cycle",
            "rank_by_best_support_sum_desc",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["candidate_index"],
                json.dumps(r["cycle"]),
                r["support_sum_best_orientation"],
                r["orientation_count"],
                "1" if r["matches_observed_cycle"] else "0",
                r["rank_by_best_support_sum_desc"],
            ])

    lines = []
    lines.append("# Native G60 anchor path candidate census fixed 020")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("After fixing unequal-size partition enumeration, are all observed anchor residue cycles found?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- total_canonical_candidate_count: `" + str(len(rows)) + "`")
    lines.append("- observed_unique_in_all_states: `" + str(result["observed_unique_in_all_states"]) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - anchor_residue_set: `" + str(p["anchor_residue_set"]) + "`")
        lines.append("  - size_profile: `" + str(p["size_profile"]) + "`")
        lines.append("  - observed_cycle: `" + str(p["observed_cycle"]) + "`")
        lines.append("  - labeled_candidate_count: `" + str(p["labeled_candidate_count"]) + "`")
        lines.append("  - supported_labeled_candidate_count: `" + str(p["supported_labeled_candidate_count"]) + "`")
        lines.append("  - canonical_candidate_count: `" + str(p["canonical_candidate_count"]) + "`")
        lines.append("  - observed_found: `" + str(p["observed_found"]) + "`")
        lines.append("  - observed_rank_by_best_support_sum_desc: `" + str(p["observed_rank_by_best_support_sum_desc"]) + "`")
        lines.append("  - observed_support_sum_best_orientation: `" + str(p["observed_support_sum_best_orientation"]) + "`")
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
    print("theorem_pass", result["theorem_pass"])
    print("total_canonical_candidate_count", len(rows))
    print("observed_unique_in_all_states", result["observed_unique_in_all_states"])
    for state in STATES:
        p = per_state[state]
        print(state, "canonical_candidate_count", p["canonical_candidate_count"], "observed_found", p["observed_found"], "observed_rank", p["observed_rank_by_best_support_sum_desc"])


if __name__ == "__main__":
    main()
