#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_032 = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"
IN_035 = ROOT / "artifacts/json/native_g60_relay_block_selector_from_mediators_035.v1.json"
IN_041 = ROOT / "artifacts/json/imported_station_row_extract_041.v1.json"
IN_043 = ROOT / "artifacts/json/coupled_register_residual_audit_043.v1.json"

OUT_JSON = ROOT / "artifacts/json/residual_correction_law_audit_044.v1.json"
OUT_CSV = ROOT / "artifacts/csv/residual_correction_law_audit_044.v1.csv"
OUT_NOTE = ROOT / "notes/residual_correction_law_audit_044.md"

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

COEFFS = list(range(-6, 7))
OFFSETS = list(range(-20, 21))
MAX_SAVE = 40


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


def bits(state):
    return {
        "O0": (0, 0),
        "O1": (0, 1),
        "B0": (1, 0),
        "B1": (1, 1),
    }[state]


def bit_law(vals):
    y00 = int(vals["O0"])
    y01 = int(vals["O1"])
    y10 = int(vals["B0"])
    y11 = int(vals["B1"])

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
        "formula": "p0 + pb*b + pr*r + pbr*b*r",
        "coefficients": coeffs,
        "predictions": preds,
        "coefficient_l1": sum(abs(v) for v in coeffs.values()),
        "max_abs_coeff": max(abs(v) for v in coeffs.values()),
    }


def path_edges(path):
    return [(path[i], path[i + 1]) for i in range(len(path) - 1)]


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


def add_set_features(features, name, vals):
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

        joined[state] = rows
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


def build_correction_features(state, rows):
    features = {}

    b, r = bits(state)
    path = STATE_C_PATHS[state]
    c_nodes = set(path[:-1])

    features["bit__const"] = 1
    features["bit__branch_b"] = b
    features["bit__rank_r"] = r
    features["bit__product_br"] = b * r
    features["bit__ordinary"] = 1 - b
    features["bit__branch"] = b
    features["bit__rank0"] = 1 - r
    features["bit__rank1"] = r
    features["onehot__O0"] = 1 if state == "O0" else 0
    features["onehot__O1"] = 1 if state == "O1" else 0
    features["onehot__B0"] = 1 if state == "B0" else 0
    features["onehot__B1"] = 1 if state == "B1" else 0

    features["cpath__sum"] = sum(c_nodes)
    features["cpath__min"] = min(c_nodes)
    features["cpath__max"] = max(c_nodes)
    features["cpath__range"] = max(c_nodes) - min(c_nodes)
    features["cpath__compl_sum"] = sum(RESIDUES - c_nodes)
    features["cpath__compl_min"] = min(RESIDUES - c_nodes)
    features["cpath__compl_max"] = max(RESIDUES - c_nodes)

    subsets = {
        "all": rows,
        "shared": [x for x in rows if x.get("role_class") == "shared_B"],
        "reverse": [x for x in rows if x.get("role_class") == "reverse_partner"],
        "q0": [x for x in rows if as_int(x.get("lift_q")) == 0],
        "q3": [x for x in rows if as_int(x.get("lift_q")) == 3],
    }

    for rp in sorted(set(str(x.get("role_pair")) for x in rows)):
        subsets["rolepair_" + safe(rp)] = [x for x in rows if str(x.get("role_pair")) == rp]

    for role in sorted(set(str(x.get("station_role")) for x in rows)):
        subsets["station_" + safe(role)] = [x for x in rows if str(x.get("station_role")) == role]

    seed_sets = {}

    for subset_name, subset_rows in subsets.items():
        features["rows__" + subset_name + "__count"] = len(subset_rows)

        for field in FIELDS:
            vals = [row_value(x, field) for x in subset_rows]
            s = add_set_features(features, "set__" + subset_name + "__" + field, vals)
            if s:
                seed_sets[subset_name + "__" + field] = s

    # Focus on the neighborhood 043 already identified.
    for name, s in seed_sets.items():
        add_set_features(features, "op__" + name + "__minus_cpath", s - c_nodes)
        add_set_features(features, "op__" + name + "__cpath_minus", c_nodes - s)
        add_set_features(features, "op__" + name + "__inter_cpath", s & c_nodes)
        add_set_features(features, "op__" + name + "__union_cpath", s | c_nodes)

    return features


def exact_correction_candidates(base, target, corr_features_by_state):
    exact = []
    near = []

    common = sorted(set.intersection(*(set(corr_features_by_state[s].keys()) for s in STATES)))

    residual = {s: target[s] - base[s] for s in STATES}

    # Always record the pure residual bit law. It is exact by construction, but
    # coefficient size tells whether the correction is small.
    residual_bit_law = bit_law(residual)

    for feature in common:
        fvals = {s: int(corr_features_by_state[s][feature]) for s in STATES}

        for a in COEFFS:
            if a == 0:
                continue

            # exact target = base + a*feature + c
            needed = [target[s] - base[s] - a * fvals[s] for s in STATES]
            if len(set(needed)) == 1 and needed[0] in OFFSETS:
                c = needed[0]
                vals = {s: base[s] + a * fvals[s] + c for s in STATES}
                exact.append({
                    "kind": "affine_feature_correction",
                    "feature": feature,
                    "a": a,
                    "c": c,
                    "feature_values": fvals,
                    "corrected_values": vals,
                    "complexity": abs(a) + abs(c) + len(feature) / 1000.0,
                })
            else:
                # nearest with best offset
                offsets = Counter(needed)
                best_c, _ = offsets.most_common(1)[0]
                if best_c in OFFSETS:
                    vals = {s: base[s] + a * fvals[s] + best_c for s in STATES}
                    err = sum(abs(vals[s] - target[s]) for s in STATES)
                    near.append({
                        "kind": "affine_feature_correction",
                        "feature": feature,
                        "a": a,
                        "c": best_c,
                        "feature_values": fvals,
                        "corrected_values": vals,
                        "l1_error": err,
                        "complexity": err * 1000 + abs(a) + abs(best_c) + len(feature) / 1000.0,
                    })

    exact.sort(key=lambda x: (x["complexity"], len(x["feature"]), x["feature"], x["a"], x["c"]))
    near.sort(key=lambda x: (x["l1_error"], x["complexity"], len(x["feature"]), x["feature"]))

    return residual, residual_bit_law, exact[:MAX_SAVE], near[:MAX_SAVE]


def main():
    a032 = load_json(IN_032)
    a035 = load_json(IN_035)
    a041 = load_json(IN_041)
    a043 = load_json(IN_043)

    if not a032.get("theorem_candidate_pass"):
        raise SystemExit("032 theorem_candidate_pass is not true")
    if not a035.get("theorem_candidate_pass"):
        raise SystemExit("035 theorem_candidate_pass is not true")
    if not a041.get("extract_pass"):
        raise SystemExit("041 extract_pass is not true")
    if not a043.get("audit_pass"):
        raise SystemExit("043 audit_pass is not true")

    targets = target_values(a032, a035)
    joined, join_checks = joined_rows(a041["canonical_rows"])

    corr_features_by_state = {}
    for state in STATES:
        print("building correction features for", state)
        corr_features_by_state[state] = build_correction_features(state, joined[state])

    per_target = {}
    csv_rows = []

    for target_name in sorted(targets.keys()):
        p043 = a043["per_target"][target_name]
        nearest = p043["nearest_candidates_first_20"][0] if p043["nearest_candidates_first_20"] else None
        exacts_043 = p043.get("exact_candidates_first_40", [])

        if target_name == "free_size":
            # Free size is structurally constant and already overexplained.
            base = {s: 0 for s in STATES}
            base_feature = "constant_free_size_already_trivial"
        elif exacts_043:
            base = exacts_043[0]["values"]
            base_feature = exacts_043[0]["feature"]
        else:
            base = nearest["values"]
            base_feature = nearest["feature"]

        base = {s: int(base[s]) for s in STATES}
        target = {s: int(targets[target_name][s]) for s in STATES}

        residual, residual_bit, exact_corr, near_corr = exact_correction_candidates(
            base, target, corr_features_by_state
        )

        exact_non_bit = [
            x for x in exact_corr
            if not x["feature"].startswith("bit__")
            and not x["feature"].startswith("onehot__")
        ]

        per_target[target_name] = {
            "target_values": target,
            "base_feature": base_feature,
            "base_values": base,
            "residual": residual,
            "residual_bit_law": residual_bit,
            "exact_correction_count": len(exact_corr),
            "exact_non_bit_correction_count_first_saved": len(exact_non_bit),
            "exact_corrections_first_40": exact_corr,
            "exact_non_bit_corrections_first_20": exact_non_bit[:20],
            "nearest_corrections_first_20": near_corr[:20],
        }

        for item in exact_corr[:40]:
            csv_rows.append([
                target_name,
                "exact",
                item["feature"],
                item["a"],
                item["c"],
                0,
                json.dumps(item["feature_values"], sort_keys=True),
                json.dumps(item["corrected_values"], sort_keys=True),
            ])

        for item in near_corr[:20]:
            csv_rows.append([
                target_name,
                "nearest",
                item["feature"],
                item["a"],
                item["c"],
                item["l1_error"],
                json.dumps(item["feature_values"], sort_keys=True),
                json.dumps(item["corrected_values"], sort_keys=True),
            ])

    nontrivial = [t for t in targets.keys() if t != "free_size"]
    nontrivial_with_exact = sum(
        1 for t in nontrivial
        if per_target[t]["exact_correction_count"] > 0
    )
    nontrivial_with_non_bit_exact = sum(
        1 for t in nontrivial
        if per_target[t]["exact_non_bit_correction_count_first_saved"] > 0
    )

    checks = {
        "free_block_scalar_032_theorem_candidate_pass": bool(a032.get("theorem_candidate_pass")),
        "relay_selector_035_theorem_candidate_pass": bool(a035.get("theorem_candidate_pass")),
        "station_extract_041_pass": bool(a041.get("extract_pass")),
        "coupled_register_043_pass": bool(a043.get("audit_pass")),
        "all_join_checks": all(all(v.values()) for v in join_checks.values()),
        "target_count": len(targets),
        "nontrivial_target_count": len(nontrivial),
        "nontrivial_targets_with_exact_correction": nontrivial_with_exact,
        "nontrivial_targets_with_non_bit_exact_correction_first_saved": nontrivial_with_non_bit_exact,
    }

    result = {
        "status": "residual_correction_law_audit_recorded",
        "audit_id": "044",
        "inputs": {
            "free_block_scalar_selector_032": str(IN_032),
            "relay_selector_035": str(IN_035),
            "station_extract_041": str(IN_041),
            "coupled_register_residual_043": str(IN_043),
        },
        "checks": checks,
        "audit_pass": all([
            checks["free_block_scalar_032_theorem_candidate_pass"],
            checks["relay_selector_035_theorem_candidate_pass"],
            checks["station_extract_041_pass"],
            checks["coupled_register_043_pass"],
            checks["all_join_checks"],
        ]),
        "per_target": per_target,
        "interpretation": (
            "Artifact 043 found one exact nontrivial coupled readout and several small structured residuals. "
            "This audit takes the best 043 base feature per target, computes the residual, and tests bounded affine corrections "
            "from state bits and station-register correction features."
        ),
        "boundary": (
            "This is a residual correction audit over the reduced four-state target. Exact correction candidates are hypotheses. "
            "They may be overfit unless they are conceptually natural and survive later candidate-universe tests. This does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target", "kind", "feature", "a", "c", "l1_error", "feature_values", "corrected_values"])
        for row in csv_rows:
            w.writerow(row)

    lines = []
    lines.append("# Residual correction law audit 044")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(result["audit_pass"]) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Target residuals")
    lines.append("")
    for target_name in sorted(per_target.keys()):
        p = per_target[target_name]
        lines.append("- " + target_name + ":")
        lines.append("  - target_values: `" + str(p["target_values"]) + "`")
        lines.append("  - base_feature: `" + str(p["base_feature"]) + "`")
        lines.append("  - base_values: `" + str(p["base_values"]) + "`")
        lines.append("  - residual: `" + str(p["residual"]) + "`")
        lines.append("  - residual_bit_law: `" + str(p["residual_bit_law"]) + "`")
        lines.append("  - exact_correction_count: `" + str(p["exact_correction_count"]) + "`")
        lines.append("  - exact_non_bit_correction_count_first_saved: `" + str(p["exact_non_bit_correction_count_first_saved"]) + "`")
        lines.append("  - exact_corrections_first_5: `" + str(p["exact_corrections_first_40"][:5]) + "`")
        lines.append("  - exact_non_bit_corrections_first_5: `" + str(p["exact_non_bit_corrections_first_20"][:5]) + "`")
        lines.append("  - nearest_corrections_first_5: `" + str(p["nearest_corrections_first_20"][:5]) + "`")
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
    print("nontrivial_targets_with_exact_correction", nontrivial_with_exact, "of", len(nontrivial))
    print("nontrivial_targets_with_non_bit_exact_correction_first_saved", nontrivial_with_non_bit_exact, "of", len(nontrivial))
    for target_name in sorted(per_target.keys()):
        p = per_target[target_name]
        print(
            target_name,
            "base", p["base_feature"],
            "residual", p["residual"],
            "exact", p["exact_correction_count"],
            "non_bit_saved", p["exact_non_bit_correction_count_first_saved"],
        )


if __name__ == "__main__":
    main()
