#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_044 = ROOT / "artifacts/json/residual_correction_law_audit_044.v1.json"

OUT_JSON = ROOT / "artifacts/json/shared_residual_correction_grammar_045.v1.json"
OUT_CSV = ROOT / "artifacts/csv/shared_residual_correction_grammar_045.v1.csv"
OUT_NOTE = ROOT / "notes/shared_residual_correction_grammar_045.md"

STATES = ["O0", "O1", "B0", "B1"]
NONTRIVIAL_TARGETS = [
    "free_min",
    "free_sum",
    "relay_max",
    "relay_min",
    "relay_size",
    "relay_sum",
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
        preds[state] = (
            coeffs["p0"]
            + coeffs["pb"] * b
            + coeffs["pr"] * r
            + coeffs["pbr"] * b * r
        )

    return {
        "formula": "p0 + pb*b + pr*r + pbr*b*r",
        "coefficients": coeffs,
        "predictions": preds,
        "coefficient_l1": sum(abs(v) for v in coeffs.values()),
        "max_abs_coeff": max(abs(v) for v in coeffs.values()),
        "nonzero_terms": [k for k, v in coeffs.items() if v != 0],
    }


def is_zero(vals):
    return all(int(vals[s]) == 0 for s in STATES)


def classify_target(row):
    if is_zero(row["residual"]):
        return "station_base_exact_zero_residual"
    if row["exact_non_bit_correction_count_first_saved"] > 0:
        return "exact_station_register_correction"
    if row["residual_bit_law"]["max_abs_coeff"] <= 3 and row["residual_bit_law"]["coefficient_l1"] <= 9:
        return "small_header_residual_remaining"
    return "large_or_unclassified_residual"


def main():
    a044 = load_json(IN_044)

    if not a044.get("audit_pass"):
        raise SystemExit("044 audit_pass is not true")

    per = a044["per_target"]

    rows = []
    classes = {}

    for target in NONTRIVIAL_TARGETS:
        p = per[target]

        target_values = {s: int(p["target_values"][s]) for s in STATES}
        base_values = {s: int(p["base_values"][s]) for s in STATES}
        residual = {s: int(p["residual"][s]) for s in STATES}

        target_law = bit_law(target_values)
        base_law = bit_law(base_values)
        residual_law = bit_law(residual)

        exact_count = int(p["exact_correction_count"])
        exact_non_bit_count = int(p["exact_non_bit_correction_count_first_saved"])

        row = {
            "target": target,
            "target_values": target_values,
            "base_feature": p["base_feature"],
            "base_values": base_values,
            "residual": residual,
            "target_bit_law": target_law,
            "base_bit_law": base_law,
            "residual_bit_law": residual_law,
            "exact_correction_count": exact_count,
            "exact_non_bit_correction_count_first_saved": exact_non_bit_count,
            "target_coeff_l1": target_law["coefficient_l1"],
            "base_coeff_l1": base_law["coefficient_l1"],
            "residual_coeff_l1": residual_law["coefficient_l1"],
            "residual_max_abs_coeff": residual_law["max_abs_coeff"],
            "residual_l1_reduction_from_target": target_law["coefficient_l1"] - residual_law["coefficient_l1"],
            "residual_is_zero": is_zero(residual),
            "residual_is_small_header": residual_law["max_abs_coeff"] <= 3 and residual_law["coefficient_l1"] <= 9,
        }

        row["classification"] = classify_target(row)
        rows.append(row)
        classes.setdefault(row["classification"], []).append(target)

    corrected_or_zero = [
        r for r in rows
        if r["classification"] in [
            "station_base_exact_zero_residual",
            "exact_station_register_correction",
        ]
    ]

    remaining_small_header = [
        r for r in rows
        if r["classification"] == "small_header_residual_remaining"
    ]

    all_residuals_small = all(r["residual_is_small_header"] for r in rows)
    all_residuals_compress_target = all(
        r["residual_coeff_l1"] <= r["target_coeff_l1"]
        for r in rows
    )

    checks = {
        "input_044_audit_pass": True,
        "nontrivial_target_count": len(rows),
        "corrected_or_zero_count": len(corrected_or_zero),
        "remaining_small_header_count": len(remaining_small_header),
        "all_residuals_small_header": all_residuals_small,
        "all_residuals_compress_target_bit_law": all_residuals_compress_target,
        "max_residual_coeff_l1": max(r["residual_coeff_l1"] for r in rows),
        "max_residual_abs_coeff": max(r["residual_max_abs_coeff"] for r in rows),
        "shared_header_grammar_pass": all_residuals_small and all_residuals_compress_target,
    }

    result = {
        "status": "shared_residual_correction_grammar_recorded",
        "audit_id": "045",
        "input": str(IN_044),
        "checks": checks,
        "classification_counts": {k: len(v) for k, v in classes.items()},
        "classification_targets": classes,
        "rows": rows,
        "grammar_candidate": {
            "name": "bounded two-bit residual header",
            "basis": ["1", "b", "r", "b*r"],
            "law": "residual = p0 + pb*b + pr*r + pbr*b*r",
            "bound": "max_abs_coeff <= 3 and coefficient_l1 <= 9",
            "interpretation": (
                "After station-register base readouts and exact station corrections, every nontrivial scalar residual "
                "is a small two-bit header correction over branch bit b and rank bit r."
            ),
        },
        "interpretation": (
            "Artifact 044 improved the exact scalar correction frontier to 3 of 6 nontrivial targets. "
            "This audit does not search for new station features. It checks whether the remaining residuals share a small "
            "two-bit header grammar. The result records a constrained grammar candidate rather than a full native derivation."
        ),
        "boundary": (
            "This proves only a reduced four-state residual compression property. Since any four values can be interpolated "
            "by a two-bit polynomial, the load-bearing claim is the small coefficient bound and the station-register complexity reduction. "
            "This does not derive the full role-labeled shared_B universe and does not close Gap A."
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
            "classification",
            "base_feature",
            "target_coeff_l1",
            "base_coeff_l1",
            "residual_coeff_l1",
            "residual_max_abs_coeff",
            "residual",
            "residual_coefficients",
        ])
        for r in rows:
            w.writerow([
                r["target"],
                r["classification"],
                r["base_feature"],
                r["target_coeff_l1"],
                r["base_coeff_l1"],
                r["residual_coeff_l1"],
                r["residual_max_abs_coeff"],
                json.dumps(r["residual"], sort_keys=True),
                json.dumps(r["residual_bit_law"]["coefficients"], sort_keys=True),
            ])

    lines = []
    lines.append("# Shared residual correction grammar 045")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Classification")
    lines.append("")
    for k, v in classes.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Grammar candidate")
    lines.append("")
    lines.append("- name: `" + result["grammar_candidate"]["name"] + "`")
    lines.append("- basis: `" + str(result["grammar_candidate"]["basis"]) + "`")
    lines.append("- law: `" + result["grammar_candidate"]["law"] + "`")
    lines.append("- bound: `" + result["grammar_candidate"]["bound"] + "`")
    lines.append("")
    lines.append("## Target rows")
    lines.append("")
    for r in rows:
        lines.append("- " + r["target"] + ":")
        lines.append("  - classification: `" + r["classification"] + "`")
        lines.append("  - base_feature: `" + r["base_feature"] + "`")
        lines.append("  - target_values: `" + str(r["target_values"]) + "`")
        lines.append("  - base_values: `" + str(r["base_values"]) + "`")
        lines.append("  - residual: `" + str(r["residual"]) + "`")
        lines.append("  - target_coeff_l1: `" + str(r["target_coeff_l1"]) + "`")
        lines.append("  - residual_coeff_l1: `" + str(r["residual_coeff_l1"]) + "`")
        lines.append("  - residual_bit_law: `" + str(r["residual_bit_law"]) + "`")
        lines.append("  - exact_non_bit_correction_count_first_saved: `" + str(r["exact_non_bit_correction_count_first_saved"]) + "`")
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
    for k, v in checks.items():
        print(k, v)
    for r in rows:
        print(
            r["target"],
            r["classification"],
            "target_l1", r["target_coeff_l1"],
            "residual_l1", r["residual_coeff_l1"],
            "residual", r["residual_bit_law"]["coefficients"],
        )


if __name__ == "__main__":
    main()
