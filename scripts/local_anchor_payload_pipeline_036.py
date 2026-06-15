#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_007 = ROOT / "artifacts/json/native_g60_c_path_residue_two_hop_relay_007.v1.json"
IN_018 = ROOT / "artifacts/json/native_g60_anchor_lift_mask_sheet_selector_018.v1.json"
IN_023 = ROOT / "artifacts/json/native_g60_anchor_rank_selector_theorem_023.v1.json"
IN_032 = ROOT / "artifacts/json/free_block_scalar_law_selector_032.v1.json"
IN_033 = ROOT / "artifacts/json/local_anchor_residue_derivation_chain_033.v1.json"
IN_034 = ROOT / "artifacts/json/local_anchor_path_derivation_chain_034.v1.json"
IN_035 = ROOT / "artifacts/json/native_g60_relay_block_selector_from_mediators_035.v1.json"

OUT_JSON = ROOT / "artifacts/json/local_anchor_payload_pipeline_036.v1.json"
OUT_CSV = ROOT / "artifacts/csv/local_anchor_payload_pipeline_036.v1.csv"
OUT_NOTE = ROOT / "notes/local_anchor_payload_pipeline_036.md"

STATES = ["O0", "O1", "B0", "B1"]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sorted_ints(xs):
    return sorted(int(x) for x in xs)


def first_selected(blocks):
    if not isinstance(blocks, list) or len(blocks) != 1:
        return None
    return sorted_ints(blocks[0])


def main():
    a007 = load_json(IN_007)
    a018 = load_json(IN_018)
    a023 = load_json(IN_023)
    a032 = load_json(IN_032)
    a033 = load_json(IN_033)
    a034 = load_json(IN_034)
    a035 = load_json(IN_035)

    if not a007.get("theorem_pass"):
        raise SystemExit("007 theorem_pass is not true")
    if not a018.get("theorem_pass"):
        raise SystemExit("018 theorem_pass is not true")
    if not a023.get("theorem_pass"):
        raise SystemExit("023 theorem_pass is not true")
    if not a032.get("theorem_candidate_pass"):
        raise SystemExit("032 theorem_candidate_pass is not true")
    if not a033.get("theorem_candidate_pass"):
        raise SystemExit("033 theorem_candidate_pass is not true")
    if not a034.get("theorem_candidate_pass"):
        raise SystemExit("034 theorem_candidate_pass is not true")
    if not a035.get("theorem_candidate_pass"):
        raise SystemExit("035 theorem_candidate_pass is not true")

    per_state = {}
    rows = []

    for state in STATES:
        s035 = a035["per_state"][state]
        s032 = a032["per_state"][state]
        s033 = a033["per_state"][state]
        s034 = a034["per_state"][state]

        relay_from_035 = first_selected(s035.get("selected_relay_blocks"))
        free_from_032 = first_selected(s032.get("selected_free_blocks"))

        if relay_from_035 is None:
            relay_from_035 = []
        if free_from_032 is None:
            free_from_032 = []

        anchor_from_035_032 = sorted(set(relay_from_035).union(set(free_from_032)))

        relay_033 = sorted_ints(s033["relay_block"])
        free_033 = sorted_ints(s033["selected_free_block"])
        anchor_033 = sorted_ints(s033["generated_anchor_residue_set"])

        node_residues_034 = sorted_ints(s034["anchor_node_path_residue_set"])
        node_path_034 = s034["anchor_node_path"]
        lift_mask_034 = [int(x) for x in s034["sheet_mask_by_node_ge_15"]]

        rec = {
            "state": state,
            "mediator_union_035": sorted_ints(s035["mediator_union"]),
            "relay_block_from_035": relay_from_035,
            "relay_block_from_033": relay_033,
            "relay_blocks_match": relay_from_035 == relay_033,
            "free_block_from_032": free_from_032,
            "free_block_from_033": free_033,
            "free_blocks_match": free_from_032 == free_033,
            "anchor_from_relay_union_free": anchor_from_035_032,
            "anchor_from_033": anchor_033,
            "anchor_union_matches_033": anchor_from_035_032 == anchor_033,
            "anchor_node_path_034": node_path_034,
            "anchor_node_residues_034": node_residues_034,
            "anchor_matches_node_residues": anchor_033 == node_residues_034,
            "lift_mask_from_034": lift_mask_034,
            "state_pipeline_pass": (
                relay_from_035 == relay_033
                and free_from_032 == free_033
                and anchor_from_035_032 == anchor_033
                and anchor_033 == node_residues_034
            ),
        }

        per_state[state] = rec
        rows.append(rec)

    checks = {
        "two_hop_relay_007_theorem_pass": bool(a007.get("theorem_pass")),
        "lift_mask_sheet_018_theorem_pass": bool(a018.get("theorem_pass")),
        "anchor_rank_selector_023_theorem_pass": bool(a023.get("theorem_pass")),
        "free_block_scalar_032_theorem_candidate_pass": bool(a032.get("theorem_candidate_pass")),
        "anchor_residue_chain_033_theorem_candidate_pass": bool(a033.get("theorem_candidate_pass")),
        "anchor_path_chain_034_theorem_candidate_pass": bool(a034.get("theorem_candidate_pass")),
        "relay_selector_035_theorem_candidate_pass": bool(a035.get("theorem_candidate_pass")),
        "mediator_source_is_artifact_007_parsed": a035.get("mediator_source") == "artifact_007_parsed",
        "relay_target_source_is_artifact_011_rows": a035.get("relay_target_source") == "artifact_011_rows",
        "all_relay_blocks_match_between_035_and_033": all(
            per_state[s]["relay_blocks_match"] for s in STATES
        ),
        "all_free_blocks_match_between_032_and_033": all(
            per_state[s]["free_blocks_match"] for s in STATES
        ),
        "all_anchor_unions_match_033": all(
            per_state[s]["anchor_union_matches_033"] for s in STATES
        ),
        "all_anchor_sets_match_034_node_residues": all(
            per_state[s]["anchor_matches_node_residues"] for s in STATES
        ),
        "all_state_pipelines_pass": all(
            per_state[s]["state_pipeline_pass"] for s in STATES
        ),
    }

    source_caveats = []
    if a034.get("path_source") == "known_project22_anchor_node_paths_fallback":
        source_caveats.append(
            "Artifact 034 used known Project22 anchor node paths as fallback rather than auto-extracting them from Project22 artifact 012."
        )

    result = {
        "status": "local_anchor_payload_pipeline_recorded",
        "audit_id": "036",
        "inputs": {
            "two_hop_relay_007": str(IN_007),
            "lift_mask_sheet_selector_018": str(IN_018),
            "anchor_rank_selector_023": str(IN_023),
            "free_block_scalar_selector_032": str(IN_032),
            "anchor_residue_chain_033": str(IN_033),
            "anchor_path_chain_034": str(IN_034),
            "relay_selector_035": str(IN_035),
        },
        "pipeline": [
            "artifact 007 supplies native two-hop C-transition mediator geometry",
            "artifact 035 selects relay blocks from mediator geometry",
            "artifact 032 selects free blocks from state-bit scalar laws",
            "artifact 033 unions relay blocks and free blocks to generate anchor residue sets",
            "artifact 023 selects anchor paths inside the generated residue-set candidate universe",
            "artifact 034 verifies node-path residues and lift masks via node-sheet rule",
        ],
        "per_state": per_state,
        "checks": checks,
        "source_caveats": source_caveats,
        "theorem_candidate_pass": all(checks.values()),
        "interpretation": (
            "This composes the current local anchor payload provenance pipeline. The anchor payload is now generated from "
            "native two-hop mediator geometry plus compact state-bit scalar selectors, then matched through anchor residues, "
            "anchor paths, and lift masks."
        ),
        "boundary": (
            "This is not full Gap A closure. The scalar laws still need native/provenance interpretation, artifact 034 has a "
            "source-binding caveat if it used fallback anchor paths, and the full role-labeled shared_B universe is not yet derived."
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
            "relay_block_from_035",
            "free_block_from_032",
            "anchor_from_relay_union_free",
            "anchor_node_residues_034",
            "lift_mask_from_034",
            "state_pipeline_pass",
        ])
        for row in rows:
            w.writerow([
                row["state"],
                json.dumps(row["relay_block_from_035"]),
                json.dumps(row["free_block_from_032"]),
                json.dumps(row["anchor_from_relay_union_free"]),
                json.dumps(row["anchor_node_residues_034"]),
                json.dumps(row["lift_mask_from_034"]),
                "1" if row["state_pipeline_pass"] else "0",
            ])

    lines = []
    lines.append("# Local anchor payload pipeline 036")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- theorem_candidate_pass: `" + str(result["theorem_candidate_pass"]) + "`")
    lines.append("- source_caveat_count: `" + str(len(source_caveats)) + "`")
    lines.append("")
    lines.append("## Pipeline")
    lines.append("")
    for item in result["pipeline"]:
        lines.append("- " + item)
    lines.append("")
    lines.append("## Per state")
    lines.append("")
    for state in STATES:
        p = per_state[state]
        lines.append("- " + state + ":")
        lines.append("  - mediator_union_035: `" + str(p["mediator_union_035"]) + "`")
        lines.append("  - relay_block_from_035: `" + str(p["relay_block_from_035"]) + "`")
        lines.append("  - free_block_from_032: `" + str(p["free_block_from_032"]) + "`")
        lines.append("  - anchor_from_relay_union_free: `" + str(p["anchor_from_relay_union_free"]) + "`")
        lines.append("  - anchor_node_residues_034: `" + str(p["anchor_node_residues_034"]) + "`")
        lines.append("  - lift_mask_from_034: `" + str(p["lift_mask_from_034"]) + "`")
        lines.append("  - state_pipeline_pass: `" + str(p["state_pipeline_pass"]) + "`")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Source caveats")
    lines.append("")
    if source_caveats:
        for c in source_caveats:
            lines.append("- " + c)
    else:
        lines.append("- none")
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
    print("theorem_candidate_pass", result["theorem_candidate_pass"])
    print("source_caveat_count", len(source_caveats))
    for state in STATES:
        p = per_state[state]
        print(
            state,
            "relay", p["relay_block_from_035"],
            "free", p["free_block_from_032"],
            "anchor", p["anchor_from_relay_union_free"],
            "mask", p["lift_mask_from_034"],
            "pass", p["state_pipeline_pass"],
        )


if __name__ == "__main__":
    main()
