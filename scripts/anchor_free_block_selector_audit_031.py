#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_030 = ROOT / "artifacts/json/anchor_free_block_law_search_030.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/anchor_free_block_selector_audit_031.v1.json"
OUT_CSV = ROOT / "artifacts/csv/anchor_free_block_selector_audit_031.v1.csv"
OUT_NOTE = ROOT / "notes/anchor_free_block_selector_audit_031.md"

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


def load_edges(path):
    edges = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            edges.append((int(row["local_u"]), int(row["local_v"])))
    return edges


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


def support_key(a, b):
    return tuple(sorted((int(a), int(b))))


def support_weight(a, b, residue_support):
    return len(residue_support.get(support_key(a, b), []))


def cut_weight(a_set, b_set, residue_support):
    supported = 0
    weight = 0
    for a in a_set:
        for b in b_set:
            w = support_weight(a, b, residue_support)
            if w:
                supported += 1
                weight += w
    return supported, weight


def internal_weight(s, residue_support):
    supported = 0
    weight = 0
    missing = 0
    for a, b in itertools.combinations(sorted(s), 2):
        w = support_weight(a, b, residue_support)
        if w:
            supported += 1
            weight += w
        else:
            missing += 1
    return supported, weight, missing


def circular_distance(a, b, n=15):
    d = abs(int(a) - int(b)) % n
    return min(d, n - d)


def distance_signature(a_set, b_set):
    vals = []
    nearest = []
    for a in sorted(a_set):
        ds = sorted(circular_distance(a, b) for b in b_set)
        nearest.append(ds[0])
        vals.extend(ds)
    return {
        "nearest_signature": ",".join(str(x) for x in sorted(nearest)),
        "nearest_sum": sum(nearest),
        "nearest_max": max(nearest) if nearest else None,
        "all_signature": ",".join(str(x) for x in sorted(vals)),
    }


def gap_signature(vals):
    xs = sorted(vals)
    gaps = []
    for i, x in enumerate(xs):
        y = xs[(i + 1) % len(xs)]
        gaps.append((y - x) % 15)
    return ",".join(str(x) for x in sorted(gaps))


def sig(vals):
    return ",".join(str(x) for x in sorted(vals))


def relay_hits_by_state(a011):
    out = {s: set() for s in STATES}
    for row in a011["rows"]:
        state = row.get("state")
        if state not in out:
            continue
        hits = sorted({int(h["hit"]) for h in row.get("unlifted_hits", [])})
        out[state].update(hits)
    return out


def feature_combo_search(state_rows, feature_names):
    observed = [r for r in state_rows if r["matches_observed_free_block"]]
    if len(observed) != 1:
        return []
    obs = observed[0]

    exact = []
    for width in (1, 2, 3):
        for combo in itertools.combinations(feature_names, width):
            obs_val = tuple(obs["features"][name] for name in combo)
            matches = [
                r for r in state_rows
                if tuple(r["features"][name] for name in combo) == obs_val
            ]
            if len(matches) == 1 and matches[0]["matches_observed_free_block"]:
                exact.append({
                    "features": list(combo),
                    "observed_values": list(obs_val),
                    "width": width,
                })
    exact.sort(key=lambda x: (x["width"], x["features"]))
    return exact


def rank_by_feature(state_rows, feature_name, reverse):
    rows = sorted(
        state_rows,
        key=lambda r: (
            -r["features"][feature_name] if reverse else r["features"][feature_name],
            r["free_block"],
        ),
    )
    out = {}
    for i, r in enumerate(rows, start=1):
        out[tuple(r["free_block"])] = i
    return out


def main():
    a011 = load_json(IN_011)
    a020 = load_json(IN_020)
    a030 = load_json(IN_030)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if a030.get("status") != "anchor_free_block_law_search_recorded":
        raise SystemExit("030 status unexpected")

    edges = load_edges(G60_EDGES)
    residue_support = {}
    for u, v in edges:
        residue_support.setdefault(support_key(u % 15, v % 15), []).append((u, v))

    relay_by_state = relay_hits_by_state(a011)

    feature_names = [
        "sum_free",
        "sum_free_mod15",
        "min_free",
        "max_free",
        "gap_signature",
        "c_overlap_signature",
        "expected_c_overlap_exact",
        "free_internal_supported_count",
        "free_internal_weight",
        "free_internal_missing_count",
        "relay_to_free_supported_count",
        "relay_to_free_weight",
        "c_to_free_supported_count",
        "c_to_free_weight",
        "free_to_complement_supported_count",
        "free_to_complement_weight",
        "nearest_c_signature",
        "nearest_c_sum",
        "nearest_relay_signature",
        "nearest_relay_sum",
    ]

    numeric_rank_features = [
        "sum_free",
        "sum_free_mod15",
        "min_free",
        "max_free",
        "free_internal_supported_count",
        "free_internal_weight",
        "free_internal_missing_count",
        "relay_to_free_supported_count",
        "relay_to_free_weight",
        "c_to_free_supported_count",
        "c_to_free_weight",
        "free_to_complement_supported_count",
        "free_to_complement_weight",
        "nearest_c_sum",
        "nearest_relay_sum",
    ]

    all_rows = []
    per_state = {}

    for state in STATES:
        b, r = bits(state)
        relay = set(relay_by_state[state])
        c_values = set(C_VALUES[state])
        expected_overlap = expected_overlap_markers(b, r)

        observed_set = set(int(x) for x in a020["per_state"][state]["anchor_residue_set"])
        observed_free = observed_set.difference(relay)
        free_size = len(observed_free)

        candidates = []
        universe = [x for x in RESIDUES if x not in relay]

        for combo in itertools.combinations(universe, free_size):
            free = set(combo)
            if free.intersection(c_values) != expected_overlap:
                continue

            full_set = relay.union(free)
            comp = set(RESIDUES).difference(full_set)

            fi_s, fi_w, fi_m = internal_weight(free, residue_support)
            rf_s, rf_w = cut_weight(relay, free, residue_support)
            cf_s, cf_w = cut_weight(c_values, free, residue_support)
            fc_s, fc_w = cut_weight(free, comp, residue_support)

            cdist = distance_signature(free, c_values)
            rdist = distance_signature(free, relay)

            features = {
                "sum_free": sum(free),
                "sum_free_mod15": sum(free) % 15,
                "min_free": min(free),
                "max_free": max(free),
                "gap_signature": gap_signature(free),
                "c_overlap_signature": sig(free.intersection(c_values)),
                "expected_c_overlap_exact": free.intersection(c_values) == expected_overlap,
                "free_internal_supported_count": fi_s,
                "free_internal_weight": fi_w,
                "free_internal_missing_count": fi_m,
                "relay_to_free_supported_count": rf_s,
                "relay_to_free_weight": rf_w,
                "c_to_free_supported_count": cf_s,
                "c_to_free_weight": cf_w,
                "free_to_complement_supported_count": fc_s,
                "free_to_complement_weight": fc_w,
                "nearest_c_signature": cdist["nearest_signature"],
                "nearest_c_sum": cdist["nearest_sum"],
                "nearest_relay_signature": rdist["nearest_signature"],
                "nearest_relay_sum": rdist["nearest_sum"],
            }

            rec = {
                "state": state,
                "shell_bit": b,
                "rank_bit": r,
                "relay_block": sorted(relay),
                "c_values": sorted(c_values),
                "expected_c_overlap": sorted(expected_overlap),
                "free_block": sorted(free),
                "full_anchor_set": sorted(full_set),
                "matches_observed_free_block": free == observed_free,
                "features": features,
            }
            candidates.append(rec)

        exact_selectors = feature_combo_search(candidates, feature_names)

        observed = [x for x in candidates if x["matches_observed_free_block"]]
        observed_found = len(observed) == 1
        observed_rec = observed[0] if observed_found else None

        rank_profiles = []
        if observed_found:
            for fn in numeric_rank_features:
                for reverse in (False, True):
                    ranks = rank_by_feature(candidates, fn, reverse)
                    obs_rank = ranks[tuple(observed_rec["free_block"])]
                    rank_profiles.append({
                        "feature": fn,
                        "order": "desc" if reverse else "asc",
                        "observed_rank": obs_rank,
                    })
            rank_profiles.sort(key=lambda x: (x["observed_rank"], x["feature"], x["order"]))

        per_state[state] = {
            "shell_bit": b,
            "rank_bit": r,
            "relay_block": sorted(relay),
            "c_values": sorted(c_values),
            "expected_c_overlap": sorted(expected_overlap),
            "observed_free_block": sorted(observed_free),
            "free_size": free_size,
            "candidate_count": len(candidates),
            "observed_found": observed_found,
            "observed_features": observed_rec["features"] if observed_found else None,
            "exact_feature_selector_count": len(exact_selectors),
            "exact_feature_selectors_first_30": exact_selectors[:30],
            "best_rank_profiles_first_20": rank_profiles[:20],
        }

        for idx, rec in enumerate(candidates):
            rec["candidate_index"] = idx
            all_rows.append(rec)

    # Common feature selector across all states.
    common_exact_feature_sets = []
    for width in (1, 2, 3):
        for combo in itertools.combinations(feature_names, width):
            ok = True
            for state in STATES:
                state_rows = [r for r in all_rows if r["state"] == state]
                obs = [r for r in state_rows if r["matches_observed_free_block"]][0]
                obs_val = tuple(obs["features"][name] for name in combo)
                matches = [
                    r for r in state_rows
                    if tuple(r["features"][name] for name in combo) == obs_val
                ]
                if len(matches) != 1 or not matches[0]["matches_observed_free_block"]:
                    ok = False
                    break
            if ok:
                common_exact_feature_sets.append(list(combo))
        if common_exact_feature_sets:
            break

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "free_block_law_search_030_recorded": a030.get("status") == "anchor_free_block_law_search_recorded",
        "g60_edge_count_is_120": len(edges) == 120,
        "all_observed_free_blocks_found": all(per_state[s]["observed_found"] for s in STATES),
        "all_states_have_exact_feature_selector": all(per_state[s]["exact_feature_selector_count"] > 0 for s in STATES),
    }

    result = {
        "status": "anchor_free_block_selector_audit_recorded",
        "audit_id": "031",
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "candidate_census_fixed_020": str(IN_020),
            "anchor_free_block_law_search_030": str(IN_030),
            "g60_edges": str(G60_EDGES),
        },
        "generation_rule": (
            "Given each state's relay block, free size, and expected C-overlap marker set, generate all disjoint free blocks "
            "of that size with exactly that C-overlap."
        ),
        "per_state": per_state,
        "common_exact_feature_sets_first_20": common_exact_feature_sets[:20],
        "common_exact_feature_set_count": len(common_exact_feature_sets),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "Artifact 030 found no common affine transform from relay or C values to free blocks. This audit asks a narrower selector question: "
            "inside each state's free-block candidate universe, do relational support/distance features select the observed free block?"
        ),
        "boundary": (
            "This is still a selector audit, not a native provenance theorem. It does not test station fields, select unique relay mediators, "
            "derive the full shared_B universe, or close Gap A."
        ),
        "rows": all_rows,
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
            "matches_observed_free_block",
            "relay_block",
            "free_block",
            "full_anchor_set",
            "sum_free",
            "sum_free_mod15",
            "gap_signature",
            "relay_to_free_weight",
            "c_to_free_weight",
            "nearest_c_signature",
            "nearest_relay_signature",
        ])
        for r in all_rows:
            fts = r["features"]
            w.writerow([
                r["state"],
                r["candidate_index"],
                "1" if r["matches_observed_free_block"] else "0",
                json.dumps(r["relay_block"]),
                json.dumps(r["free_block"]),
                json.dumps(r["full_anchor_set"]),
                fts["sum_free"],
                fts["sum_free_mod15"],
                fts["gap_signature"],
                fts["relay_to_free_weight"],
                fts["c_to_free_weight"],
                fts["nearest_c_signature"],
                fts["nearest_relay_signature"],
            ])

    lines = []
    lines.append("# Anchor free-block selector audit 031")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- all_checks_pass: `" + str(result["all_checks_pass"]) + "`")
    lines.append("- common_exact_feature_set_count: `" + str(len(common_exact_feature_sets)) + "`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - relay_block: `" + str(p["relay_block"]) + "`")
        lines.append("  - c_values: `" + str(p["c_values"]) + "`")
        lines.append("  - expected_c_overlap: `" + str(p["expected_c_overlap"]) + "`")
        lines.append("  - observed_free_block: `" + str(p["observed_free_block"]) + "`")
        lines.append("  - candidate_count: `" + str(p["candidate_count"]) + "`")
        lines.append("  - observed_found: `" + str(p["observed_found"]) + "`")
        lines.append("  - exact_feature_selector_count: `" + str(p["exact_feature_selector_count"]) + "`")
        lines.append("  - exact_feature_selectors_first_30: `" + str(p["exact_feature_selectors_first_30"]) + "`")
        lines.append("  - best_rank_profiles_first_20: `" + str(p["best_rank_profiles_first_20"]) + "`")
    lines.append("")
    lines.append("## Common exact feature sets first 20")
    lines.append("")
    if common_exact_feature_sets:
        for combo in common_exact_feature_sets[:20]:
            lines.append("- `" + str(combo) + "`")
    else:
        lines.append("- none")
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
    print("common_exact_feature_set_count", len(common_exact_feature_sets))
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "candidates", p["candidate_count"],
            "observed", p["observed_free_block"],
            "exact_selectors", p["exact_feature_selector_count"],
        )
    print("first_common_exact", common_exact_feature_sets[0] if common_exact_feature_sets else None)


if __name__ == "__main__":
    main()
