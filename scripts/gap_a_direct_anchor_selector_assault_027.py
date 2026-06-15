#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_022 = ROOT / "artifacts/json/native_g60_anchor_rank_fingerprint_law_022.v1.json"
IN_024 = ROOT / "artifacts/json/local_cell_provenance_frontier_checkpoint_024.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/gap_a_direct_anchor_selector_assault_027.v1.json"
OUT_CSV = ROOT / "artifacts/csv/gap_a_direct_anchor_selector_assault_027.v1.csv"
OUT_NOTE = ROOT / "notes/gap_a_direct_anchor_selector_assault_027.md"

STATES = ["O0", "O1", "B0", "B1"]
RESIDUES = list(range(15))


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


def bits(state):
    if state == "O0":
        return 0, 0
    if state == "O1":
        return 0, 1
    if state == "B0":
        return 1, 0
    if state == "B1":
        return 1, 1
    raise ValueError(state)


def rank_law(b, r):
    return 2 + 7*b + 2*r - b*r


def residue_count_law(b, r):
    # Matches the inherited local-cell residue counts:
    # O0,O1,B1 have 6 residues; B0 has 5.
    return 6 - b*(1-r)


def size_profile_law(b, r):
    # B0 is the only singleton-middle profile.
    # Others are 2-2-2 cycles.
    return [2, 2 - b*(1-r), 2]


def support_key(a, b):
    return tuple(sorted((int(a), int(b))))


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


def relay_obligations_from_011(a011):
    obligations = {s: [] for s in STATES}

    for row in a011["rows"]:
        state = row["state"]
        hits = sorted({int(h["hit"]) for h in row.get("unlifted_hits", [])})
        if hits:
            obligations[state].append({
                "c_step": int(row.get("step", -1)),
                "from_C": row.get("from_C"),
                "to_C": row.get("to_C"),
                "allowed_hits": hits,
            })

    return obligations


def satisfies_relay_obligations(residue_set, obligations):
    s = set(residue_set)
    for ob in obligations:
        if not s.intersection(ob["allowed_hits"]):
            return False
    return True


def cycle_flat(cycle):
    return sorted({int(x) for pair in cycle for x in pair})


def main():
    a011 = load_json(IN_011)
    a020 = load_json(IN_020)
    a022 = load_json(IN_022)
    a024 = load_json(IN_024)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if not a022.get("theorem_pass"):
        raise SystemExit("022 theorem_pass is not true")
    if not a024.get("checkpoint_pass"):
        raise SystemExit("024 checkpoint_pass is not true")

    edges = load_edges(G60_EDGES)
    residue_support = {}
    for u, v in edges:
        residue_support.setdefault(support_key(u % 15, v % 15), []).append((u, v))

    obligations_by_state = relay_obligations_from_011(a011)

    per_state = {}
    selected_rows = []
    csv_rows = []

    for state in STATES:
        b, r = bits(state)
        target_rank = rank_law(b, r)
        residue_count = residue_count_law(b, r)
        size_profile = size_profile_law(b, r)

        observed_cycle = tuple(tuple(x) for x in a020["per_state"][state]["observed_cycle"])
        observed_canon = canonical_cycle(observed_cycle)

        candidates_by_canon = {}
        residue_set_count = 0
        residue_set_after_relay_count = 0
        labeled_candidate_count = 0
        supported_labeled_candidate_count = 0

        for residue_set in itertools.combinations(RESIDUES, residue_count):
            residue_set_count += 1
            if not satisfies_relay_obligations(residue_set, obligations_by_state[state]):
                continue

            residue_set_after_relay_count += 1

            for parts in all_labeled_partitions(residue_set, size_profile):
                labeled_candidate_count += 1

                if not all(step_supported(parts[i], parts[(i + 1) % 3], residue_support) for i in range(3)):
                    continue

                supported_labeled_candidate_count += 1
                canon = canonical_cycle(parts)

                support_counts = [
                    step_support_count(parts[i], parts[(i + 1) % 3], residue_support)
                    for i in range(3)
                ]
                support_sum = sum(support_counts)

                rec = candidates_by_canon.setdefault(canon, {
                    "cycle": [list(x) for x in canon],
                    "residue_set": cycle_flat(canon),
                    "support_sum_best_orientation": None,
                    "support_sum_values": [],
                    "orientation_count": 0,
                    "matches_observed_cycle": canon == observed_canon,
                })

                rec["orientation_count"] += 1
                rec["support_sum_values"].append(support_sum)
                if rec["support_sum_best_orientation"] is None or support_sum > rec["support_sum_best_orientation"]:
                    rec["support_sum_best_orientation"] = support_sum

        candidates = list(candidates_by_canon.values())
        candidates.sort(key=lambda c: (-c["support_sum_best_orientation"], c["cycle"]))

        for idx, c in enumerate(candidates):
            c["candidate_index"] = idx
            c["rank_by_best_support_sum_desc"] = idx + 1

        selected = [c for c in candidates if c["rank_by_best_support_sum_desc"] == target_rank]
        observed = [c for c in candidates if c["matches_observed_cycle"]]

        selected_count = len(selected)
        observed_found = len(observed) == 1
        selected_matches_observed = (
            selected_count == 1
            and observed_found
            and selected[0]["matches_observed_cycle"]
        )

        state_rec = {
            "state": state,
            "shell_bit": b,
            "rank_bit": r,
            "target_rank": target_rank,
            "residue_count_law": residue_count,
            "size_profile_law": size_profile,
            "relay_obligations": obligations_by_state[state],
            "residue_set_count": residue_set_count,
            "residue_set_after_relay_count": residue_set_after_relay_count,
            "labeled_candidate_count": labeled_candidate_count,
            "supported_labeled_candidate_count": supported_labeled_candidate_count,
            "canonical_candidate_count": len(candidates),
            "observed_found": observed_found,
            "observed_candidate_index": observed[0]["candidate_index"] if observed_found else None,
            "observed_rank": observed[0]["rank_by_best_support_sum_desc"] if observed_found else None,
            "observed_support_sum_best_orientation": observed[0]["support_sum_best_orientation"] if observed_found else None,
            "selected_count": selected_count,
            "selected_candidate_index": selected[0]["candidate_index"] if selected_count == 1 else None,
            "selected_rank": selected[0]["rank_by_best_support_sum_desc"] if selected_count == 1 else None,
            "selected_cycle": selected[0]["cycle"] if selected_count == 1 else None,
            "selected_residue_set": selected[0]["residue_set"] if selected_count == 1 else None,
            "selected_support_sum_best_orientation": selected[0]["support_sum_best_orientation"] if selected_count == 1 else None,
            "observed_cycle": [list(x) for x in observed_canon],
            "selected_matches_observed": selected_matches_observed,
            "top_20_candidates": candidates[:20],
        }
        per_state[state] = state_rec
        selected_rows.append(state_rec)

        for c in candidates[:50]:
            csv_rows.append({
                "state": state,
                "candidate_index": c["candidate_index"],
                "rank": c["rank_by_best_support_sum_desc"],
                "support_sum": c["support_sum_best_orientation"],
                "orientation_count": c["orientation_count"],
                "matches_observed": c["matches_observed_cycle"],
                "is_selected": c["rank_by_best_support_sum_desc"] == target_rank,
                "cycle": c["cycle"],
                "residue_set": c["residue_set"],
            })

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "prior_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "rank_law_022_theorem_pass": bool(a022.get("theorem_pass")),
        "frontier_checkpoint_024_pass": bool(a024.get("checkpoint_pass")),
        "g60_edge_count_is_120": len(edges) == 120,
        "all_observed_cycles_found_in_direct_universe": all(per_state[s]["observed_found"] for s in STATES),
        "all_states_select_one_candidate_by_rank_law": all(per_state[s]["selected_count"] == 1 for s in STATES),
        "all_selected_candidates_match_observed": all(per_state[s]["selected_matches_observed"] for s in STATES),
    }

    result = {
        "status": "gap_a_direct_anchor_selector_assault_recorded",
        "audit_id": "027",
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "prior_corrected_census_020_validation_only": str(IN_020),
            "rank_law_022": str(IN_022),
            "frontier_checkpoint_024": str(IN_024),
            "g60_edges": str(G60_EDGES),
        },
        "uses_observed_anchor_residue_sets_for_generation": False,
        "uses_observed_anchor_paths_for_generation": False,
        "uses_observed_anchor_paths_for_validation": True,
        "generation_rules": {
            "residue_count_law": "6 - b*(1-r)",
            "size_profile_law": "[2, 2 - b*(1-r), 2]",
            "relay_obligation_rule": "candidate residue set must intersect every same-state unlifted relay-hit set from artifact 011",
            "quotient_support_rule": "every cycle step must have native G60 mod15 residue-pair support",
            "rank_selector_law": "rank = 2 + 7*b + 2*r - b*r",
        },
        "per_state": per_state,
        "checks": checks,
        "closure_candidate_pass": all(checks.values()),
        "interpretation": (
            "This is a direct Gap A assault on the anchor selector. It stops assuming the observed anchor residue sets and "
            "instead generates candidates from state bits, C-relay obligations, native mod15 G60 quotient support, and the "
            "rank law. If the selected candidates match the observed anchor paths in all four states, the anchor-selector "
            "subproblem moves from observed residue-set assumption to a native/provenance candidate law."
        ),
        "boundary": (
            "Even if this passes, it is not full Gap A closure by itself. The rank law and size-profile law still require "
            "independent native/provenance justification, relay mediators are not uniquely selected, station fields are not tested, "
            "and the full role-labeled shared_B universe is not yet derived."
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
            "rank",
            "support_sum",
            "orientation_count",
            "matches_observed",
            "is_selected",
            "residue_set",
            "cycle",
        ])
        for row in csv_rows:
            w.writerow([
                row["state"],
                row["candidate_index"],
                row["rank"],
                row["support_sum"],
                row["orientation_count"],
                "1" if row["matches_observed"] else "0",
                "1" if row["is_selected"] else "0",
                json.dumps(row["residue_set"]),
                json.dumps(row["cycle"]),
            ])

    lines = []
    lines.append("# Gap A direct anchor selector assault 027")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- closure_candidate_pass: `" + str(result["closure_candidate_pass"]) + "`")
    lines.append("- uses_observed_anchor_residue_sets_for_generation: `False`")
    lines.append("- uses_observed_anchor_paths_for_generation: `False`")
    lines.append("")
    lines.append("## Generation rules")
    lines.append("")
    for k, v in result["generation_rules"].items():
        lines.append("- " + k + ": `" + v + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - target_rank: `" + str(p["target_rank"]) + "`")
        lines.append("  - residue_count_law: `" + str(p["residue_count_law"]) + "`")
        lines.append("  - size_profile_law: `" + str(p["size_profile_law"]) + "`")
        lines.append("  - residue_set_after_relay_count: `" + str(p["residue_set_after_relay_count"]) + "`")
        lines.append("  - canonical_candidate_count: `" + str(p["canonical_candidate_count"]) + "`")
        lines.append("  - observed_found: `" + str(p["observed_found"]) + "`")
        lines.append("  - observed_rank: `" + str(p["observed_rank"]) + "`")
        lines.append("  - selected_candidate_index: `" + str(p["selected_candidate_index"]) + "`")
        lines.append("  - selected_rank: `" + str(p["selected_rank"]) + "`")
        lines.append("  - selected_matches_observed: `" + str(p["selected_matches_observed"]) + "`")
        lines.append("  - selected_residue_set: `" + str(p["selected_residue_set"]) + "`")
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
    print("closure_candidate_pass", result["closure_candidate_pass"])
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "candidates", p["canonical_candidate_count"],
            "observed_found", p["observed_found"],
            "observed_rank", p["observed_rank"],
            "selected_rank", p["selected_rank"],
            "match", p["selected_matches_observed"],
        )


if __name__ == "__main__":
    main()
