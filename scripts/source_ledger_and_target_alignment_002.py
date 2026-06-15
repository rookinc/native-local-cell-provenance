#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

P22_JSON = ROOT / "source/project22_artifacts/json"
P23_JSON = ROOT / "source/project23_artifacts/json"
P18_PAYLOAD = ROOT / "source/project18_payload"

OUT_JSON = ROOT / "artifacts/json/source_ledger_and_target_alignment_002.v1.json"
OUT_CSV = ROOT / "artifacts/csv/source_ledger_and_target_alignment_002.v1.csv"
OUT_NOTE = ROOT / "notes/source_ledger_and_target_alignment_002.md"

REQUIRED_PROJECT22 = {
    "target_006": "lift_twist_local_answer_cell_target_006.v1.json",
    "bit_law_007": "lift_twist_local_answer_cell_bit_law_007.v1.json",
    "overlap_008": "lift_twist_payload_overlap_marker_law_008.v1.json",
    "c_path_009": "lift_twist_c_payload_path_law_009.v1.json",
    "anchor_residue_010": "lift_twist_anchor_residue_set_law_010.v1.json",
    "generator_011": "lift_twist_local_answer_cell_generator_theorem_011.v1.json",
    "anchor_path_012": "lift_twist_anchor_node_path_geometry_012.v1.json",
    "boundary_014": "local_cell_theorem_boundary_audit_014.v1.json",
}

REQUIRED_PROJECT23 = {
    "reduced_universe_002": "local_cell_to_reduced_universe_derivation_002.v1.json",
    "boundary_003": "local_cell_to_reduced_universe_boundary_audit_003.v1.json",
    "paper_sync_004": "reduced_universe_theorem_sync_004.v1.json",
}

OPTIONAL_NATIVE = {
    "g60_local_edges": "g60_local_edges.csv",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def file_record(group, key, path, required):
    return {
        "group": group,
        "key": key,
        "path": str(path),
        "exists": path.exists(),
        "required": required,
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def read_csv_header(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        try:
            return next(r)
        except StopIteration:
            return []


def count_csv_rows(path):
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as f:
        return max(0, sum(1 for _ in f) - 1)


def main():
    ledger = []

    for key, name in REQUIRED_PROJECT22.items():
        ledger.append(file_record("project22", key, P22_JSON / name, True))

    for key, name in REQUIRED_PROJECT23.items():
        ledger.append(file_record("project23", key, P23_JSON / name, True))

    for key, name in OPTIONAL_NATIVE.items():
        ledger.append(file_record("native_payload", key, P18_PAYLOAD / name, False))

    missing_required = [x for x in ledger if x["required"] and not x["exists"]]
    available_optional = [x for x in ledger if (not x["required"]) and x["exists"]]
    missing_optional = [x for x in ledger if (not x["required"]) and not x["exists"]]

    a006 = load_json(P22_JSON / REQUIRED_PROJECT22["target_006"])
    a011 = load_json(P22_JSON / REQUIRED_PROJECT22["generator_011"])
    a012 = load_json(P22_JSON / REQUIRED_PROJECT22["anchor_path_012"])
    a014 = load_json(P22_JSON / REQUIRED_PROJECT22["boundary_014"])
    a23002 = load_json(P23_JSON / REQUIRED_PROJECT23["reduced_universe_002"])
    a23003 = load_json(P23_JSON / REQUIRED_PROJECT23["boundary_003"])

    local_rows = a011.get("generated_rows", [])
    states = [r.get("state") for r in local_rows]
    selected = [r.get("selected_candidate_index") for r in local_rows]
    c_paths = {r.get("state"): r.get("c_path") for r in local_rows}
    anchor_residues = {r.get("state"): r.get("anchor_residues") for r in local_rows}
    overlaps = {r.get("state"): r.get("overlap") for r in local_rows}

    native_payload = P18_PAYLOAD / OPTIONAL_NATIVE["g60_local_edges"]
    native_payload_report = {
        "g60_local_edges_exists": native_payload.exists(),
        "g60_local_edges_header": read_csv_header(native_payload),
        "g60_local_edges_row_count": count_csv_rows(native_payload),
    }

    alignment_checks = {
        "required_project22_sources_present": all(x["exists"] for x in ledger if x["group"] == "project22"),
        "required_project23_sources_present": all(x["exists"] for x in ledger if x["group"] == "project23"),
        "project22_011_theorem_pass": bool(a011.get("theorem_pass")),
        "project22_012_theorem_pass": bool(a012.get("theorem_pass")),
        "project22_014_boundary_pass": bool(a014.get("boundary_pass")),
        "project23_002_theorem_pass": bool(a23002.get("theorem_pass")),
        "project23_003_boundary_pass": bool(a23003.get("boundary_pass")),
        "local_state_count_is_4": len(states) == 4,
        "local_states_match_expected": states == ["O0", "O1", "B0", "B1"],
        "selected_candidates_match_expected": selected == [1, 6, 8, 15],
        "project23_diagonal_matches_project22_selected": a23002.get("diagonal_indices") == selected,
    }

    ready_for_native_search = (
        all(alignment_checks.values())
        and len(missing_required) == 0
    )

    if native_payload.exists():
        next_route = [
            "Use copied g60_local_edges.csv as initial native edge source.",
            "Test whether Project 22 C paths are literal G60 paths, quotient-supported paths, or transition overlays.",
            "Test whether anchor residue sets correspond to G60 neighborhoods, lifted masks, or station-pair closures.",
            "Search for ordinary/branch shell markers in native payload fields.",
        ]
    else:
        next_route = [
            "Required theorem targets are present, but no copied native G60 edge payload was found.",
            "Locate canonical G60 local edge payload or import it from the current lab/repo before native derivation tests.",
            "Then test C paths, anchor residues, and shell markers against native records.",
        ]

    result = {
        "status": "source_ledger_and_target_alignment_recorded",
        "audit_id": "002",
        "ledger": ledger,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "available_optional": available_optional,
        "native_payload_report": native_payload_report,
        "local_cell_target": {
            "states": states,
            "selected_candidates": selected,
            "c_paths": c_paths,
            "anchor_residues": anchor_residues,
            "overlaps": overlaps,
        },
        "alignment_checks": alignment_checks,
        "ready_for_native_search": ready_for_native_search,
        "next_route": next_route,
        "closed_inputs": [
            "Project 22 local-cell kernel is available.",
            "Project 23 reduced-universe derivation is available.",
        ],
        "open_boundary": [
            "No native local-cell provenance theorem is claimed.",
            "No full role-labeled shared_B edge universe is derived.",
            "Gap A is not closed.",
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "key", "required", "exists", "size_bytes", "path"])
        for x in ledger:
            w.writerow([x["group"], x["key"], x["required"], x["exists"], x["size_bytes"], x["path"]])

    lines = []
    lines.append("# Source ledger and target alignment 002")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Alignment")
    lines.append("")
    for k, v in alignment_checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("- ready_for_native_search: `" + str(ready_for_native_search) + "`")
    lines.append("")
    lines.append("## Local-cell target")
    lines.append("")
    lines.append("- states: `" + str(states) + "`")
    lines.append("- selected_candidates: `" + str(selected) + "`")
    lines.append("- c_paths: `" + str(c_paths) + "`")
    lines.append("- anchor_residues: `" + str(anchor_residues) + "`")
    lines.append("- overlaps: `" + str(overlaps) + "`")
    lines.append("")
    lines.append("## Native payload report")
    lines.append("")
    for k, v in native_payload_report.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Missing required sources")
    lines.append("")
    if missing_required:
        for x in missing_required:
            lines.append("- `" + x["group"] + "/" + x["key"] + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Missing optional sources")
    lines.append("")
    if missing_optional:
        for x in missing_optional:
            lines.append("- `" + x["group"] + "/" + x["key"] + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Next route")
    lines.append("")
    for x in next_route:
        lines.append("- " + x)
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    for x in result["open_boundary"]:
        lines.append("- " + x)
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("ready_for_native_search", ready_for_native_search)
    print("missing_required_count", len(missing_required))
    print("g60_local_edges_exists", native_payload.exists())
    print("g60_local_edges_row_count", native_payload_report["g60_local_edges_row_count"])


if __name__ == "__main__":
    main()
