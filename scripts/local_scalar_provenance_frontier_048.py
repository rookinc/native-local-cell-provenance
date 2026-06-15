#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_046 = ROOT / "artifacts/json/local_scalar_provenance_checkpoint_046.v1.json"
IN_047 = ROOT / "artifacts/json/header_source_audit_047.v1.json"

OUT_JSON = ROOT / "artifacts/json/local_scalar_provenance_frontier_048.v1.json"
OUT_CSV = ROOT / "artifacts/csv/local_scalar_provenance_frontier_048.v1.csv"
OUT_NOTE = ROOT / "notes/local_scalar_provenance_frontier_048.md"

FORBIDDEN = [
    "Gap A is closed",
    "native closure achieved",
    "full shared_B universe derived",
    "header source derived",
]

REQUIRED = [
    "local scalar-provenance normal form",
    "bounded header remains open",
    "not Gap A closure",
    "not native closure",
    "not full role-labeled shared_B universe",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a046 = load_json(IN_046)
    a047 = load_json(IN_047)

    if not a046.get("checkpoint_pass"):
        raise SystemExit("046 checkpoint_pass is not true")
    if not a047.get("audit_pass"):
        raise SystemExit("047 audit_pass is not true")

    closed_items = [
        {
            "item": "canonical_24_row_station_register",
            "status": "closed_for_local_normal_form",
            "evidence": "046 confirms canonical_24_row_station_register=true using 041.",
        },
        {
            "item": "clean_state_to_station_join",
            "status": "closed_for_local_normal_form",
            "evidence": "046 confirms clean_state_to_station_join=true using 042.",
        },
        {
            "item": "relay_size_station_base_exact",
            "status": "closed_for_local_normal_form",
            "evidence": "046 classifies relay_size as station_base_exact_zero_residual.",
        },
        {
            "item": "free_min_station_register_correction",
            "status": "closed_for_local_normal_form",
            "evidence": "046 classifies free_min as exact_station_register_correction.",
        },
        {
            "item": "relay_min_station_register_correction",
            "status": "closed_for_local_normal_form",
            "evidence": "046 classifies relay_min as exact_station_register_correction.",
        },
        {
            "item": "bounded_two_bit_header_normal_form",
            "status": "closed_as_compression_not_source",
            "evidence": "046 confirms all_residuals_small_header=true, max_residual_abs_coeff<=3, max_residual_coeff_l1<=9.",
        },
    ]

    open_items = [
        {
            "item": "free_sum_header_source",
            "status": "open",
            "evidence": "047 finds no exact station-feature source for free_sum header residual.",
        },
        {
            "item": "relay_max_header_source",
            "status": "open",
            "evidence": "047 finds no exact station-feature source for relay_max header residual.",
        },
        {
            "item": "relay_sum_header_source",
            "status": "open",
            "evidence": "047 finds no exact station-feature source for relay_sum header residual.",
        },
        {
            "item": "shared_header_station_family",
            "status": "open",
            "evidence": "047 reports shared_near_station_family_exists=false.",
        },
        {
            "item": "small_integer_relation_among_headers",
            "status": "open",
            "evidence": "047 reports small_integer_relation_found=false.",
        },
        {
            "item": "full_role_labeled_shared_B_universe",
            "status": "open",
            "evidence": "046 and 047 explicitly do not derive the full role-labeled shared_B universe.",
        },
        {
            "item": "Gap_A_closure",
            "status": "open",
            "evidence": "046 and 047 explicitly state this is not Gap A closure.",
        },
    ]

    plateau_statement = (
        "Project 24 has reached a local scalar-provenance normal form. "
        "The scalar package is compressed into station-register base readouts, exact station corrections where available, "
        "and a bounded two-bit residual header. The bounded header remains open. "
        "This is not native closure, not full role-labeled shared_B universe derivation, and not Gap A closure."
    )

    next_attack = (
        "The next attack should not be a wider station-feature search. "
        "It should target the provenance of the bounded header, likely by moving upstream from the reduced four-state local cell "
        "toward the source-native lift/twist mechanism, role-labeled shared_B universe, or a native explanation of the two-bit header itself."
    )

    combined = "\n".join([plateau_statement, next_attack])
    missing_required = missing_phrases(combined, REQUIRED)
    forbidden_found = found_phrases(combined, FORBIDDEN)

    checks = {
        "checkpoint_046_pass": bool(a046.get("checkpoint_pass")),
        "header_source_047_pass": bool(a047.get("audit_pass")),
        "header_source_remains_open": a047.get("verdict") == "header_source_remains_open_small_bit_header_only",
        "closed_item_count": len(closed_items),
        "open_item_count": len(open_items),
        "required_phrases_present": len(missing_required) == 0,
        "forbidden_phrases_absent": len(forbidden_found) == 0,
    }

    frontier_pass = all([
        checks["checkpoint_046_pass"],
        checks["header_source_047_pass"],
        checks["header_source_remains_open"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "local_scalar_provenance_frontier_recorded",
        "audit_id": "048",
        "inputs": {
            "local_scalar_checkpoint_046": str(IN_046),
            "header_source_audit_047": str(IN_047),
        },
        "checks": checks,
        "frontier_pass": frontier_pass,
        "plateau_statement": plateau_statement,
        "next_attack": next_attack,
        "closed_items": closed_items,
        "open_items": open_items,
        "missing_required_phrases": missing_required,
        "forbidden_phrases_found": forbidden_found,
        "interpretation": (
            "This artifact records the current plateau after 046 and 047. The local scalar package is compressed, "
            "but the bounded header remains an open provenance target."
        ),
        "boundary": (
            "This is a project-frontier record, not a new derivation. It does not close Gap A, does not derive the full role-labeled shared_B universe, "
            "and does not derive the bounded header from native structure."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "item", "status", "evidence"])
        for row in closed_items:
            w.writerow(["closed", row["item"], row["status"], row["evidence"]])
        for row in open_items:
            w.writerow(["open", row["item"], row["status"], row["evidence"]])

    lines = []
    lines.append("# Local scalar provenance frontier 048")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- frontier_pass: `" + str(frontier_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Plateau statement")
    lines.append("")
    lines.append(plateau_statement)
    lines.append("")
    lines.append("## Closed")
    lines.append("")
    for row in closed_items:
        lines.append("- " + row["item"] + ": `" + row["status"] + "`")
        lines.append("  - " + row["evidence"])
    lines.append("")
    lines.append("## Open")
    lines.append("")
    for row in open_items:
        lines.append("- " + row["item"] + ": `" + row["status"] + "`")
        lines.append("  - " + row["evidence"])
    lines.append("")
    lines.append("## Next attack")
    lines.append("")
    lines.append(next_attack)
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
    print("frontier_pass", frontier_pass)
    for k, v in checks.items():
        print(k, v)
    print("closed_items", len(closed_items))
    print("open_items", len(open_items))


if __name__ == "__main__":
    main()
