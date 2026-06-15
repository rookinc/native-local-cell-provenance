#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_032 = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"
IN_035 = ROOT / "artifacts/json/native_g60_relay_block_selector_from_mediators_035.v1.json"
IN_041 = ROOT / "artifacts/json/imported_station_row_extract_041.v1.json"
IN_042 = ROOT / "artifacts/json/station_scalar_join_audit_042.v1.json"

OUT_JSON = ROOT / "artifacts/json/coupled_register_residual_audit_043.v1.json"
OUT_CSV = ROOT / "artifacts/csv/coupled_register_residual_audit_043.v1.csv"
OUT_NOTE = ROOT / "notes/coupled_register_residual_audit_043.md"

STATES = ["O0", "O1", "B0", "B1"]
RESIDUES = set(range(15))

STATE_C_PATHS = {
    "O0": [11, 2, 14, 11],
    "O1": [13, 1, 10, 13],
    "B0": [2, 5, 0, 2],
    "B1": [4, 5, 2, 4],
}

FIELDS = [
    "from_A", "to_A",
    "from_B", "to_B",
    "from_C", "to_C",
    "from_slot", "to_slot",
    "from_fiber_mod15", "to_fiber_mod15",
    "A_delta", "B_delta", "C_delta", "slot_delta",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def as_int(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str) and v.strip().lstrip("-").isdigit():
        return int(v.strip())
    return None


def safe(s):
    return str(s).replace("/", "_").replace(" ", "_").replace("-", "_")


def path_edges(path):
    return [(path[i], path[i + 1]) for i in range(len(path) - 1)]


def bits(state):
    return {
        "O0": (0, 0),
        "O1": (0, 1),
        "B0": (1, 0),
        "B1": (1, 1),
    }[state]


def bit_law(vals):
    y00 = vals["O0"]
    y01 = vals["O1"]
    y10 = vals["B0"]
    y11 = vals["B1"]

    coeffs = {
        "p0": y00,
        "pb": y10 - y00,
        "pr": y01 - y00,
        "pbr": y11 - y10 - y01 + y00,
    }

    preds = {}
    for state in STATES:
        b, r = bits(state)
        preds[state] = coeffs["p0"] + coeffs["pb"] * b + coeffs["pr"] * r + coeffs["pbr"] * b * r

    return {
        "coefficients": coeffs,
        "predictions": preds,
        "coefficient_l1": sum(abs(v) for v in coeffs.values()),
    }


def row_value(row, field):
    if field == "A_delta":
        a = as_int(row.get("from_A"))
        b = as_int(row.get("to_A"))
    elif field == "B_delta":
        a = as_int(row.get("from_B"))
        b = as_int(row.get("to_B"))
    elif field == "C_delta":
        a = as_int(row.get("from_C"))
        b = as_int(row.get("to_C"))
    elif field == "slot_delta":
        a = as_int(row.get("from_slot"))
        b = as_int(row.get("to_slot"))
    else:
        return as_int(row.get(field))

    if a is None or b is None:
        return None
    return (b - a) % 15


def add_stats(features, name, vals):
    s = set()
    for v in vals:
        iv = as_int(v)
        if iv is not None:
            s.add(iv % 15)

    c = RESIDUES - s

    features[name + "__size"] = len(s)
    features[name + "__sum"] = sum(s)
    if s:
        features[name + "__min"] = min(s)
        features[name + "__max"] = max(s)
        features[name + "__range"] = max(s) - min(s)

    features[name + "__compl_size"] = len(c)
    features[name + "__compl_sum"] = sum(c)
    if c:
        features[name + "__compl_min"] = min(c)
        features[name + "__compl_max"] = max(c)
        features[name + "__compl_range"] = max(c) - min(c)

    return s


def add_set_stats(features, name, s):
    add_stats(features, name, list(s))


def joined_rows(canonical_rows):
    by_transition = defaultdict(list)
    for row in canonical_rows:
        by_transition[(as_int(row.get("from_C")), as_int(row.get("to_C")))].append(row)

    joined = {}
    checks = {}

    for state in STATES:
        rows = []
        transition_counts = {}
        for tr in path_edges(STATE_C_PATHS[state]):
            got = by_transition.get(tr, [])
            rows.extend(got)
            transition_counts[str(tr)] = len(got)

        role_classes = Counter(str(r.get("role_class")) for r in rows)
        role_pairs = Counter(str(r.get("role_pair")) for r in rows)
        station_roles = Counter(str(r.get("station_role")) for r in rows)

        joined[state] = {
            "rows": rows,
            "row_count": len(rows),
            "transition_counts": dict(transition_counts),
            "role_class_counts": dict(role_classes),
            "role_pair_counts": dict(role_pairs),
            "station_role_counts": dict(station_roles),
        }

        checks[state] = {
            "row_count_is_6": len(rows) == 6,
            "transition_counts_are_2_each": all(v == 2 for v in transition_counts.values()),
            "shared_count_is_3": role_classes.get("shared_B", 0) == 3,
            "reverse_count_is_3": role_classes.get("reverse_partner", 0) == 3,
            "role_pair_count_is_3": len(role_pairs) == 3,
            "station_role_count_is_6": len(station_roles) == 6,
        }

    return joined, checks


def target_values(a032, a035):
    targets = {
        "free_size": {},
        "free_sum": {},
        "free_min": {},
        "relay_size": {},
        "relay_sum": {},
        "relay_min": {},
        "relay_max": {},
    }

    for state in STATES:
        s032 = a032["per_state"][state]
        s035 = a035["per_state"][state]

        targets["free_size"][state] = int(s032["free_size"])
        targets["free_sum"][state] = int(s032["sum_free_target"])
        targets["free_min"][state] = int(s032["min_free_target"])

        targets["relay_size"][state] = int(s035["size_target"])
        targets["relay_sum"][state] = int(s035["sum_target"])
        targets["relay_min"][state] = int(s035["min_target"])
        targets["relay_max"][state] = int(s035["max_target"])

    return targets


def build_state_features(state, rows):
    features = {}
    seed_sets = {}

    c_nodes = set(STATE_C_PATHS[state][:-1])
    seed_sets["state_c_path"] = c_nodes
    seed_sets["state_c_compl"] = RESIDUES - c_nodes

    subsets = {
        "all": rows,
        "shared": [r for r in rows if r.get("role_class") == "shared_B"],
        "reverse": [r for r in rows if r.get("role_class") == "reverse_partner"],
        "q0": [r for r in rows if as_int(r.get("lift_q")) == 0],
        "q3": [r for r in rows if as_int(r.get("lift_q")) == 3],
    }

    for rp in sorted(set(str(r.get("role_pair")) for r in rows)):
        subsets["rolepair_" + safe(rp)] = [r for r in rows if str(r.get("role_pair")) == rp]

    for role in sorted(set(str(r.get("station_role")) for r in rows)):
        subsets["station_" + safe(role)] = [r for r in rows if str(r.get("station_role")) == role]

    for subset_name, subset_rows in subsets.items():
        features["rows__" + subset_name + "__count"] = len(subset_rows)

        for field in FIELDS:
            vals = [row_value(r, field) for r in subset_rows]
            s = add_stats(features, "set__" + subset_name + "__" + field, vals)
            if s:
                seed_sets[subset_name + "__" + field] = s

    # Focused coupled set operations only.
    for name, s in list(seed_sets.items()):
        for op_name, op_set in [
            ("inter_cpath", s & c_nodes),
            ("minus_cpath", s - c_nodes),
            ("cpath_minus", c_nodes - s),
            ("union_cpath", s | c_nodes),
        ]:
            add_set_stats(features, "op__" + name + "__" + op_name, op_set)

    # Role-class couplings by same field.
    for field in FIELDS:
        shared = seed_sets.get("shared__" + field, set())
        reverse = seed_sets.get("reverse__" + field, set())
        if shared or reverse:
            add_set_stats(features, "rolecouple__" + field + "__union", shared | reverse)
            add_set_stats(features, "rolecouple__" + field + "__inter", shared & reverse)
            add_set_stats(features, "rolecouple__" + field + "__shared_minus_reverse", shared - reverse)
            add_set_stats(features, "rolecouple__" + field + "__reverse_minus_shared", reverse - shared)
            add_set_stats(features, "rolecouple__" + field + "__symdiff", shared ^ reverse)

    return features, {"seed_set_count": len(seed_sets), "feature_count": len(features)}


def compare(features_by_state, target_by_state):
    common = sorted(set.intersection(*(set(features_by_state[s]) for s in STATES)))

    exact = []
    near = []

    for feature in common:
        vals = {s: features_by_state[s][feature] for s in STATES}
        err = sum(abs(vals[s] - target_by_state[s]) for s in STATES)
        item = {
            "feature": feature,
            "values": vals,
            "l1_error": err,
        }
        if err == 0:
            exact.append(item)
        else:
            near.append(item)

    exact.sort(key=lambda x: (len(x["feature"]), x["feature"]))
    near.sort(key=lambda x: (x["l1_error"], len(x["feature"]), x["feature"]))

    return exact, near


def main():
    a032 = load_json(IN_032)
    a035 = load_json(IN_035)
    a041 = load_json(IN_041)
    a042 = load_json(IN_042)

    if not a032.get("theorem_candidate_pass"):
        raise SystemExit("032 theorem_candidate_pass is not true")
    if not a035.get("theorem_candidate_pass"):
        raise SystemExit("035 theorem_candidate_pass is not true")
    if not a041.get("extract_pass"):
        raise SystemExit("041 extract_pass is not true")
    if not a042.get("audit_pass"):
        raise SystemExit("042 audit_pass is not true")

    joined, join_checks = joined_rows(a041["canonical_rows"])

    features_by_state = {}
    seed_summary = {}

    for state in STATES:
        print("building bounded coupled features for", state)
        features, summary = build_state_features(state, joined[state]["rows"])
        features_by_state[state] = features
        summary["joined_row_count"] = joined[state]["row_count"]
        summary["join_checks"] = join_checks[state]
        seed_summary[state] = summary

    targets = target_values(a032, a035)
    per_target = {}
    csv_rows = []

    for target_name, target in targets.items():
        exact, near = compare(features_by_state, target)
        per_target[target_name] = {
            "target_values": target,
            "target_bit_law": bit_law(target),
            "candidate_feature_count": len(set.intersection(*(set(features_by_state[s]) for s in STATES))),
            "exact_candidate_count": len(exact),
            "exact_candidates_first_40": exact[:40],
            "nearest_candidates_first_20": near[:20],
        }

        for item in exact[:80]:
            csv_rows.append([target_name, "exact", item["feature"], item["l1_error"], json.dumps(item["values"], sort_keys=True)])
        for item in near[:20]:
            csv_rows.append([target_name, "nearest", item["feature"], item["l1_error"], json.dumps(item["values"], sort_keys=True)])

    nontrivial = [t for t in targets if t != "free_size"]
    exact_nontrivial = sum(1 for t in nontrivial if per_target[t]["exact_candidate_count"] > 0)

    checks = {
        "free_block_scalar_032_theorem_candidate_pass": bool(a032.get("theorem_candidate_pass")),
        "relay_selector_035_theorem_candidate_pass": bool(a035.get("theorem_candidate_pass")),
        "station_extract_041_pass": bool(a041.get("extract_pass")),
        "station_scalar_join_042_pass": bool(a042.get("audit_pass")),
        "all_join_checks": all(all(v.values()) for v in join_checks.values()),
        "target_count": len(targets),
        "nontrivial_target_count": len(nontrivial),
        "nontrivial_targets_with_exact_coupled_candidate": exact_nontrivial,
        "all_nontrivial_targets_have_exact_candidate": exact_nontrivial == len(nontrivial),
    }

    result = {
        "status": "coupled_register_residual_audit_recorded",
        "audit_id": "043",
        "checks": checks,
        "audit_pass": all([
            checks["free_block_scalar_032_theorem_candidate_pass"],
            checks["relay_selector_035_theorem_candidate_pass"],
            checks["station_extract_041_pass"],
            checks["station_scalar_join_042_pass"],
            checks["all_join_checks"],
        ]),
        "seed_summary": seed_summary,
        "joined_state_summary": {
            s: {k: v for k, v in joined[s].items() if k != "rows"}
            for s in STATES
        },
        "per_target": per_target,
        "interpretation": (
            "Artifact 042 showed that scalar targets are not raw station-row aggregate readouts. "
            "This bounded audit searches coupled residue readouts using complements, C-path exclusions, role-class gates, "
            "role-pair gates, station-role gates, and q gates."
        ),
        "boundary": (
            "This is a bounded reduced four-state candidate search. Exact candidates are hypotheses, not full native derivations. "
            "This does not derive the full role-labeled shared_B universe and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "kind", "feature", "l1_error", "values"])
        for row in csv_rows:
            w.writerow(row)

    lines = []
    lines.append("# Coupled register residual audit 043")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(result["audit_pass"]) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Seed summary")
    lines.append("")
    for state in STATES:
        lines.append("- " + state + ": `" + str(seed_summary[state]) + "`")
    lines.append("")
    lines.append("## Target results")
    lines.append("")
    for target_name in sorted(per_target):
        p = per_target[target_name]
        lines.append("- " + target_name + ":")
        lines.append("  - target_values: `" + str(p["target_values"]) + "`")
        lines.append("  - target_bit_law: `" + str(p["target_bit_law"]) + "`")
        lines.append("  - candidate_feature_count: `" + str(p["candidate_feature_count"]) + "`")
        lines.append("  - exact_candidate_count: `" + str(p["exact_candidate_count"]) + "`")
        lines.append("  - exact_candidates_first_10: `" + str(p["exact_candidates_first_40"][:10]) + "`")
        lines.append("  - nearest_candidates_first_5: `" + str(p["nearest_candidates_first_20"][:5]) + "`")
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
    print("audit_pass", result["audit_pass"])
    print("nontrivial_targets_with_exact_coupled_candidate", exact_nontrivial, "of", len(nontrivial))
    for state in STATES:
        print(state, seed_summary[state])
    for target_name in sorted(per_target):
        p = per_target[target_name]
        print(target_name, "exact", p["exact_candidate_count"], "nearest", p["nearest_candidates_first_20"][:2])


if __name__ == "__main__":
    main()
