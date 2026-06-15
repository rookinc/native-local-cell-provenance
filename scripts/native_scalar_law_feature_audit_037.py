#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_032 = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"
IN_035 = ROOT / "artifacts/json/native_g60_relay_block_selector_from_mediators_035.v1.json"
IN_036 = ROOT / "artifacts/json/local_anchor_payload_pipeline_036.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_scalar_law_feature_audit_037.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_scalar_law_feature_audit_037.v1.csv"
OUT_NOTE = ROOT / "notes/native_scalar_law_feature_audit_037.md"

STATES = ["O0", "O1", "B0", "B1"]
RESIDUES = list(range(15))


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


def cyclic_dist(a, b, mod=15):
    d = abs(int(a) - int(b)) % mod
    return min(d, mod - d)


def safe_min(xs):
    return min(xs) if xs else None


def safe_max(xs):
    return max(xs) if xs else None


def safe_sum(xs):
    return sum(xs) if xs else 0


def add_stats(prefix, xs, out):
    xs = sorted(int(x) for x in xs)
    out[prefix + "_size"] = len(xs)
    out[prefix + "_sum"] = safe_sum(xs)
    out[prefix + "_min"] = safe_min(xs)
    out[prefix + "_max"] = safe_max(xs)
    out[prefix + "_range"] = (safe_max(xs) - safe_min(xs)) if xs else None
    out[prefix + "_sum_mod15"] = safe_sum(xs) % 15
    return out


def numeric_only(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, bool):
            continue
        if isinstance(v, int):
            out[k] = v
        elif isinstance(v, float) and v.is_integer():
            out[k] = int(v)
    return out


def direct_bit_law(values):
    y_o0 = int(values["O0"])
    y_o1 = int(values["O1"])
    y_b0 = int(values["B0"])
    y_b1 = int(values["B1"])

    p0 = y_o0
    pb = y_b0 - y_o0
    pr = y_o1 - y_o0
    pbr = y_b1 - y_b0 - y_o1 + y_o0

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


def law_eval(law, state):
    b, r = bits(state)
    c = law["coefficients"]
    return int(c["p0"]) + int(c["pb"])*b + int(c["pr"])*r + int(c["pbr"])*b*r


def build_native_features(a035, state):
    p = a035["per_state"][state]

    u = sorted(int(x) for x in p["mediator_union"])
    c = sorted(int(x) for x in p["c_values"])
    cset = set(c)
    uset = set(u)

    u_inter_c = sorted(uset.intersection(cset))
    u_minus_c = sorted(uset.difference(cset))
    missing = sorted(set(RESIDUES).difference(uset))
    missing_minus_c = sorted(set(missing).difference(cset))
    u_union_c = sorted(uset.union(cset))

    out = {}
    b, r = bits(state)
    out["shell_bit"] = b
    out["rank_bit"] = r
    out["bit_product"] = b * r

    add_stats("mediator_union", u, out)
    add_stats("c_values", c, out)
    add_stats("u_inter_c", u_inter_c, out)
    add_stats("u_minus_c", u_minus_c, out)
    add_stats("missing_from_u", missing, out)
    add_stats("missing_from_u_minus_c", missing_minus_c, out)
    add_stats("u_union_c", u_union_c, out)

    rows = p.get("mediator_rows", [])
    row_sizes = []
    row_sums = []
    row_mins = []
    row_maxs = []
    row_hit_c_counts = []

    for row in rows:
        vals = sorted(int(x) for x in row.get("mediators", []))
        if vals:
            row_sizes.append(len(vals))
            row_sums.append(sum(vals))
            row_mins.append(min(vals))
            row_maxs.append(max(vals))
            row_hit_c_counts.append(len(set(vals).intersection(cset)))

    out["mediator_row_count"] = len(rows)
    add_stats("mediator_row_sizes", row_sizes, out)
    add_stats("mediator_row_sums", row_sums, out)
    add_stats("mediator_row_mins", row_mins, out)
    add_stats("mediator_row_maxs", row_maxs, out)
    add_stats("mediator_row_hit_c_counts", row_hit_c_counts, out)

    nearest_c_dists = []
    for x in u:
        if c:
            nearest_c_dists.append(min(cyclic_dist(x, y) for y in c))
    add_stats("mediator_nearest_c_dist", nearest_c_dists, out)

    nearest_u_dists_from_c = []
    for x in c:
        if u:
            nearest_u_dists_from_c.append(min(cyclic_dist(x, y) for y in u))
    add_stats("c_nearest_mediator_dist", nearest_u_dists_from_c, out)

    return numeric_only(out)


def target_values(a032, a035):
    values = {
        "relay_size": {},
        "relay_sum": {},
        "relay_min": {},
        "relay_max": {},
        "free_size": {},
        "free_sum": {},
        "free_min": {},
    }

    for state in STATES:
        s035 = a035["per_state"][state]
        s032 = a032["per_state"][state]

        values["relay_size"][state] = int(s035["size_target"])
        values["relay_sum"][state] = int(s035["sum_target"])
        values["relay_min"][state] = int(s035["min_target"])
        values["relay_max"][state] = int(s035["max_target"])

        values["free_size"][state] = int(s032["free_size"])
        values["free_sum"][state] = int(s032["sum_free_target"])
        values["free_min"][state] = int(s032["min_free_target"])

    return values


def find_exact_native_features(features_by_state, target_by_state):
    names = sorted(set.intersection(*(set(features_by_state[s].keys()) for s in STATES)))
    exact = []
    near = []

    for name in names:
        vals = {s: features_by_state[s][name] for s in STATES}
        if all(vals[s] == target_by_state[s] for s in STATES):
            exact.append({"feature": name, "values": vals})
        else:
            err = sum(abs(int(vals[s]) - int(target_by_state[s])) for s in STATES)
            near.append({"feature": name, "values": vals, "l1_error": err})

    near.sort(key=lambda x: (x["l1_error"], x["feature"]))
    return exact, near[:10]


def residual_laws(features_by_state, target_by_state):
    names = sorted(set.intersection(*(set(features_by_state[s].keys()) for s in STATES)))
    rows = []

    for name in names:
        vals = {s: features_by_state[s][name] for s in STATES}
        residual = {s: int(target_by_state[s]) - int(vals[s]) for s in STATES}
        law = direct_bit_law(residual)
        rows.append({
            "feature": name,
            "feature_values": vals,
            "residual_values": residual,
            "residual_law": law,
        })

    rows.sort(key=lambda x: (x["residual_law"]["coefficient_l1"], x["feature"]))
    return rows[:10]


def main():
    a032 = load_json(IN_032)
    a035 = load_json(IN_035)
    a036 = load_json(IN_036)

    if not a032.get("theorem_candidate_pass"):
        raise SystemExit("032 theorem_candidate_pass is not true")
    if not a035.get("theorem_candidate_pass"):
        raise SystemExit("035 theorem_candidate_pass is not true")
    if not a036.get("theorem_candidate_pass"):
        raise SystemExit("036 theorem_candidate_pass is not true")

    features_by_state = {s: build_native_features(a035, s) for s in STATES}
    targets = target_values(a032, a035)

    per_target = {}
    csv_rows = []

    for target_name, tv in targets.items():
        exact, near = find_exact_native_features(features_by_state, tv)
        residuals = residual_laws(features_by_state, tv)
        bit_law = direct_bit_law(tv)

        per_target[target_name] = {
            "target_values": tv,
            "target_bit_law": bit_law,
            "direct_exact_native_feature_count": len(exact),
            "direct_exact_native_features": exact,
            "nearest_native_features_by_l1": near,
            "best_native_feature_plus_bit_residuals": residuals,
        }

        for item in exact:
            csv_rows.append({
                "target": target_name,
                "kind": "direct_exact",
                "feature": item["feature"],
                "l1_error": 0,
                "values": item["values"],
            })

        for item in near:
            csv_rows.append({
                "target": target_name,
                "kind": "nearest",
                "feature": item["feature"],
                "l1_error": item["l1_error"],
                "values": item["values"],
            })

    checks = {
        "free_block_scalar_032_theorem_candidate_pass": bool(a032.get("theorem_candidate_pass")),
        "relay_selector_035_theorem_candidate_pass": bool(a035.get("theorem_candidate_pass")),
        "anchor_payload_pipeline_036_theorem_candidate_pass": bool(a036.get("theorem_candidate_pass")),
        "mediator_source_is_artifact_007_parsed": a035.get("mediator_source") == "artifact_007_parsed",
        "all_targets_have_bit_laws": all(
            per_target[t]["target_bit_law"]["predictions"] == per_target[t]["target_values"]
            for t in per_target
        ),
    }

    native_direct_derivation_pass = all(
        per_target[t]["direct_exact_native_feature_count"] > 0
        for t in per_target
    )

    result = {
        "status": "native_scalar_law_feature_audit_recorded",
        "audit_id": "037",
        "inputs": {
            "free_block_scalar_selector_032": str(IN_032),
            "relay_selector_035": str(IN_035),
            "anchor_payload_pipeline_036": str(IN_036),
        },
        "question": (
            "Are the scalar targets used by 032 and 035 directly visible as native mediator/C-geometry features, "
            "or do they remain compact state-bit selector laws?"
        ),
        "features_by_state": features_by_state,
        "per_target": per_target,
        "checks": checks,
        "audit_pass": all(checks.values()),
        "native_direct_derivation_pass": native_direct_derivation_pass,
        "interpretation": (
            "This audit separates two claims. The scalar targets all have compact state-bit laws, already used by 032 and 035. "
            "A stronger native derivation would require the targets to appear directly as mediator/C-geometry features, or to be "
            "explained by a non-circular provenance law."
        ),
        "boundary": (
            "This is a feature audit only. Direct feature matches are evidence, not proof of native meaning. Failure to find direct "
            "matches does not refute the pipeline; it means scalar provenance remains open and may require station/provenance fields."
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
    lines.append("# Native scalar law feature audit 037")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(result["audit_pass"]) + "`")
    lines.append("- native_direct_derivation_pass: `" + str(native_direct_derivation_pass) + "`")
    lines.append("")
    lines.append("## Per scalar target")
    lines.append("")
    for target_name in sorted(per_target.keys()):
        p = per_target[target_name]
        lines.append("- " + target_name + ":")
        lines.append("  - target_values: `" + str(p["target_values"]) + "`")
        lines.append("  - target_bit_law: `" + str(p["target_bit_law"]) + "`")
        lines.append("  - direct_exact_native_feature_count: `" + str(p["direct_exact_native_feature_count"]) + "`")
        if p["direct_exact_native_features"]:
            lines.append("  - direct_exact_native_features_first_10: `" + str(p["direct_exact_native_features"][:10]) + "`")
        lines.append("  - nearest_native_features_by_l1_first_5: `" + str(p["nearest_native_features_by_l1"][:5]) + "`")
        lines.append("  - best_native_feature_plus_bit_residuals_first_3: `" + str(p["best_native_feature_plus_bit_residuals"][:3]) + "`")
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
    print("audit_pass", result["audit_pass"])
    print("native_direct_derivation_pass", native_direct_derivation_pass)
    for target_name in sorted(per_target.keys()):
        p = per_target[target_name]
        print(
            target_name,
            "exact_native_features", p["direct_exact_native_feature_count"],
            "nearest", p["nearest_native_features_by_l1"][:2],
        )


if __name__ == "__main__":
    main()
