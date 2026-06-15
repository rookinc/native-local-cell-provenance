#!/usr/bin/env python3
import csv
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_011 = ROOT / "artifacts/json/native_g60_unlifted_anchor_relay_cover_011.v1.json"
IN_020 = ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json"
IN_027 = ROOT / "artifacts/json/gap_a_direct_anchor_selector_assault_027.v1.json"
G60_EDGES = ROOT / "source/project18_payload/g60_local_edges.csv"

OUT_JSON = ROOT / "artifacts/json/native_g60_anchor_residue_set_selector_audit_028.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_g60_anchor_residue_set_selector_audit_028.v1.csv"
OUT_NOTE = ROOT / "notes/native_g60_anchor_residue_set_selector_audit_028.md"

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
    if state == "O0":
        return 0, 0
    if state == "O1":
        return 0, 1
    if state == "B0":
        return 1, 0
    if state == "B1":
        return 1, 1
    raise ValueError(state)


def residue_count_law(b, r):
    return 6 - b * (1 - r)


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


def relay_obligations_from_011(a011):
    obligations = {s: [] for s in STATES}
    relay_hits = {s: set() for s in STATES}
    unique_hits = {s: set() for s in STATES}

    for row in a011["rows"]:
        state = row["state"]
        hits = sorted({int(h["hit"]) for h in row.get("unlifted_hits", [])})
        if not hits:
            continue
        obligations[state].append({
            "step": int(row.get("step", -1)),
            "allowed_hits": hits,
        })
        relay_hits[state].update(hits)
        if len(hits) == 1:
            unique_hits[state].add(hits[0])

    return obligations, relay_hits, unique_hits


def satisfies_relay_obligations(residue_set, obligations):
    s = set(residue_set)
    for ob in obligations:
        if not s.intersection(ob["allowed_hits"]):
            return False
    return True


def pair_support_weight(a, b, residue_support):
    return len(residue_support.get(support_key(a, b), []))


def set_support_features(residue_set, residue_support):
    s = set(residue_set)
    comp = set(RESIDUES).difference(s)

    internal_supported = 0
    internal_weight = 0
    internal_missing = 0

    for a, b in itertools.combinations(sorted(s), 2):
        w = pair_support_weight(a, b, residue_support)
        if w:
            internal_supported += 1
            internal_weight += w
        else:
            internal_missing += 1

    boundary_supported = 0
    boundary_weight = 0
    for a in sorted(s):
        for b in sorted(comp):
            w = pair_support_weight(a, b, residue_support)
            if w:
                boundary_supported += 1
                boundary_weight += w

    complement_supported = 0
    complement_weight = 0
    for a, b in itertools.combinations(sorted(comp), 2):
        w = pair_support_weight(a, b, residue_support)
        if w:
            complement_supported += 1
            complement_weight += w

    return {
        "internal_supported_pair_count": internal_supported,
        "internal_support_weight": internal_weight,
        "internal_missing_pair_count": internal_missing,
        "boundary_supported_pair_count": boundary_supported,
        "boundary_support_weight": boundary_weight,
        "complement_supported_pair_count": complement_supported,
        "complement_support_weight": complement_weight,
    }


def sig(values):
    return ",".join(str(x) for x in sorted(values))


def feature_combo_search(state_rows, feature_names):
    observed = [r for r in state_rows if r["matches_observed_residue_set"]]
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
            if len(matches) == 1 and matches[0]["matches_observed_residue_set"]:
                exact.append({
                    "features": list(combo),
                    "observed_values": list(obs_val),
                    "width": width,
                })

    exact.sort(key=lambda x: (x["width"], x["features"]))
    return exact


def main():
    a011 = load_json(IN_011)
    a020 = load_json(IN_020)
    a027 = load_json(IN_027)

    if not a011.get("theorem_pass"):
        raise SystemExit("011 theorem_pass is not true")
    if not a020.get("theorem_pass"):
        raise SystemExit("020 theorem_pass is not true")
    if a027.get("status") != "gap_a_direct_anchor_selector_assault_recorded":
        raise SystemExit("027 status is unexpected")

    edges = load_edges(G60_EDGES)
    residue_support = {}
    for u, v in edges:
        residue_support.setdefault(support_key(u % 15, v % 15), []).append((u, v))

    obligations_by_state, relay_hits_by_state, unique_hits_by_state = relay_obligations_from_011(a011)

    rows = []
    per_state = {}

    feature_names = [
        "sum_residues",
        "sum_mod15",
        "min_residue",
        "max_residue",
        "span",
        "even_count",
        "odd_count",
        "c_overlap_count",
        "c_overlap_signature",
        "expected_c_overlap_exact",
        "relay_hit_overlap_count",
        "relay_hit_overlap_signature",
        "contains_all_relay_hits",
        "unique_relay_hit_overlap_count",
        "contains_all_unique_relay_hits",
        "internal_supported_pair_count",
        "internal_support_weight",
        "internal_missing_pair_count",
        "boundary_supported_pair_count",
        "boundary_support_weight",
        "complement_supported_pair_count",
        "complement_support_weight",
    ]

    for state in STATES:
        b, r = bits(state)
        count = residue_count_law(b, r)

        observed_set = set(int(x) for x in a020["per_state"][state]["anchor_residue_set"])
        c_values = set(C_VALUES[state])
        expected_overlap = expected_overlap_markers(b, r)

        relay_hits = set(relay_hits_by_state[state])
        unique_hits = set(unique_hits_by_state[state])
        obligations = obligations_by_state[state]

        state_rows = []
        candidate_index = 0

        for residue_set_tuple in itertools.combinations(RESIDUES, count):
            residue_set = set(residue_set_tuple)
            if not satisfies_relay_obligations(residue_set, obligations):
                continue

            c_overlap = residue_set.intersection(c_values)
            relay_overlap = residue_set.intersection(relay_hits)
            unique_overlap = residue_set.intersection(unique_hits)
            support_features = set_support_features(residue_set, residue_support)

            features = {
                "sum_residues": sum(residue_set),
                "sum_mod15": sum(residue_set) % 15,
                "min_residue": min(residue_set),
                "max_residue": max(residue_set),
                "span": max(residue_set) - min(residue_set),
                "even_count": sum(1 for x in residue_set if x % 2 == 0),
                "odd_count": sum(1 for x in residue_set if x % 2 == 1),
                "c_overlap_count": len(c_overlap),
                "c_overlap_signature": sig(c_overlap),
                "expected_c_overlap_exact": c_overlap == expected_overlap,
                "relay_hit_overlap_count": len(relay_overlap),
                "relay_hit_overlap_signature": sig(relay_overlap),
                "contains_all_relay_hits": relay_hits.issubset(residue_set),
                "unique_relay_hit_overlap_count": len(unique_overlap),
                "contains_all_unique_relay_hits": unique_hits.issubset(residue_set),
            }
            features.update(support_features)

            rec = {
                "state": state,
                "candidate_index": candidate_index,
                "residue_set": sorted(residue_set),
                "matches_observed_residue_set": residue_set == observed_set,
                "features": features,
            }
            rows.append(rec)
            state_rows.append(rec)
            candidate_index += 1

        observed_found = any(r["matches_observed_residue_set"] for r in state_rows)
        exact_selectors = feature_combo_search(state_rows, feature_names)

        per_state[state] = {
            "shell_bit": b,
            "rank_bit": r,
            "residue_count_law": count,
            "observed_anchor_residue_set": sorted(observed_set),
            "c_values": sorted(c_values),
            "expected_c_overlap": sorted(expected_overlap),
            "relay_hits": sorted(relay_hits),
            "unique_relay_hits": sorted(unique_hits),
            "candidate_count_after_relay_obligations": len(state_rows),
            "observed_found": observed_found,
            "observed_candidate_index": (
                [r["candidate_index"] for r in state_rows if r["matches_observed_residue_set"]] or [None]
            )[0],
            "exact_feature_selectors_first_30": exact_selectors[:30],
            "exact_feature_selector_count": len(exact_selectors),
        }

    checks = {
        "unlifted_relay_cover_011_theorem_pass": bool(a011.get("theorem_pass")),
        "candidate_census_020_theorem_pass": bool(a020.get("theorem_pass")),
        "direct_assault_027_recorded": a027.get("status") == "gap_a_direct_anchor_selector_assault_recorded",
        "g60_edge_count_is_120": len(edges) == 120,
        "all_observed_residue_sets_found": all(per_state[s]["observed_found"] for s in STATES),
        "all_states_have_exact_feature_selector": all(per_state[s]["exact_feature_selector_count"] > 0 for s in STATES),
    }

    result = {
        "status": "native_g60_anchor_residue_set_selector_audit_recorded",
        "audit_id": "028",
        "inputs": {
            "unlifted_relay_cover_011": str(IN_011),
            "candidate_census_fixed_020": str(IN_020),
            "direct_anchor_selector_assault_027": str(IN_027),
            "g60_edges": str(G60_EDGES),
        },
        "uses_observed_anchor_residue_sets_for_generation": False,
        "uses_observed_anchor_residue_sets_for_validation": True,
        "generation_rule": "all residue subsets of size 6 - b*(1-r) satisfying same-state unlifted relay obligations from artifact 011",
        "feature_names": feature_names,
        "per_state": per_state,
        "rows": rows,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "Artifact 027 showed that the global cycle universe is too broad. This audit moves one layer earlier and "
            "asks whether simple residue-set features can identify the observed anchor residue sets before cycle ranking. "
            "Exact feature selectors here are candidate directions, not final native provenance unless independently justified."
        ),
        "boundary": (
            "This is a residue-set feature audit. It does not derive a native selector theorem by itself, does not test station fields, "
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
            "matches_observed_residue_set",
            "residue_set",
            "sum_residues",
            "sum_mod15",
            "c_overlap_signature",
            "expected_c_overlap_exact",
            "relay_hit_overlap_signature",
            "contains_all_relay_hits",
            "internal_supported_pair_count",
            "internal_support_weight",
            "boundary_supported_pair_count",
            "boundary_support_weight",
        ])
        for r in rows:
            fts = r["features"]
            w.writerow([
                r["state"],
                r["candidate_index"],
                "1" if r["matches_observed_residue_set"] else "0",
                json.dumps(r["residue_set"]),
                fts["sum_residues"],
                fts["sum_mod15"],
                fts["c_overlap_signature"],
                "1" if fts["expected_c_overlap_exact"] else "0",
                fts["relay_hit_overlap_signature"],
                "1" if fts["contains_all_relay_hits"] else "0",
                fts["internal_supported_pair_count"],
                fts["internal_support_weight"],
                fts["boundary_supported_pair_count"],
                fts["boundary_support_weight"],
            ])

    lines = []
    lines.append("# Native G60 anchor residue-set selector audit 028")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append("Can simple residue-set features select the observed anchor residue sets before cycle ranking?")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- all_checks_pass: `" + str(result["all_checks_pass"]) + "`")
    lines.append("- uses_observed_anchor_residue_sets_for_generation: `False`")
    lines.append("- uses_observed_anchor_residue_sets_for_validation: `True`")
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - residue_count_law: `" + str(p["residue_count_law"]) + "`")
        lines.append("  - observed_anchor_residue_set: `" + str(p["observed_anchor_residue_set"]) + "`")
        lines.append("  - c_values: `" + str(p["c_values"]) + "`")
        lines.append("  - expected_c_overlap: `" + str(p["expected_c_overlap"]) + "`")
        lines.append("  - relay_hits: `" + str(p["relay_hits"]) + "`")
        lines.append("  - unique_relay_hits: `" + str(p["unique_relay_hits"]) + "`")
        lines.append("  - candidate_count_after_relay_obligations: `" + str(p["candidate_count_after_relay_obligations"]) + "`")
        lines.append("  - observed_found: `" + str(p["observed_found"]) + "`")
        lines.append("  - observed_candidate_index: `" + str(p["observed_candidate_index"]) + "`")
        lines.append("  - exact_feature_selector_count: `" + str(p["exact_feature_selector_count"]) + "`")
        lines.append("  - exact_feature_selectors_first_30: `" + str(p["exact_feature_selectors_first_30"]) + "`")
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
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "candidates", p["candidate_count_after_relay_obligations"],
            "observed_found", p["observed_found"],
            "exact_selectors", p["exact_feature_selector_count"],
        )


if __name__ == "__main__":
    main()
