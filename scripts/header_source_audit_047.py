#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_041 = ROOT / "artifacts/json/imported_station_row_extract_041.v1.json"
IN_045 = ROOT / "artifacts/json/shared_residual_correction_grammar_045.v1.json"
IN_046 = ROOT / "artifacts/json/local_scalar_provenance_checkpoint_046.v1.json"

OUT_JSON = ROOT / "artifacts/json/header_source_audit_047.v1.json"
OUT_CSV = ROOT / "artifacts/csv/header_source_audit_047.v1.csv"
OUT_NOTE = ROOT / "notes/header_source_audit_047.md"

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
TOP_N = 30


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
        "nonzero_terms": [k for k, v in coeffs.items() if v != 0],
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


def add_set_feature(features, name, vals):
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

        role_class_counts = Counter(str(r.get("role_class")) for r in rows)
        role_pair_counts = Counter(str(r.get("role_pair")) for r in rows)
        station_role_counts = Counter(str(r.get("station_role")) for r in rows)

        joined[state] = rows
        checks[state] = {
            "row_count_is_6": len(rows) == 6,
            "transition_counts_are_2_each": all(v == 2 for v in transition_counts.values()),
            "shared_count_is_3": role_class_counts.get("shared_B", 0) == 3,
            "reverse_count_is_3": role_class_counts.get("reverse_partner", 0) == 3,
            "role_pair_count_is_3": len(role_pair_counts) == 3,
            "station_role_count_is_6": len(station_role_counts) == 6,
        }

    return joined, checks


def build_station_features(state, rows):
    features = {}

    b, r = bits(state)
    c_nodes = set(STATE_C_PATHS[state][:-1])

    features["bit__const"] = 1
    features["bit__b"] = b
    features["bit__r"] = r
    features["bit__br"] = b * r

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

    seed_sets = {
        "state_cpath": c_nodes,
        "state_cpath_compl": RESIDUES - c_nodes,
    }

    for subset_name, subset_rows in subsets.items():
        features["rows__" + subset_name + "__count"] = len(subset_rows)

        for field in FIELDS:
            vals = [row_value(x, field) for x in subset_rows]
            s = add_set_feature(features, "set__" + subset_name + "__" + field, vals)
            if s:
                seed_sets[subset_name + "__" + field] = s

    for name, s in list(seed_sets.items()):
        add_set_feature(features, "op__" + name + "__minus_cpath", s - c_nodes)
        add_set_feature(features, "op__" + name + "__cpath_minus", c_nodes - s)
        add_set_feature(features, "op__" + name + "__inter_cpath", s & c_nodes)
        add_set_feature(features, "op__" + name + "__union_cpath", s | c_nodes)

    return features


def normalize_family(feature):
    suffixes = [
        "__compl_size", "__compl_sum", "__compl_min", "__compl_max", "__compl_range",
        "__size", "__sum", "__min", "__max", "__range",
    ]
    for suffix in suffixes:
        if feature.endswith(suffix):
            return feature[:-len(suffix)]
    return feature


def source_class(feature):
    if feature.startswith("bit__"):
        return "bit_header"
    if feature.startswith("rows__"):
        return "row_count"
    if feature.startswith("set__q0") or feature.startswith("op__q0"):
        return "q0_station_feature"
    if feature.startswith("set__q3") or feature.startswith("op__q3"):
        return "q3_station_feature"
    if feature.startswith("set__shared") or feature.startswith("op__shared"):
        return "shared_B_feature"
    if feature.startswith("set__reverse") or feature.startswith("op__reverse"):
        return "reverse_partner_feature"
    if "rolepair_" in feature:
        return "role_pair_feature"
    if "station_" in feature:
        return "station_role_feature"
    if "state_cpath" in feature:
        return "state_cpath_feature"
    return "other_station_feature"


def exact_and_near_station_sources(features_by_state, residual):
    common = sorted(set.intersection(*(set(features_by_state[s].keys()) for s in STATES)))

    exact = []
    near = []

    for feature in common:
        fvals = {s: int(features_by_state[s][feature]) for s in STATES}

        for a in COEFFS:
            if a == 0:
                continue

            needed = [int(residual[s]) - a * fvals[s] for s in STATES]
            if len(set(needed)) == 1 and needed[0] in OFFSETS:
                c = needed[0]
                pred = {s: a * fvals[s] + c for s in STATES}
                exact.append({
                    "feature": feature,
                    "source_class": source_class(feature),
                    "family": normalize_family(feature),
                    "a": a,
                    "c": c,
                    "feature_values": fvals,
                    "predicted_residual": pred,
                    "l1_error": 0,
                    "complexity": abs(a) + abs(c) + len(feature) / 1000.0,
                })
            else:
                counts = Counter(needed)
                c, _ = counts.most_common(1)[0]
                if c not in OFFSETS:
                    continue
                pred = {s: a * fvals[s] + c for s in STATES}
                err = sum(abs(pred[s] - int(residual[s])) for s in STATES)
                near.append({
                    "feature": feature,
                    "source_class": source_class(feature),
                    "family": normalize_family(feature),
                    "a": a,
                    "c": c,
                    "feature_values": fvals,
                    "predicted_residual": pred,
                    "l1_error": err,
                    "complexity": err * 1000 + abs(a) + abs(c) + len(feature) / 1000.0,
                })

    exact.sort(key=lambda x: (x["complexity"], len(x["feature"]), x["feature"]))
    near.sort(key=lambda x: (x["l1_error"], x["complexity"], len(x["feature"]), x["feature"]))

    return exact[:TOP_N], near[:TOP_N]


def small_header_rows(a045):
    out = []
    for row in a045["rows"]:
        if row["classification"] == "small_header_residual_remaining":
            out.append(row)
    out.sort(key=lambda x: x["target"])
    return out


def relation_search(residuals):
    # Look for very small integer relations among the three header residual maps.
    names = sorted(residuals.keys())
    found = []

    for a in range(-4, 5):
        for b in range(-4, 5):
            for c in range(-4, 5):
                coeffs = [a, b, c]
                if coeffs == [0, 0, 0]:
                    continue
                # Avoid duplicate sign variants by requiring first nonzero positive.
                first = next((x for x in coeffs if x != 0), 0)
                if first < 0:
                    continue

                vals = {}
                for state in STATES:
                    vals[state] = (
                        a * residuals[names[0]][state]
                        + b * residuals[names[1]][state]
                        + c * residuals[names[2]][state]
                    )

                if all(v == 0 for v in vals.values()):
                    found.append({
                        "kind": "zero_relation",
                        "targets": names,
                        "coefficients": {names[0]: a, names[1]: b, names[2]: c},
                        "values": vals,
                        "coeff_l1": abs(a) + abs(b) + abs(c),
                    })
                elif len(set(vals.values())) == 1:
                    found.append({
                        "kind": "constant_relation",
                        "targets": names,
                        "coefficients": {names[0]: a, names[1]: b, names[2]: c},
                        "values": vals,
                        "constant": next(iter(vals.values())),
                        "coeff_l1": abs(a) + abs(b) + abs(c),
                    })

    found.sort(key=lambda x: (x["coeff_l1"], x["kind"], str(x["coefficients"])))
    return found[:30]


def main():
    a041 = load_json(IN_041)
    a045 = load_json(IN_045)
    a046 = load_json(IN_046)

    if not a041.get("extract_pass"):
        raise SystemExit("041 extract_pass is not true")
    if not a045["checks"].get("shared_header_grammar_pass"):
        raise SystemExit("045 shared_header_grammar_pass is not true")
    if not a046.get("checkpoint_pass"):
        raise SystemExit("046 checkpoint_pass is not true")

    joined, join_checks = joined_rows(a041["canonical_rows"])

    features_by_state = {}
    feature_counts = {}
    for state in STATES:
        print("building header-source features for", state)
        features_by_state[state] = build_station_features(state, joined[state])
        feature_counts[state] = len(features_by_state[state])

    header_rows = small_header_rows(a045)
    residuals = {
        row["target"]: {s: int(row["residual"][s]) for s in STATES}
        for row in header_rows
    }

    per_header = {}
    csv_rows = []

    for row in header_rows:
        target = row["target"]
        residual = residuals[target]
        exact, near = exact_and_near_station_sources(features_by_state, residual)

        near_family_counts = Counter(x["family"] for x in near[:20])
        near_class_counts = Counter(x["source_class"] for x in near[:20])

        exact_non_bit = [x for x in exact if x["source_class"] != "bit_header"]
        near_non_bit = [x for x in near if x["source_class"] != "bit_header"]

        per_header[target] = {
            "base_feature": row["base_feature"],
            "residual": residual,
            "residual_bit_law": bit_law(residual),
            "exact_station_source_count": len(exact_non_bit),
            "exact_station_sources_first": exact_non_bit[:TOP_N],
            "nearest_station_sources_first": near_non_bit[:TOP_N],
            "nearest_family_counts_top20": dict(near_family_counts.most_common()),
            "nearest_source_class_counts_top20": dict(near_class_counts.most_common()),
            "station_source_found": len(exact_non_bit) > 0,
        }

        for item in exact_non_bit[:20]:
            csv_rows.append([
                target,
                "exact",
                item["source_class"],
                item["family"],
                item["feature"],
                item["a"],
                item["c"],
                item["l1_error"],
                json.dumps(item["feature_values"], sort_keys=True),
                json.dumps(item["predicted_residual"], sort_keys=True),
            ])

        for item in near_non_bit[:20]:
            csv_rows.append([
                target,
                "nearest",
                item["source_class"],
                item["family"],
                item["feature"],
                item["a"],
                item["c"],
                item["l1_error"],
                json.dumps(item["feature_values"], sort_keys=True),
                json.dumps(item["predicted_residual"], sort_keys=True),
            ])

    near_family_sets = []
    near_class_sets = []
    for target in sorted(per_header):
        near_family_sets.append(set(per_header[target]["nearest_family_counts_top20"].keys()))
        near_class_sets.append(set(per_header[target]["nearest_source_class_counts_top20"].keys()))

    shared_near_families = sorted(set.intersection(*near_family_sets)) if near_family_sets else []
    shared_near_classes = sorted(set.intersection(*near_class_sets)) if near_class_sets else []

    relation_candidates = relation_search(residuals)

    all_join_checks = all(all(v.values()) for v in join_checks.values())
    all_headers_small = all(
        per_header[t]["residual_bit_law"]["max_abs_coeff"] <= 3
        and per_header[t]["residual_bit_law"]["coefficient_l1"] <= 9
        for t in per_header
    )

    station_header_source_found = all(per_header[t]["station_source_found"] for t in per_header)

    checks = {
        "station_extract_041_pass": bool(a041.get("extract_pass")),
        "shared_header_045_pass": bool(a045["checks"].get("shared_header_grammar_pass")),
        "checkpoint_046_pass": bool(a046.get("checkpoint_pass")),
        "all_join_checks": all_join_checks,
        "remaining_header_target_count": len(per_header),
        "remaining_headers_are_free_sum_relay_max_relay_sum": sorted(per_header.keys()) == ["free_sum", "relay_max", "relay_sum"],
        "all_headers_small": all_headers_small,
        "station_header_source_found_for_all": station_header_source_found,
        "shared_near_station_family_exists": len(shared_near_families) > 0,
        "small_integer_relation_found": len(relation_candidates) > 0,
    }

    audit_pass = all([
        checks["station_extract_041_pass"],
        checks["shared_header_045_pass"],
        checks["checkpoint_046_pass"],
        checks["all_join_checks"],
        checks["remaining_headers_are_free_sum_relay_max_relay_sum"],
        checks["all_headers_small"],
    ])

    if station_header_source_found:
        verdict = "station_header_source_candidate_found"
    elif checks["shared_near_station_family_exists"]:
        verdict = "shared_near_station_family_but_no_exact_source"
    else:
        verdict = "header_source_remains_open_small_bit_header_only"

    result = {
        "status": "header_source_audit_recorded",
        "audit_id": "047",
        "inputs": {
            "station_extract_041": str(IN_041),
            "shared_header_grammar_045": str(IN_045),
            "local_scalar_checkpoint_046": str(IN_046),
        },
        "checks": checks,
        "audit_pass": audit_pass,
        "verdict": verdict,
        "feature_counts_by_state": feature_counts,
        "per_header": per_header,
        "shared_near_families": shared_near_families,
        "shared_near_source_classes": shared_near_classes,
        "small_integer_relation_candidates": relation_candidates,
        "interpretation": (
            "Artifact 046 records a station-register normal form with three remaining small two-bit header residuals. "
            "This audit tests whether those residuals have exact station-feature sources or a shared near station family."
        ),
        "boundary": (
            "This is a header-source audit over the reduced four-state local normal form. "
            "Failure to find an exact station source does not refute the normal form; it leaves the bounded header as an open provenance target. "
            "This does not derive the full role-labeled shared_B universe and is not Gap A closure."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "target",
            "kind",
            "source_class",
            "family",
            "feature",
            "a",
            "c",
            "l1_error",
            "feature_values",
            "predicted_residual",
        ])
        for row in csv_rows:
            w.writerow(row)

    lines = []
    lines.append("# Header source audit 047")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(audit_pass) + "`")
    lines.append("- verdict: `" + verdict + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Header targets")
    lines.append("")
    for target in sorted(per_header):
        p = per_header[target]
        lines.append("- " + target + ":")
        lines.append("  - base_feature: `" + p["base_feature"] + "`")
        lines.append("  - residual: `" + str(p["residual"]) + "`")
        lines.append("  - residual_bit_law: `" + str(p["residual_bit_law"]) + "`")
        lines.append("  - exact_station_source_count: `" + str(p["exact_station_source_count"]) + "`")
        lines.append("  - station_source_found: `" + str(p["station_source_found"]) + "`")
        lines.append("  - nearest_source_class_counts_top20: `" + str(p["nearest_source_class_counts_top20"]) + "`")
        lines.append("  - exact_station_sources_first_5: `" + str(p["exact_station_sources_first"][:5]) + "`")
        lines.append("  - nearest_station_sources_first_5: `" + str(p["nearest_station_sources_first"][:5]) + "`")
    lines.append("")
    lines.append("## Shared near families")
    lines.append("")
    lines.append("- shared_near_source_classes: `" + str(shared_near_classes) + "`")
    lines.append("- shared_near_families: `" + str(shared_near_families) + "`")
    lines.append("")
    lines.append("## Small integer relations among header residuals")
    lines.append("")
    lines.append("`" + str(relation_candidates[:10]) + "`")
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
    print("audit_pass", audit_pass)
    print("verdict", verdict)
    for k, v in checks.items():
        print(k, v)
    for target in sorted(per_header):
        p = per_header[target]
        print(
            target,
            "exact_station_sources", p["exact_station_source_count"],
            "nearest", p["nearest_station_sources_first"][:2],
        )
    print("shared_near_source_classes", shared_near_classes)
    print("shared_near_families", shared_near_families[:10])
    print("small_integer_relation_count", len(relation_candidates))


if __name__ == "__main__":
    main()
