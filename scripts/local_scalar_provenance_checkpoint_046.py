#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_041 = ROOT / "artifacts/json/imported_station_row_extract_041.v1.json"
IN_042 = ROOT / "artifacts/json/station_scalar_join_audit_042.v1.json"
IN_043 = ROOT / "artifacts/json/coupled_register_residual_audit_043.v1.json"
IN_044 = ROOT / "artifacts/json/residual_correction_law_audit_044.v1.json"
IN_045 = ROOT / "artifacts/json/shared_residual_correction_grammar_045.v1.json"

OUT_JSON = ROOT / "artifacts/json/local_scalar_provenance_checkpoint_046.v1.json"
OUT_CSV = ROOT / "artifacts/csv/local_scalar_provenance_checkpoint_046.v1.csv"
OUT_NOTE = ROOT / "notes/local_scalar_provenance_checkpoint_046.md"

TARGET_ORDER = [
    "free_min",
    "free_sum",
    "relay_max",
    "relay_min",
    "relay_size",
    "relay_sum",
]

REQUIRED_CLOSED_PHRASES = [
    "canonical 24-row station register",
    "clean state-to-station join",
    "station-register base readout",
    "bounded two-bit residual header",
]

REQUIRED_BOUNDARY_PHRASES = [
    "reduced four-state",
    "does not derive the full role-labeled shared_B universe",
    "not Gap A closure",
    "not native closure",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "full Gap A closure",
    "native derivation is complete",
    "full shared_B universe derived",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def assert_true(name, value):
    if not value:
        raise SystemExit(name + " is not true")


def canonical_row_count(a041):
    return (
        a041.get("canonical_station_row_count")
        or a041.get("canonical_counts", {}).get("row_count")
        or len(a041.get("canonical_rows", []))
    )


def canonical_transition_count(a041):
    return (
        a041.get("canonical_transition_count")
        or a041.get("canonical_counts", {}).get("transition_count")
    )


def canonical_station_role_counts(a041):
    return (
        a041.get("canonical_station_role_counts")
        or a041.get("canonical_counts", {}).get("station_role_counts")
    )


def canonical_role_class_counts(a041):
    return (
        a041.get("canonical_role_class_counts")
        or a041.get("canonical_counts", {}).get("role_class_counts")
    )


def canonical_fiber_mod15_matches_C(a041):
    return a041.get("canonical_fiber_mod15_matches_C")


def get_041_summary(a041):
    return {
        "extract_pass": bool(a041.get("extract_pass")),
        "canonical_station_row_count": canonical_row_count(a041),
        "canonical_transition_count": canonical_transition_count(a041),
        "canonical_station_role_counts": canonical_station_role_counts(a041),
        "canonical_role_class_counts": canonical_role_class_counts(a041),
        "canonical_fiber_mod15_matches_C": canonical_fiber_mod15_matches_C(a041),
    }


def target_rows_from_045(a045):
    rows = []
    for r in a045["rows"]:
        if r["target"] not in TARGET_ORDER:
            continue
        rows.append({
            "target": r["target"],
            "classification": r["classification"],
            "base_feature": r["base_feature"],
            "target_values": r["target_values"],
            "base_values": r["base_values"],
            "residual": r["residual"],
            "target_coeff_l1": r["target_coeff_l1"],
            "base_coeff_l1": r["base_coeff_l1"],
            "residual_coeff_l1": r["residual_coeff_l1"],
            "residual_max_abs_coeff": r["residual_max_abs_coeff"],
            "residual_bit_law": r["residual_bit_law"],
            "exact_non_bit_correction_count_first_saved": r["exact_non_bit_correction_count_first_saved"],
        })

    order = {x: i for i, x in enumerate(TARGET_ORDER)}
    rows.sort(key=lambda x: order[x["target"]])
    return rows


def contains_all(text, phrases):
    missing = []
    for phrase in phrases:
        if phrase not in text:
            missing.append(phrase)
    return missing


def contains_any(text, phrases):
    found = []
    for phrase in phrases:
        if phrase in text:
            found.append(phrase)
    return found


def main():
    a041 = load_json(IN_041)
    a042 = load_json(IN_042)
    a043 = load_json(IN_043)
    a044 = load_json(IN_044)
    a045 = load_json(IN_045)

    assert_true("041 extract_pass", a041.get("extract_pass"))
    assert_true("042 audit_pass", a042.get("audit_pass"))
    assert_true("043 audit_pass", a043.get("audit_pass"))
    assert_true("044 audit_pass", a044.get("audit_pass"))
    assert_true("045 shared_header_grammar_pass", a045["checks"].get("shared_header_grammar_pass"))

    target_rows = target_rows_from_045(a045)

    classification_targets = a045["classification_targets"]
    checks_045 = a045["checks"]

    closed_statement = (
        "Given the reduced four-state Lift/Twist local-cell target and the imported canonical 24-row station register, "
        "Project 24 now records a local scalar-provenance normal form. The station register gives a clean state-to-station join. "
        "Each scalar target is represented as a station-register base readout, plus an exact station-register correction where available, "
        "plus a bounded two-bit residual header over basis [1,b,r,b*r]."
    )

    result_statement = (
        "The six nontrivial scalar targets split as follows: relay_size has station-base exact zero residual; "
        "free_min and relay_min have exact station-register corrections; free_sum, relay_max, and relay_sum remain as "
        "small bounded two-bit header residuals."
    )

    boundary_statement = (
        "This is a reduced four-state local normal form, not native closure. It does not derive the bounded header from native G60 structure, "
        "does not derive the full role-labeled shared_B universe, and is not Gap A closure."
    )

    combined = "\n".join([closed_statement, result_statement, boundary_statement])

    missing_closed = contains_all(combined, REQUIRED_CLOSED_PHRASES)
    missing_boundary = contains_all(combined, REQUIRED_BOUNDARY_PHRASES)
    forbidden_found = contains_any(combined, FORBIDDEN_PHRASES)

    checks = {
        "station_extract_041_pass": bool(a041.get("extract_pass")),
        "station_scalar_join_042_pass": bool(a042.get("audit_pass")),
        "coupled_register_043_pass": bool(a043.get("audit_pass")),
        "residual_correction_044_pass": bool(a044.get("audit_pass")),
        "shared_header_045_pass": bool(a045["checks"].get("shared_header_grammar_pass")),
        "canonical_24_row_station_register": canonical_row_count(a041) == 24,
        "clean_state_to_station_join": bool(a042["checks"].get("all_state_join_checks")),
        "direct_station_derivation_not_claimed": not bool(a042.get("station_direct_derivation_pass")),
        "nontrivial_target_count_is_6": checks_045.get("nontrivial_target_count") == 6,
        "corrected_or_zero_count_is_3": checks_045.get("corrected_or_zero_count") == 3,
        "remaining_small_header_count_is_3": checks_045.get("remaining_small_header_count") == 3,
        "all_residuals_small_header": bool(checks_045.get("all_residuals_small_header")),
        "all_residuals_compress_target_bit_law": bool(checks_045.get("all_residuals_compress_target_bit_law")),
        "max_residual_coeff_l1_at_most_9": int(checks_045.get("max_residual_coeff_l1")) <= 9,
        "max_residual_abs_coeff_at_most_3": int(checks_045.get("max_residual_abs_coeff")) <= 3,
        "required_closed_phrases_present": len(missing_closed) == 0,
        "required_boundary_phrases_present": len(missing_boundary) == 0,
        "forbidden_phrases_absent": len(forbidden_found) == 0,
    }

    checkpoint_pass = all(checks.values())

    result = {
        "status": "local_scalar_provenance_checkpoint_recorded",
        "audit_id": "046",
        "inputs": {
            "station_extract_041": str(IN_041),
            "station_scalar_join_042": str(IN_042),
            "coupled_register_043": str(IN_043),
            "residual_correction_044": str(IN_044),
            "shared_residual_grammar_045": str(IN_045),
        },
        "checks": checks,
        "checkpoint_pass": checkpoint_pass,
        "station_register_summary_041": get_041_summary(a041),
        "classification_targets_045": classification_targets,
        "target_rows": target_rows,
        "closed_statement": closed_statement,
        "result_statement": result_statement,
        "boundary_statement": boundary_statement,
        "missing_closed_phrases": missing_closed,
        "missing_boundary_phrases": missing_boundary,
        "forbidden_phrases_found": forbidden_found,
        "normal_form": {
            "name": "local scalar-provenance normal form",
            "formula": "scalar target = station-register base readout + exact station correction where available + bounded two-bit residual header",
            "header_basis": ["1", "b", "r", "b*r"],
            "header_bound": "max_abs_coeff <= 3 and coefficient_l1 <= 9",
        },
        "interpretation": (
            "This checkpoint packages artifacts 041 through 045 into one bounded local result. "
            "The scalar-provenance problem is compressed into a station-register normal form with a small residual header, but it is not closed."
        ),
        "boundary": (
            "This checkpoint is a reduced four-state local result. It does not derive the bounded header from native G60 structure, "
            "does not derive the full role-labeled shared_B universe, and does not close Gap A."
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
            "target_values",
            "base_values",
            "residual",
            "target_coeff_l1",
            "residual_coeff_l1",
            "residual_max_abs_coeff",
        ])
        for r in target_rows:
            w.writerow([
                r["target"],
                r["classification"],
                r["base_feature"],
                json.dumps(r["target_values"], sort_keys=True),
                json.dumps(r["base_values"], sort_keys=True),
                json.dumps(r["residual"], sort_keys=True),
                r["target_coeff_l1"],
                r["residual_coeff_l1"],
                r["residual_max_abs_coeff"],
            ])

    lines = []
    lines.append("# Local scalar provenance checkpoint 046")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- checkpoint_pass: `" + str(checkpoint_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Closed statement")
    lines.append("")
    lines.append(closed_statement)
    lines.append("")
    lines.append("## Result statement")
    lines.append("")
    lines.append(result_statement)
    lines.append("")
    lines.append("## Normal form")
    lines.append("")
    lines.append("```text")
    lines.append(result["normal_form"]["formula"])
    lines.append("```")
    lines.append("")
    lines.append("- header_basis: `" + str(result["normal_form"]["header_basis"]) + "`")
    lines.append("- header_bound: `" + result["normal_form"]["header_bound"] + "`")
    lines.append("")
    lines.append("## Target classification")
    lines.append("")
    for k, v in classification_targets.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Target rows")
    lines.append("")
    for r in target_rows:
        lines.append("- " + r["target"] + ":")
        lines.append("  - classification: `" + r["classification"] + "`")
        lines.append("  - base_feature: `" + r["base_feature"] + "`")
        lines.append("  - target_values: `" + str(r["target_values"]) + "`")
        lines.append("  - base_values: `" + str(r["base_values"]) + "`")
        lines.append("  - residual: `" + str(r["residual"]) + "`")
        lines.append("  - target_coeff_l1: `" + str(r["target_coeff_l1"]) + "`")
        lines.append("  - residual_coeff_l1: `" + str(r["residual_coeff_l1"]) + "`")
        lines.append("  - residual_max_abs_coeff: `" + str(r["residual_max_abs_coeff"]) + "`")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(boundary_statement)
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(result["interpretation"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("checkpoint_pass", checkpoint_pass)
    for k, v in checks.items():
        print(k, v)
    print("classification_targets", classification_targets)


if __name__ == "__main__":
    main()
