#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_052 = ROOT / "artifacts/json/null_completion_header_interpretation_052.v1.json"
IN_053 = ROOT / "artifacts/json/completion_ladder_provenance_frontier_053.v1.json"
IN_055 = ROOT / "artifacts/json/form_index_provenance_audit_055.v1.json"

OUT_JSON = ROOT / "artifacts/json/euclidean_completion_ladder_schema_056.v1.json"
OUT_CSV = ROOT / "artifacts/csv/euclidean_completion_ladder_schema_056.v1.csv"
OUT_NOTE = ROOT / "notes/euclidean_completion_ladder_schema_056.md"

REQUIRED_PHRASES = [
    "Euclidean local completion ladder",
    "construction grammar",
    "null -> point -> edge -> hinge -> closed face -> filled cell",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
]

FORBIDDEN_PHRASES = [
    "Gap A is closed",
    "native closure achieved",
    "Euclid establishes native G60 derivation",
    "completion ladder proven natively",
    "answer-label leakage ruled out",
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
    a052 = load_json(IN_052)
    a053 = load_json(IN_053)
    a055 = load_json(IN_055)

    if not a052.get("interpretation_candidate_pass"):
        raise SystemExit("052 interpretation_candidate_pass is not true")
    if not a053.get("frontier_pass"):
        raise SystemExit("053 frontier_pass is not true")
    if not a055.get("audit_pass"):
        raise SystemExit("055 audit_pass is not true")

    ladder = [
        {
            "level": 0,
            "name": "null",
            "euclidean_reading": "no constructed object is yet given",
            "construction_role": "pre-given absence",
            "active_in_reduced_cell": False,
        },
        {
            "level": 1,
            "name": "point",
            "euclidean_reading": "a position is marked",
            "construction_role": "primitive mark",
            "active_in_reduced_cell": False,
        },
        {
            "level": 2,
            "name": "edge",
            "euclidean_reading": "two marked points are joined",
            "construction_role": "first relation",
            "active_in_reduced_cell": True,
        },
        {
            "level": 3,
            "name": "hinge",
            "euclidean_reading": "two joined edges share a point but remain open",
            "construction_role": "open angle or local turn",
            "active_in_reduced_cell": True,
        },
        {
            "level": 4,
            "name": "closed_face",
            "euclidean_reading": "the hinge closes into a bounded face",
            "construction_role": "closed boundary",
            "active_in_reduced_cell": True,
        },
        {
            "level": 5,
            "name": "filled_cell",
            "euclidean_reading": "the closed boundary is treated as carrying interior",
            "construction_role": "bounded interior",
            "active_in_reduced_cell": True,
        },
    ]

    state_rows = []
    by_level = {row["level"]: row for row in ladder}
    for row in a052.get("state_rows", []):
        level = int(row["completion_level"])
        state_rows.append({
            "state": row["state"],
            "b": int(row["b"]),
            "r": int(row["r"]),
            "c_row": int(row["c_row"]),
            "completion_level": level,
            "completion_name": row["completion_name"],
            "euclidean_reading": by_level[level]["euclidean_reading"],
            "construction_role": by_level[level]["construction_role"],
            "headers": [
                int(row["predicted_headers"]["free_sum"]),
                int(row["predicted_headers"]["relay_max"]),
                int(row["predicted_headers"]["relay_sum"]),
            ],
            "match": bool(row["all_match"]),
        })

    levels = [row["completion_level"] for row in state_rows]
    names = [row["completion_name"] for row in state_rows]

    schema_statement = (
        "Artifact 056 records the Euclidean local completion ladder as a construction grammar: "
        "null -> point -> edge -> hinge -> closed face -> filled cell. "
        "This does not claim that Euclid establishes a native G60 derivation. It records that the ladder used in 052 has a classical constructive shape: "
        "primitive mark, relation, open angle, closed boundary, bounded interior."
    )

    project_statement = (
        "The reduced local cell occupies the active Euclidean window edge -> hinge -> closed face -> filled cell. "
        "In the current artifacts this is exactly the 052 window completion_level = c_row + 2, while 055 keeps the provenance boundary honest: "
        "form_index remains a candidate source with answer-label leakage risk."
    )

    next_attack = (
        "The next native target is to derive this construction grammar internally: show why the native G60/shared_B or lift-twist records produce the local order "
        "edge, hinge, closed face, filled cell without using record order, form_index as a label, or the already-selected reduced answer."
    )

    boundary = (
        "This is a schema artifact, not native closure. It does not prove the completion ladder natively, "
        "does not rule out answer-label leakage, is not full role-labeled shared_B universe derivation, and is not Gap A closure."
    )

    combined = schema_statement + "\n" + project_statement + "\n" + next_attack + "\n" + boundary
    missing = missing_phrases(combined, REQUIRED_PHRASES)
    forbidden = found_phrases(combined, FORBIDDEN_PHRASES)

    checks = {
        "null_completion_header_052_pass": bool(a052.get("interpretation_candidate_pass")),
        "completion_frontier_053_pass": bool(a053.get("frontier_pass")),
        "form_index_audit_055_pass": bool(a055.get("audit_pass")),
        "form_index_candidate_but_leakage_risk": a055.get("verdict") == "form_index_has_candidates_but_order_label_leakage_risk",
        "active_window_is_2_3_4_5": levels == [2, 3, 4, 5],
        "active_names_are_edge_hinge_closed_face_filled_cell": names == ["edge", "hinge", "closed_face", "filled_cell"],
        "all_052_state_rows_match": all(row["match"] for row in state_rows),
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden) == 0,
    }

    schema_pass = all(checks.values())

    result = {
        "status": "euclidean_completion_ladder_schema_recorded",
        "audit_id": "056",
        "inputs": {
            "null_completion_header_interpretation_052": str(IN_052),
            "completion_ladder_provenance_frontier_053": str(IN_053),
            "form_index_provenance_audit_055": str(IN_055),
        },
        "checks": checks,
        "schema_pass": schema_pass,
        "ladder": ladder,
        "state_rows": state_rows,
        "schema_statement": schema_statement,
        "project_statement": project_statement,
        "next_attack": next_attack,
        "boundary": boundary,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden,
        "interpretation": (
            "Artifact 056 does not add a native derivation. It names the shape of the 052 ladder as a Euclidean local completion ladder. "
            "This gives the next provenance attack a clean target: derive the constructive ladder from native records rather than merely matching form_index."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "kind",
            "level",
            "name",
            "state",
            "c_row",
            "headers",
            "construction_role",
            "euclidean_reading",
            "active_in_reduced_cell",
        ])
        for row in ladder:
            w.writerow([
                "ladder",
                row["level"],
                row["name"],
                "",
                "",
                "",
                row["construction_role"],
                row["euclidean_reading"],
                row["active_in_reduced_cell"],
            ])
        for row in state_rows:
            w.writerow([
                "state_window",
                row["completion_level"],
                row["completion_name"],
                row["state"],
                row["c_row"],
                json.dumps(row["headers"]),
                row["construction_role"],
                row["euclidean_reading"],
                True,
            ])

    lines = []
    lines.append("# Euclidean completion ladder schema 056")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- schema_pass: `" + str(schema_pass) + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Schema statement")
    lines.append("")
    lines.append(schema_statement)
    lines.append("")
    lines.append("## Ladder")
    lines.append("")
    for row in ladder:
        lines.append(
            "- {level}: {name} - {role} - {reading}".format(
                level=row["level"],
                name=row["name"],
                role=row["construction_role"],
                reading=row["euclidean_reading"],
            )
        )
    lines.append("")
    lines.append("## Reduced local window")
    lines.append("")
    for row in state_rows:
        lines.append(
            "- {state}: c_row={c_row}, completion_level={level}, name={name}, headers={headers}, role={role}".format(
                state=row["state"],
                c_row=row["c_row"],
                level=row["completion_level"],
                name=row["completion_name"],
                headers=row["headers"],
                role=row["construction_role"],
            )
        )
    lines.append("")
    lines.append("## Project statement")
    lines.append("")
    lines.append(project_statement)
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
    lines.append(boundary)
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("schema_pass", schema_pass)
    for k, v in checks.items():
        print(k, v)
    print("active_levels", levels)
    print("active_names", names)


if __name__ == "__main__":
    main()
