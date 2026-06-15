#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_050 = ROOT / "artifacts/json/header_frontier_after_upstream_locator_050.v1.json"
IN_051 = ROOT / "artifacts/json/native_two_bit_header_mechanism_051.v1.json"
IN_052 = ROOT / "artifacts/json/null_completion_header_interpretation_052.v1.json"

OUT_JSON = ROOT / "artifacts/json/completion_ladder_provenance_frontier_053.v1.json"
OUT_CSV = ROOT / "artifacts/csv/completion_ladder_provenance_frontier_053.v1.csv"
OUT_NOTE = ROOT / "notes/completion_ladder_provenance_frontier_053.md"

REQUIRED_PHRASES = [
    "header expression is closed",
    "completion ladder provenance remains open",
    "null-completion header",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "completion ladder proven natively",
    "full shared_B universe derived",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def missing_phrases(text, phrases):
    return [p for p in phrases if p not in text]


def found_phrases(text, phrases):
    return [p for p in phrases if p in text]


def main():
    a050 = load_json(IN_050)
    a051 = load_json(IN_051)
    a052 = load_json(IN_052)

    if not a050.get("frontier_pass"):
        raise SystemExit("050 frontier_pass is not true")
    if not a051.get("theorem_candidate_pass"):
        raise SystemExit("051 theorem_candidate_pass is not true")
    if not a052.get("interpretation_candidate_pass"):
        raise SystemExit("052 interpretation_candidate_pass is not true")

    closed_or_stabilized = [
        {
            "item": "same_layer_and_imported_upstream_header_source_absence",
            "status": "bounded_negative_stabilized",
            "evidence": "050 records that the bounded header was not sourced by same-layer station search or imported-upstream scan.",
        },
        {
            "item": "bounded_header_coordinate_expression",
            "status": "closed_at_reduced_coordinate_layer",
            "evidence": "051 exactly recovers free_sum, relay_max, and relay_sum from b, r, and c_row.",
        },
        {
            "item": "completion_window",
            "status": "stabilized",
            "evidence": "052 identifies the local completion window as levels 2,3,4,5: edge, hinge, closed_face, filled_cell.",
        },
        {
            "item": "null_completion_header_reading",
            "status": "stabilized_as_interpretation",
            "evidence": "052 interprets the 051 coordinate header as a null-completion header.",
        },
    ]

    open_items = [
        {
            "item": "completion_ladder_native_provenance",
            "status": "open",
            "evidence": "052 explicitly does not derive the completion ladder from the full native G60/shared_B universe.",
        },
        {
            "item": "why_c_row_lifts_to_completion_level_plus_two",
            "status": "open",
            "evidence": "052 uses completion_level=c_row+2 as an exact interpretation, but does not derive the +2 lift natively.",
        },
        {
            "item": "native_two_bit_coordinate_source",
            "status": "open",
            "evidence": "051 derives the header from reduced coordinates but does not derive those coordinates from full native G60/shared_B structure.",
        },
        {
            "item": "full_role_labeled_shared_B_universe",
            "status": "open",
            "evidence": "050, 051, and 052 explicitly do not derive the full role-labeled shared_B universe.",
        },
        {
            "item": "Gap_A_closure",
            "status": "open",
            "evidence": "050, 051, and 052 explicitly state this is not Gap A closure.",
        },
    ]

    phase_transition_statement = (
        "After 052, the project has crossed a useful boundary. The header expression is closed at the reduced coordinate layer, "
        "and the bounded header has a stable null-completion header reading. However, completion ladder provenance remains open. "
        "The remaining target is not to express the header again, but to derive why the reduced local cell occupies the edge -> hinge -> closed face -> filled cell window. "
        "This is not native closure, not full role-labeled shared_B universe derivation, and not Gap A closure."
    )

    next_attack = (
        "The next attack should target the native source of the completion ladder: why null -> point -> edge -> hinge -> closed face -> filled cell is the right ladder, "
        "why the local window starts at edge, why c_row lifts by +2, and how that ladder is encoded by the native G60/shared_B structure."
    )

    combined = phase_transition_statement + "\n" + next_attack
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    state_rows_052 = a052.get("state_rows", [])
    completion_levels = [row.get("completion_level") for row in state_rows_052]
    completion_names = [row.get("completion_name") for row in state_rows_052]

    checks = {
        "frontier_050_pass": bool(a050.get("frontier_pass")),
        "native_two_bit_header_051_pass": bool(a051.get("theorem_candidate_pass")),
        "null_completion_header_052_pass": bool(a052.get("interpretation_candidate_pass")),
        "header_source_absence_stabilized": a050.get("checks", {}).get("locator_049_verdict_is_no_source") is True,
        "header_expression_closed_at_reduced_coordinate_layer": bool(a051.get("checks", {}).get("all_target_formulas_match")),
        "null_completion_reading_stabilized": bool(a052.get("checks", {}).get("all_state_rows_match")),
        "completion_window_is_2_3_4_5": completion_levels == [2, 3, 4, 5],
        "completion_names_are_edge_hinge_closed_face_filled_cell": completion_names == ["edge", "hinge", "closed_face", "filled_cell"],
        "closed_or_stabilized_count": len(closed_or_stabilized),
        "open_item_count": len(open_items),
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    frontier_pass = all(checks.values())

    result = {
        "status": "completion_ladder_provenance_frontier_recorded",
        "audit_id": "053",
        "inputs": {
            "header_frontier_after_upstream_locator_050": str(IN_050),
            "native_two_bit_header_mechanism_051": str(IN_051),
            "null_completion_header_interpretation_052": str(IN_052),
        },
        "checks": checks,
        "frontier_pass": frontier_pass,
        "phase_transition_statement": phase_transition_statement,
        "next_attack": next_attack,
        "closed_or_stabilized": closed_or_stabilized,
        "open_items": open_items,
        "completion_window": {
            "levels": completion_levels,
            "names": completion_names,
        },
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "This artifact records the phase transition after 051 and 052. The bounded header is no longer merely an unexplained residual: "
            "it has an exact reduced-coordinate expression and a null-completion reading. The next unresolved object is the native provenance of the completion ladder."
        ),
        "boundary": (
            "This is a frontier artifact, not a new derivation. It does not derive the completion ladder natively, "
            "does not derive the full role-labeled shared_B universe, and is not Gap A closure."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "item", "status", "evidence"])
        for row in closed_or_stabilized:
            w.writerow(["closed_or_stabilized", row["item"], row["status"], row["evidence"]])
        for row in open_items:
            w.writerow(["open", row["item"], row["status"], row["evidence"]])

    lines = []
    lines.append("# Completion ladder provenance frontier 053")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- frontier_pass: `" + str(frontier_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Phase transition statement")
    lines.append("")
    lines.append(phase_transition_statement)
    lines.append("")
    lines.append("## Closed or stabilized")
    lines.append("")
    for row in closed_or_stabilized:
        lines.append("- " + row["item"] + ": `" + row["status"] + "`")
        lines.append("  - " + row["evidence"])
    lines.append("")
    lines.append("## Open")
    lines.append("")
    for row in open_items:
        lines.append("- " + row["item"] + ": `" + row["status"] + "`")
        lines.append("  - " + row["evidence"])
    lines.append("")
    lines.append("## Completion window")
    lines.append("")
    lines.append("- levels: `" + str(completion_levels) + "`")
    lines.append("- names: `" + str(completion_names) + "`")
    lines.append("")
    lines.append("## Next attack")
    lines.append("")
    lines.append(next_attack)
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
    print("frontier_pass", frontier_pass)
    for k, v in checks.items():
        print(k, v)
    print("completion_levels", completion_levels)
    print("completion_names", completion_names)
    print("closed_or_stabilized", len(closed_or_stabilized))
    print("open_items", len(open_items))


if __name__ == "__main__":
    main()
