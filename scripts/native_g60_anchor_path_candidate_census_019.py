#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_012 = ROOT / "source/project22_artifacts/json/lift_twist_anchor_node_path_geometry_012.v1.json"
IN_017 = ROOT / "artifacts/json/native_g60_anchor_path_quotient_pair_theorem_017.v1.json"
IN_018 = ROOT / "artifacts/json/native_g60_anchor_lift_mask_sheet_selector_018.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_019.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_path_candidate_census_019.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_path_candidate_census_019.md"

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


def residue_pair(pair):
    return tuple(sorted({int(x) % 15 for x in pair}))


def support_key(a, b):
    return tuple(sorted((int(a), int(b))))


def path_key(path):
    return tuple(tuple(x) for x in path)


def rotations(path3):
    # path3 is a 3-tuple of residue-pairs, without repeated closure.
    out = []
    for i in range(3):
        p = path3[i:] + path3[:i]
        out.append(p)
        out.append(tuple(reversed(p)))
    return out


def canonical_cycle(path3):
    return min(rotations(tuple(path3)))


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


def set_partitions_fixed_sizes(items, sizes):
    items = tuple(sorted(items))

    def rec(remaining, sizes_left):
        if not sizes_left:
            if not remaining:
                yield []
            return
        size = sizes_left[0]
        remaining = tuple(remaining)
        first = remaining[0]
        rest = remaining[1:]
        for combo_tail in itertools.combinations(rest, size - 1):
            block = tuple(sorted((first,) + combo_tail))
            new_remaining = tuple(x for x in remaining if x not in block)
            for tail in rec(new_remaining, sizes_left[1:]):
                yield [block] + tail

    # Sort sizes descending for less duplication, then canonicalize final blocks.
    size_order = sorted(sizes, reverse=True)
    seen = set()
    for parts in rec(items, size_order):
        key = tuple(sorted(parts))
        if key in seen:
            continue
        seen.add(key)
        yield list(key)


def main():
    a012 = load_json(IN_012)
    a017 = load_json(IN_017)
    a018 = load_json(IN_018)
    g60_edges = load_edges(G60_EDGES)

    if not a012.get("theorem_pass"):
        raise SystemExit("Project22 012 theorem_pass is not true")
    if not a017.get("theorem_pass"):
        raise SystemExit("017 theorem_pass is not true")
    if not a018.get("theorem_pass"):
        raise SystemExit("018 theorem_pass is not true")

    residue_support = {}
    for u, v in g60_edges:
        key = support_key(u % 15, v % 15)
        residue_support.setdefault(key, []).append((u, v))

    rows = []
    per_state = {}

    for state in STATES:
        prof = a017["per_state"][state]
        observed_path = [residue_pair(pair) for pair in prof["closed_path"][:-1]]
        observed_cycle = canonical_cycle(tuple(observed_path))
        anchor_set = sorted({x for pair in observed_path for x in pair})
        sizes = [len(pair) for pair in observed_path]

        candidates = []
        for partition in set_partitions_fixed_sizes(anchor_set, sizes):
            # Every unordered partition gets all ordered 3-cycles.
            for ordered in itertools.permutations(partition, 3):
                if len(set(ordered)) != 3:
                    continue
                if not all(step_supported(ordered[i], ordered[(i + 1) % 3], residue_support) for i in range(3)):
                    continue
                canon = canonical_cycle(tuple(ordered))
                if canon != tuple(ordered):
                    continue

                support_counts = [
                    step_support_count(ordered[i], ordered[(i + 1) % 3], residue_support)
                    for i in range(3)
                ]
                candidates.append({
                    "cycle": [list(x) for x in ordered],
                    "support_counts": support_counts,
                    "support_sum": sum(support_counts),
                    "min_support": min(support_counts),
                    "max_support": max(support_counts),
                    "matches_observed_cycle": tuple(ordered) == observed_cycle,
                })

        observed_found = any(c["matches_observed_cycle"] for c in candidates)

        support_sums = sorted(set(c["support_sum"] for c in candidates))
        observed_support_sum = None
        observed_rank_by_support_sum_desc = None
        if observed_found:
            observed = [c for c in candidates if c["matches_observed_cycle"]][0]
            observed_support_sum = observed["support_sum"]
            greater = sum(1 for c in candidates if c["support_sum"] > observed_support_sum)
            observed_rank_by_support_sum_desc = greater + 1

        per_state[state] = {
            "anchor_residue_set": anchor_set,
            "observed_residue_cycle": [list(x) for x in observed_cycle],
            "pair_sizes": sizes,
            "candidate_count": len(candidates),
            "observed_found": observed_found,
            "observed_support_sum": observed_support_sum,
            "observed_rank_by_support_sum_desc": observed_rank_by_support_sum_desc,
            "support_sum_values": support_sums,
            "candidate_examples_first_20": candidates[:20],
        }

        for idx, c in enumerate(candidates):
            rows.append({
                "state": state,
                "candidate_index": idx,
                "cycle": c["cycle"],
                "support_counts": c["support_counts"],
                "support_sum": c["support_sum"],
                "min_support": c["min_support"],
                "max_support": c["max_support"],
                "matches_observed_cycle": c["matches_observed_cycle"],
            })

    total_candidates = len(rows)
    observed_found_all = all(per_state[s]["observed_found"] for s in STATES)
    unique_all = all(per_state[s]["candidate_count"] == 1 for s in STATES)

    checks = {
        "project22_012_theorem_pass": bool(a012.get("theorem_pass")),
        "anchor_quotient_pair_017_theorem_pass": bool(a017.get("theorem_pass")),
        "lift_mask_sheet_018_theorem_pass": bool(a018.get("theorem_pass")),
        "g60_edge_count_is_120": len(g60_edges) == 120,
        "all_observed_cycles_found": observed_found_all,
        "all_states_have_at_least_one_candidate": all(per_state[s]["candidate_count"] > 0 for s in STATES),
    }

    result = {
        "status": "native_g60_anchor_path_candidate_census_recorded",
        "audit_id": "019",
        "inputs": {
            "project22_anchor_path_012": str(IN_012),
            "anchor_quotient_pair_theorem_017": str(IN_017),
            "lift_mask_sheet_selector_018": str(IN_018),
            "g60_edges": str(G60_EDGES),
        },
        "total_candidate_count": total_candidates,
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "theorem_pass": all(checks.values()),
        "observed_unique_in_all_states": unique_all,
        "interpretation": (
            "This enumerates closed three-step residue-pair cycles using each state's observed anchor residue set "
            "and pair-size profile, keeping only cycles supported by native mod15 G60 residue-pair edges. If the observed "
            "cycle is unique, residue-pair support already selects the anchor path. If not, another selector layer is needed."
        ),
        "boundary": (
            "This is a candidate census over observed anchor residue sets and observed pair-size profiles. It does not derive "
            "the anchor residue sets themselves, does not derive the full local cell from native G60 provenance, does not test "
            "station fields, does not select unique relay mediators, does not derive the full role-labeled shared_B universe, "
            "and does not close Gap A."
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
            "support_counts",
            "support_sum",
            "min_support",
            "max_support",
            "matches_observed_cycle",
        ])
        for r in rows:
            w.writerow([
                r["state"],
                r["candidate_index"],
                json.dumps(r["cycle"]),
                " ".join(str(x) for x in r["support_counts"]),
                r["support_sum"],
                r["min_support"],
                r["max_support"],
                "1" if r["matches_observed_cycle"] else "0",
            ])

    lines = []
    lines.append("# Native G60 anchor path candidate census 019")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Given each state's anchor residue set and native mod15 quotient-pair support, how many closed three-step residue-pair paths exist?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_pass: `" + str(result["theorem_pass"]) + "`")
    lines.append("- total_candidate_count: `" + str(total_candidates) + "`")
    lines.append("- observed_unique_in_all_states: `" + str(unique_all) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - anchor_residue_set: `" + str(p["anchor_residue_set"]) + "`")
        lines.append("  - pair_sizes: `" + str(p["pair_sizes"]) + "`")
        lines.append("  - observed_residue_cycle: `" + str(p["observed_residue_cycle"]) + "`")
        lines.append("  - candidate_count: `" + str(p["candidate_count"]) + "`")
        lines.append("  - observed_found: `" + str(p["observed_found"]) + "`")
        lines.append("  - observed_support_sum: `" + str(p["observed_support_sum"]) + "`")
        lines.append("  - observed_rank_by_support_sum_desc: `" + str(p["observed_rank_by_support_sum_desc"]) + "`")
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
    print("total_candidate_count", total_candidates)
    print("observed_unique_in_all_states", unique_all)
    for state in STATES:
        p = per_state[state]
        print(state, "candidate_count", p["candidate_count"], "observed_found", p["observed_found"], "observed_rank", p["observed_rank_by_support_sum_desc"])


if __name__ == "__main__":
    main()
