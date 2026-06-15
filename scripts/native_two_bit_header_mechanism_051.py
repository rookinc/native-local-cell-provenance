#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_045 = ROOT / "artifacts/json/shared_residual_correction_grammar_045.v1.json"
IN_050 = ROOT / "artifacts/json/header_frontier_after_upstream_locator_050.v1.json"

OUT_JSON = ROOT / "artifacts/json/native_two_bit_header_mechanism_051.v1.json"
OUT_CSV = ROOT / "artifacts/csv/native_two_bit_header_mechanism_051.v1.csv"
OUT_NOTE = ROOT / "notes/native_two_bit_header_mechanism_051.md"

STATES = ["O0", "O1", "B0", "B1"]

STATE_BITS = {
    "O0": {"b": 0, "r": 0},
    "O1": {"b": 0, "r": 1},
    "B0": {"b": 1, "r": 0},
    "B1": {"b": 1, "r": 1},
}

TARGETS = ["free_sum", "relay_max", "relay_sum"]

REQUIRED_PHRASES = [
    "two-bit coordinate mechanism",
    "C-row phase",
    "branch-only hinge",
    "rank release plus branch relief",
    "not native closure",
    "not Gap A closure",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "full shared_B universe derived",
    "header source fully derived",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_header_targets(a045):
    rows = {}
    for row in a045["rows"]:
        if row.get("classification") == "small_header_residual_remaining":
            target = row["target"]
            rows[target] = {
                "base_feature": row["base_feature"],
                "residual": {s: int(row["residual"][s]) for s in STATES},
                "residual_bit_law": row["residual_bit_law"],
            }
    return rows


def local_coordinates(b, r):
    # Project 22 / Lift-Twist local answer-cell coordinate law.
    # This is the reduced coordinate skeleton, not a full native source proof.
    c_row = 2 * b + r
    anchor_col = 1 + r + b * (2 * r - 1)
    selected_candidate_index = 4 * c_row + anchor_col
    c_key = (11 + 6 * b + 2 * r) % 15
    anchor_key = (4 * b + 12 * r + 12 * b * r) % 15
    return {
        "c_row": c_row,
        "anchor_col": anchor_col,
        "selected_candidate_index": selected_candidate_index,
        "c_key": c_key,
        "anchor_key": anchor_key,
    }


def predict_headers(b, r):
    coords = local_coordinates(b, r)
    c_row = coords["c_row"]

    # Mechanism candidate:
    #
    # 1. free_sum is a four-phase C-row clock, shifted by two.
    # 2. relay_max is zero in the ordinary shell and a branch-only hinge in the branch shell.
    # 3. relay_sum is ordinary rank release plus branch relief.
    return {
        "free_sum": (c_row + 2) % 4,
        "relay_max": b * (3 * r - 2),
        "relay_sum": -3 + 3 * r + b * (2 - r),
    }


def bit_coefficients(vals):
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
        b = STATE_BITS[state]["b"]
        r = STATE_BITS[state]["r"]
        preds[state] = coeffs["p0"] + coeffs["pb"] * b + coeffs["pr"] * r + coeffs["pbr"] * b * r

    return {
        "coefficients": coeffs,
        "predictions": preds,
        "coefficient_l1": sum(abs(v) for v in coeffs.values()),
        "max_abs_coeff": max(abs(v) for v in coeffs.values()),
        "nonzero_terms": [k for k, v in coeffs.items() if v != 0],
    }


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a045 = load_json(IN_045)
    a050 = load_json(IN_050)

    if not a045["checks"].get("shared_header_grammar_pass"):
        raise SystemExit("045 shared_header_grammar_pass is not true")
    if not a050.get("frontier_pass"):
        raise SystemExit("050 frontier_pass is not true")

    header_targets = get_header_targets(a045)

    rows = []
    predicted_by_target = {t: {} for t in TARGETS}
    observed_by_target = {t: header_targets[t]["residual"] for t in TARGETS}

    for state in STATES:
        b = STATE_BITS[state]["b"]
        r = STATE_BITS[state]["r"]
        coords = local_coordinates(b, r)
        pred = predict_headers(b, r)

        for target in TARGETS:
            predicted_by_target[target][state] = pred[target]

        rows.append({
            "state": state,
            "b": b,
            "r": r,
            **coords,
            "observed_free_sum": observed_by_target["free_sum"][state],
            "predicted_free_sum": pred["free_sum"],
            "observed_relay_max": observed_by_target["relay_max"][state],
            "predicted_relay_max": pred["relay_max"],
            "observed_relay_sum": observed_by_target["relay_sum"][state],
            "predicted_relay_sum": pred["relay_sum"],
            "all_match": all(pred[t] == observed_by_target[t][state] for t in TARGETS),
        })

    target_results = {}
    for target in TARGETS:
        obs = observed_by_target[target]
        pred = predicted_by_target[target]
        target_results[target] = {
            "base_feature": header_targets[target]["base_feature"],
            "observed_residual": obs,
            "predicted_residual": pred,
            "exact_match": obs == pred,
            "observed_bit_coefficients": bit_coefficients(obs),
            "predicted_bit_coefficients": bit_coefficients(pred),
        }

    mechanism_claims = [
        {
            "target": "free_sum",
            "claim": "free_sum header is the C-row phase shifted by two",
            "formula": "H_free_sum = (c_row + 2) mod 4",
            "interpretation": "The free-sum residual is not an arbitrary four-state table; it is the four-step C-row clock read from the opposite half-cycle.",
        },
        {
            "target": "relay_max",
            "claim": "relay_max header is a branch-only hinge",
            "formula": "H_relay_max = b * (3*r - 2)",
            "interpretation": "The relay-max residual vanishes in the ordinary shell and appears only when the branch shell is active.",
        },
        {
            "target": "relay_sum",
            "claim": "relay_sum header is rank release plus branch relief",
            "formula": "H_relay_sum = -3 + 3*r + b*(2-r)",
            "interpretation": "The relay-sum residual has an ordinary rank release from -3 to 0, then branch relief shifts B0 and B1 differently.",
        },
    ]

    closed_statement = (
        "Within the reduced four-state Lift/Twist local-cell coordinate system, the remaining bounded header is exactly recovered by a two-bit coordinate mechanism: "
        "free_sum is a C-row phase shift, relay_max is a branch-only hinge, and relay_sum is rank release plus branch relief."
    )

    boundary = (
        "This is a coordinate-mechanism derivation candidate, not native closure. It derives the remaining header from the reduced two-bit local-cell coordinates, "
        "but it does not derive those coordinates from the full native G60/shared_B universe and is not Gap A closure."
    )

    combined = closed_statement + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "shared_header_045_pass": bool(a045["checks"].get("shared_header_grammar_pass")),
        "frontier_050_pass": bool(a050.get("frontier_pass")),
        "target_set_is_free_sum_relay_max_relay_sum": sorted(header_targets.keys()) == TARGETS,
        "all_state_rows_match": all(row["all_match"] for row in rows),
        "all_target_formulas_match": all(target_results[t]["exact_match"] for t in TARGETS),
        "free_sum_is_c_row_phase_shift": target_results["free_sum"]["exact_match"],
        "relay_max_is_branch_only_hinge": target_results["relay_max"]["exact_match"],
        "relay_sum_is_rank_release_plus_branch_relief": target_results["relay_sum"]["exact_match"],
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    theorem_candidate_pass = all(checks.values())

    result = {
        "status": "native_two_bit_header_mechanism_recorded",
        "audit_id": "051",
        "inputs": {
            "shared_header_grammar_045": str(IN_045),
            "header_frontier_after_upstream_locator_050": str(IN_050),
        },
        "checks": checks,
        "theorem_candidate_pass": theorem_candidate_pass,
        "state_rows": rows,
        "target_results": target_results,
        "mechanism_claims": mechanism_claims,
        "closed_statement": closed_statement,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifacts 047 and 049 failed to source the bounded header as a station or imported-upstream feature. "
            "Artifact 051 turns the direction around: it treats the header as a reduced local-cell coordinate mechanism and verifies exact recovery from b, r, and c_row."
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
            "b",
            "r",
            "c_row",
            "anchor_col",
            "selected_candidate_index",
            "c_key",
            "anchor_key",
            "target",
            "observed",
            "predicted",
            "match",
        ])
        for row in rows:
            for target in TARGETS:
                w.writerow([
                    row["state"],
                    row["b"],
                    row["r"],
                    row["c_row"],
                    row["anchor_col"],
                    row["selected_candidate_index"],
                    row["c_key"],
                    row["anchor_key"],
                    target,
                    row["observed_" + target],
                    row["predicted_" + target],
                    row["observed_" + target] == row["predicted_" + target],
                ])

    lines = []
    lines.append("# Native two-bit header mechanism 051")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_candidate_pass: `" + str(theorem_candidate_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Closed statement")
    lines.append("")
    lines.append(closed_statement)
    lines.append("")
    lines.append("## Mechanism")
    lines.append("")
    for claim in mechanism_claims:
        lines.append("- " + claim["target"] + ":")
        lines.append("  - claim: " + claim["claim"])
        lines.append("  - formula: `" + claim["formula"] + "`")
        lines.append("  - interpretation: " + claim["interpretation"])
    lines.append("")
    lines.append("## State table")
    lines.append("")
    for row in rows:
        lines.append(
            "- {state}: b={b}, r={r}, c_row={c_row}, anchor_col={anchor_col}, selected={selected_candidate_index}, "
            "headers=({free_sum},{relay_max},{relay_sum}), match={match}".format(
                state=row["state"],
                b=row["b"],
                r=row["r"],
                c_row=row["c_row"],
                anchor_col=row["anchor_col"],
                selected_candidate_index=row["selected_candidate_index"],
                free_sum=row["predicted_free_sum"],
                relay_max=row["predicted_relay_max"],
                relay_sum=row["predicted_relay_sum"],
                match=row["all_match"],
            )
        )
    lines.append("")
    lines.append("## Target results")
    lines.append("")
    for target in TARGETS:
        tr = target_results[target]
        lines.append("- " + target + ":")
        lines.append("  - observed_residual: `" + str(tr["observed_residual"]) + "`")
        lines.append("  - predicted_residual: `" + str(tr["predicted_residual"]) + "`")
        lines.append("  - exact_match: `" + str(tr["exact_match"]) + "`")
        lines.append("  - predicted_bit_coefficients: `" + str(tr["predicted_bit_coefficients"]) + "`")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(result["interpretation"])
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(boundary)
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("theorem_candidate_pass", theorem_candidate_pass)
    for k, v in checks.items():
        print(k, v)
    for row in rows:
        print(
            row["state"],
            "b", row["b"],
            "r", row["r"],
            "c_row", row["c_row"],
            "anchor_col", row["anchor_col"],
            "headers",
            [row["predicted_" + t] for t in TARGETS],
            "match", row["all_match"],
        )


if __name__ == "__main__":
    main()
