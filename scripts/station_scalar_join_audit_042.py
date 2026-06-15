#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]

IN_032 = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"
IN_035 = ROOT / "artifacts/json/native_g60_relay_block_selector_from_mediators_035.v1.json"
IN_041 = ROOT / "artifacts/json/imported_station_row_extract_041.v1.json"

OUT_JSON = ROOT / "artifacts/json/station_scalar_join_audit_042.v1.json"
OUT_CSV = ROOT / "artifacts/csv/station_scalar_join_audit_042.v1.csv"
OUT_NOTE = ROOT / "notes/station_scalar_join_audit_042.md"

STATES = ["O0", "O1", "B0", "B1"]

STATE_C_PATHS = {
    "O0": [11, 2, 14, 11],
    "O1": [13, 1, 10, 13],
    "B0": [2, 5, 0, 2],
    "B1": [4, 5, 2, 4],
}

NUM_FIELDS = [
    "from_A",
    "from_B",
    "from_C",
    "from_slot",
    "from_fiber",
    "to_A",
    "to_B",
    "to_C",
    "to_slot",
    "to_fiber",
    "lift_q",
    "from_fiber_mod15",
    "to_fiber_mod15",
    "C_delta_mod15",
]


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


def as_int(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, str) and v.strip().lstrip("-").isdigit():
        return int(v.strip())
    return None


def path_edges(path):
    return [(int(path[i]), int(path[i + 1])) for i in range(len(path) - 1)]


def add_stats(out, prefix, values):
    vals = [as_int(v) for v in values]
    vals = [v for v in vals if v is not None]
    if not vals:
        return
    uniq = sorted(set(vals))

    out[prefix + "_count"] = len(vals)
    out[prefix + "_sum"] = sum(vals)
    out[prefix + "_min"] = min(vals)
    out[prefix + "_max"] = max(vals)
    out[prefix + "_range"] = max(vals) - min(vals)
    out[prefix + "_sum_mod15"] = sum(vals) % 15

    out[prefix + "_unique_count"] = len(uniq)
    out[prefix + "_unique_sum"] = sum(uniq)
    out[prefix + "_unique_min"] = min(uniq)
    out[prefix + "_unique_max"] = max(uniq)
    out[prefix + "_unique_range"] = max(uniq) - min(uniq)
    out[prefix + "_unique_sum_mod15"] = sum(uniq) % 15


def add_delta_stats(out, prefix, rows, a, b, mod=15):
    int_deltas = []
    mod_deltas = []
    for r in rows:
        av = as_int(r.get(a))
        bv = as_int(r.get(b))
        if av is None or bv is None:
            continue
        int_deltas.append(bv - av)
        mod_deltas.append((bv - av) % mod)

    add_stats(out, prefix + "_int_delta", int_deltas)
    add_stats(out, prefix + "_mod_delta", mod_deltas)


def numeric_features_only(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, bool):
            continue
        if isinstance(v, int):
            out[k] = v
        elif isinstance(v, float) and v.is_integer():
            out[k] = int(v)
    return out


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


def build_features_for_rows(state, rows):
    out = {}

    b, r = bits(state)
    out["shell_bit"] = b
    out["rank_bit"] = r
    out["bit_product"] = b * r

    path = STATE_C_PATHS[state]
    transitions = path_edges(path)

    out["state_transition_count"] = len(transitions)
    out["state_c_path_sum"] = sum(path[:-1])
    out["state_c_path_min"] = min(path[:-1])
    out["state_c_path_max"] = max(path[:-1])
    out["state_c_path_range"] = max(path[:-1]) - min(path[:-1])
    out["state_c_path_sum_mod15"] = sum(path[:-1]) % 15

    groups = {
        "all": rows,
        "shared": [x for x in rows if x.get("role_class") == "shared_B"],
        "reverse": [x for x in rows if x.get("role_class") == "reverse_partner"],
    }

    for name, xs in groups.items():
        out[name + "_row_count"] = len(xs)
        out[name + "_role_pair_count"] = len(set(str(x.get("role_pair")) for x in xs))
        out[name + "_station_role_count"] = len(set(str(x.get("station_role")) for x in xs))
        out[name + "_transition_count"] = len(set((as_int(x.get("from_C")), as_int(x.get("to_C"))) for x in xs))

        q_vals = [as_int(x.get("lift_q")) for x in xs]
        out[name + "_lift_q0_count"] = sum(1 for q in q_vals if q == 0)
        out[name + "_lift_q3_count"] = sum(1 for q in q_vals if q == 3)

        for field in NUM_FIELDS:
            add_stats(out, name + "_" + field, [x.get(field) for x in xs])

        add_delta_stats(out, name + "_A", xs, "from_A", "to_A")
        add_delta_stats(out, name + "_B", xs, "from_B", "to_B")
        add_delta_stats(out, name + "_C", xs, "from_C", "to_C")
        add_delta_stats(out, name + "_slot", xs, "from_slot", "to_slot")
        add_delta_stats(out, name + "_fiber", xs, "from_fiber", "to_fiber", mod=60)

        out[name + "_same_A_count"] = sum(
            1 for x in xs
            if as_int(x.get("from_A")) is not None
            and as_int(x.get("from_A")) == as_int(x.get("to_A"))
        )
        out[name + "_same_B_count"] = sum(
            1 for x in xs
            if as_int(x.get("from_B")) is not None
            and as_int(x.get("from_B")) == as_int(x.get("to_B"))
        )
        out[name + "_same_slot_count"] = sum(
            1 for x in xs
            if as_int(x.get("from_slot")) is not None
            and as_int(x.get("from_slot")) == as_int(x.get("to_slot"))
        )

    # Coupled readouts comparing shared_B and reverse_partner rows inside the same state.
    shared = groups["shared"]
    reverse = groups["reverse"]

    for f in ["from_A", "to_A", "from_B", "to_B", "from_slot", "to_slot", "from_C", "to_C"]:
        shared_vals = [as_int(x.get(f)) for x in shared]
        reverse_vals = [as_int(x.get(f)) for x in reverse]
        shared_vals = [x for x in shared_vals if x is not None]
        reverse_vals = [x for x in reverse_vals if x is not None]
        if shared_vals and reverse_vals:
            out["shared_minus_reverse_" + f + "_sum"] = sum(shared_vals) - sum(reverse_vals)
            out["shared_plus_reverse_" + f + "_sum"] = sum(shared_vals) + sum(reverse_vals)
            out["shared_union_reverse_" + f + "_unique_sum"] = sum(sorted(set(shared_vals).union(reverse_vals)))
            out["shared_inter_reverse_" + f + "_unique_count"] = len(set(shared_vals).intersection(reverse_vals))

    return numeric_features_only(out)


def direct_bit_law(values):
    y00 = int(values["O0"])
    y01 = int(values["O1"])
    y10 = int(values["B0"])
    y11 = int(values["B1"])

    p0 = y00
    pb = y10 - y00
    pr = y01 - y00
    pbr = y11 - y10 - y01 + y00

    preds = {}
    for state in STATES:
        b, r = bits(state)
        preds[state] = p0 + pb*b + pr*r + pbr*b*r

    return {
        "formula": "p0 + pb*b + pr*r + pbr*b*r",
        "coefficients": {"p0": p0, "pb": pb, "pr": pr, "pbr": pbr},
        "predictions": preds,
        "coefficient_l1": abs(p0) + abs(pb) + abs(pr) + abs(pbr),
    }


def exact_and_near(features_by_state, target_by_state):
    common = sorted(set.intersection(*(set(features_by_state[s].keys()) for s in STATES)))
    exact = []
    near = []

    for name in common:
        vals = {s: features_by_state[s][name] for s in STATES}
        if all(vals[s] == target_by_state[s] for s in STATES):
            exact.append({"feature": name, "values": vals})
        else:
            err = sum(abs(int(vals[s]) - int(target_by_state[s])) for s in STATES)
            near.append({"feature": name, "values": vals, "l1_error": err})

    near.sort(key=lambda x: (x["l1_error"], x["feature"]))
    return exact, near[:20]


def main():
    a032 = load_json(IN_032)
    a035 = load_json(IN_035)
    a041 = load_json(IN_041)

    if not a032.get("theorem_candidate_pass"):
        raise SystemExit("032 theorem_candidate_pass is not true")
    if not a035.get("theorem_candidate_pass"):
        raise SystemExit("035 theorem_candidate_pass is not true")
    if not a041.get("extract_pass"):
        raise SystemExit("041 extract_pass is not true")

    rows = a041["canonical_rows"]
    rows_by_transition = defaultdict(list)
    for row in rows:
        key = (as_int(row.get("from_C")), as_int(row.get("to_C")))
        rows_by_transition[key].append(row)

    joined_by_state = {}
    features_by_state = {}
    state_checks = {}

    for state in STATES:
        transitions = path_edges(STATE_C_PATHS[state])
        state_rows = []
        transition_counts = {}
        for tr in transitions:
            xs = rows_by_transition.get(tr, [])
            state_rows.extend(xs)
            transition_counts[str(tr)] = len(xs)

        role_counts = Counter(str(x.get("role_class")) for x in state_rows)
        role_pair_counts = Counter(str(x.get("role_pair")) for x in state_rows)
        station_role_counts = Counter(str(x.get("station_role")) for x in state_rows)

        joined_by_state[state] = {
            "c_path": STATE_C_PATHS[state],
            "transitions": transitions,
            "row_count": len(state_rows),
            "transition_counts": transition_counts,
            "role_class_counts": dict(role_counts.most_common()),
            "role_pair_counts": dict(role_pair_counts.most_common()),
            "station_role_counts": dict(station_role_counts.most_common()),
            "rows": state_rows,
        }

        state_checks[state] = {
            "row_count_is_6": len(state_rows) == 6,
            "transition_counts_are_2_each": all(v == 2 for v in transition_counts.values()),
            "shared_count_is_3": role_counts.get("shared_B", 0) == 3,
            "reverse_count_is_3": role_counts.get("reverse_partner", 0) == 3,
            "role_pair_count_is_3": len(role_pair_counts) == 3,
        }

        features_by_state[state] = build_features_for_rows(state, state_rows)

    targets = target_values(a032, a035)

    per_target = {}
    csv_rows = []

    for target_name, target_by_state in targets.items():
        exact, near = exact_and_near(features_by_state, target_by_state)
        bit_law = direct_bit_law(target_by_state)
        per_target[target_name] = {
            "target_values": target_by_state,
            "target_bit_law": bit_law,
            "direct_exact_station_feature_count": len(exact),
            "direct_exact_station_features": exact,
            "nearest_station_features_by_l1": near,
        }

        for item in exact:
            csv_rows.append({
                "target": target_name,
                "kind": "direct_exact",
                "feature": item["feature"],
                "l1_error": 0,
                "values": item["values"],
            })

        for item in near[:10]:
            csv_rows.append({
                "target": target_name,
                "kind": "nearest",
                "feature": item["feature"],
                "l1_error": item["l1_error"],
                "values": item["values"],
            })

    all_state_join_checks = all(
        all(check.values()) for check in state_checks.values()
    )

    target_count_with_exact_station_feature = sum(
        1 for p in per_target.values()
        if p["direct_exact_station_feature_count"] > 0
    )

    station_direct_derivation_pass = target_count_with_exact_station_feature == len(per_target)

    checks = {
        "free_block_scalar_032_theorem_candidate_pass": bool(a032.get("theorem_candidate_pass")),
        "relay_selector_035_theorem_candidate_pass": bool(a035.get("theorem_candidate_pass")),
        "station_extract_041_pass": bool(a041.get("extract_pass")),
        "canonical_row_count_24": len(rows) == 24,
        "all_state_join_checks": all_state_join_checks,
        "target_count": len(per_target),
        "target_count_with_exact_station_feature": target_count_with_exact_station_feature,
        "station_direct_derivation_pass": station_direct_derivation_pass,
    }

    result = {
        "status": "station_scalar_join_audit_recorded",
        "audit_id": "042",
        "inputs": {
            "free_block_scalar_selector_032": str(IN_032),
            "relay_selector_035": str(IN_035),
            "station_extract_041": str(IN_041),
        },
        "state_c_paths": STATE_C_PATHS,
        "joined_by_state": joined_by_state,
        "state_join_checks": state_checks,
        "features_by_state": features_by_state,
        "per_target": per_target,
        "checks": checks,
        "audit_pass": all([
            checks["free_block_scalar_032_theorem_candidate_pass"],
            checks["relay_selector_035_theorem_candidate_pass"],
            checks["station_extract_041_pass"],
            checks["canonical_row_count_24"],
            checks["all_state_join_checks"],
        ]),
        "station_direct_derivation_pass": station_direct_derivation_pass,
        "interpretation": (
            "This joins each local Lift/Twist state to the canonical WXYZTI station rows using the state's C path transitions. "
            "It then tests whether the scalar targets from 032 and 035 are direct readouts of station-register summaries."
        ),
        "boundary": (
            "This is a join and feature audit. Exact station features are evidence of station-register provenance, not a full generator. "
            "Failure to find exact station features does not refute the 036 pipeline; it means the scalar laws need a richer register law or a different join."
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
            w.writerow([
                row["target"],
                row["kind"],
                row["feature"],
                row["l1_error"],
                json.dumps(row["values"], sort_keys=True),
            ])

    lines = []
    lines.append("# Station scalar join audit 042")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(result["audit_pass"]) + "`")
    lines.append("- station_direct_derivation_pass: `" + str(station_direct_derivation_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## State joins")
    lines.append("")
    for state in STATES:
        j = joined_by_state[state]
        lines.append("- " + state + ":")
        lines.append("  - c_path: `" + str(j["c_path"]) + "`")
        lines.append("  - row_count: `" + str(j["row_count"]) + "`")
        lines.append("  - transition_counts: `" + str(j["transition_counts"]) + "`")
        lines.append("  - role_class_counts: `" + str(j["role_class_counts"]) + "`")
        lines.append("  - role_pair_counts: `" + str(j["role_pair_counts"]) + "`")
        lines.append("  - station_role_counts: `" + str(j["station_role_counts"]) + "`")
        lines.append("  - checks: `" + str(state_checks[state]) + "`")
    lines.append("")
    lines.append("## Scalar targets")
    lines.append("")
    for target_name in sorted(per_target.keys()):
        p = per_target[target_name]
        lines.append("- " + target_name + ":")
        lines.append("  - target_values: `" + str(p["target_values"]) + "`")
        lines.append("  - target_bit_law: `" + str(p["target_bit_law"]) + "`")
        lines.append("  - direct_exact_station_feature_count: `" + str(p["direct_exact_station_feature_count"]) + "`")
        if p["direct_exact_station_features"]:
            lines.append("  - direct_exact_station_features_first_10: `" + str(p["direct_exact_station_features"][:10]) + "`")
        lines.append("  - nearest_station_features_by_l1_first_5: `" + str(p["nearest_station_features_by_l1"][:5]) + "`")
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
    print("station_direct_derivation_pass", station_direct_derivation_pass)
    print("target_count_with_exact_station_feature", target_count_with_exact_station_feature)
    for state in STATES:
        print(state, "row_count", joined_by_state[state]["row_count"], "checks", state_checks[state])
    for target_name in sorted(per_target.keys()):
        p = per_target[target_name]
        print(
            target_name,
            "exact_station_features", p["direct_exact_station_feature_count"],
            "nearest", p["nearest_station_features_by_l1"][:2],
        )


if __name__ == "__main__":
    main()
