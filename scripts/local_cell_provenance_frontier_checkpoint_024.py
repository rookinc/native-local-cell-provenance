#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUTS = {
    "c_path_cover_012": ROOT / "artifacts/json/native_g60_c_path_quotient_anchor_cover_012.v1.json",
    "paper_boundary_014": ROOT / "artifacts/json/c_path_cover_paper_boundary_audit_014.v1.json",
    "anchor_literal_015": ROOT / "artifacts/json/native_g60_anchor_node_path_edge_support_015.v1.json",
    "anchor_residue_016": ROOT / "artifacts/json/native_g60_anchor_node_path_residue_pair_support_016.v1.json",
    "anchor_quotient_theorem_017": ROOT / "artifacts/json/native_g60_anchor_path_quotient_pair_theorem_017.v1.json",
    "lift_mask_sheet_018": ROOT / "artifacts/json/native_g60_anchor_lift_mask_sheet_selector_018.v1.json",
    "candidate_census_020": ROOT / "artifacts/json/native_g60_anchor_path_candidate_census_fixed_020.v1.json",
    "feature_audit_021": ROOT / "artifacts/json/native_g60_anchor_candidate_feature_audit_021.v1.json",
    "rank_law_022": ROOT / "artifacts/json/native_g60_anchor_rank_fingerprint_law_022.v1.json",
    "rank_selector_023": ROOT / "artifacts/json/native_g60_anchor_rank_selector_theorem_023.v1.json",
}

OUT_JSON = ROOT / "artifacts/json/local_cell_provenance_frontier_checkpoint_024.v1.json"
OUT_NOTE = ROOT / "notes/local_cell_provenance_frontier_checkpoint_024.md"


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data = {k: load(v) for k, v in INPUTS.items()}

    checks = {
        "c_path_cover_012_theorem_pass": data["c_path_cover_012"].get("theorem_pass") is True,
        "paper_boundary_014_pass": data["paper_boundary_014"].get("boundary_pass") is True,
        "anchor_literal_015_checks_pass": data["anchor_literal_015"].get("all_checks_pass") is True,
        "anchor_literal_015_not_full_support": data["anchor_literal_015"].get("all_anchor_pair_steps_supported") is False,
        "anchor_residue_016_full_support": data["anchor_residue_016"].get("all_anchor_residue_pair_steps_supported") is True,
        "anchor_quotient_017_theorem_pass": data["anchor_quotient_theorem_017"].get("theorem_pass") is True,
        "lift_mask_sheet_018_theorem_pass": data["lift_mask_sheet_018"].get("theorem_pass") is True,
        "candidate_census_020_theorem_pass": data["candidate_census_020"].get("theorem_pass") is True,
        "candidate_census_020_not_unique": data["candidate_census_020"].get("observed_unique_in_all_states") is False,
        "feature_audit_021_checks_pass": data["feature_audit_021"].get("all_checks_pass") is True,
        "rank_law_022_theorem_pass": data["rank_law_022"].get("theorem_pass") is True,
        "rank_selector_023_theorem_pass": data["rank_selector_023"].get("theorem_pass") is True,
    }

    closed_results = [
        {
            "id": "012",
            "claim": "Every Project22 C-path step is covered by direct mod15 G60 residue support or same-state unlifted anchor-path relay support.",
            "status": "closed intermediate theorem",
        },
        {
            "id": "017",
            "claim": "Every Project22 closed anchor node-path step is supported after projection to mod15 residue pairs.",
            "status": "closed intermediate theorem",
        },
        {
            "id": "018",
            "claim": "Project22 anchor lift masks are exactly recovered by node-sheet selector node >= 15 on the inherited anchor paths.",
            "status": "closed intermediate theorem",
        },
        {
            "id": "023",
            "claim": "Given observed anchor residue sets, observed pair-size profiles, corrected quotient candidate census, and the rank law, the observed anchor paths are selected exactly.",
            "status": "conditional selector theorem",
        },
    ]

    open_frontier = [
        "Derive the anchor residue sets natively rather than inheriting them from Project22.",
        "Derive the pair-size profiles natively rather than inheriting them from observed anchor paths.",
        "Validate or derive the rank law rank = 2 + 7*b + 2*r - b*r from native/provenance fields rather than fitting it to four observed states.",
        "Test station/provenance fields if available.",
        "Select unique relay mediators rather than only covering relay transitions.",
        "Derive the full role-labeled shared_B edge universe.",
        "Only then reconsider Gap A closure."
    ]

    result = {
        "status": "local_cell_provenance_frontier_checkpoint_recorded",
        "audit_id": "024",
        "inputs": {k: str(v) for k, v in INPUTS.items()},
        "checks": checks,
        "checkpoint_pass": all(checks.values()),
        "closed_results": closed_results,
        "open_frontier": open_frontier,
        "summary": (
            "Project24 has moved the local-cell provenance frontier. The C-path side is covered by quotient-anchor support; "
            "the anchor side is quotient-pair supported; lift masks are native sheet labels; and the observed anchor paths "
            "are conditionally selected by a compact bit-rank law inside the candidate universe. The remaining upstream problem "
            "is no longer generic support. It is provenance selection: native derivation of anchor residue sets, pair-size profiles, "
            "and the rank law."
        ),
        "boundary": (
            "This checkpoint does not close Gap A. It records the current frontier and explicitly preserves the remaining "
            "native-provenance obligations."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Local cell provenance frontier checkpoint 024")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Checkpoint result")
    lines.append("")
    lines.append("- checkpoint_pass: `" + str(result["checkpoint_pass"]) + "`")
    lines.append("")
    lines.append("## Closed results")
    lines.append("")
    for item in closed_results:
        lines.append("- " + item["id"] + ": " + item["claim"])
        lines.append("  - status: `" + item["status"] + "`")
    lines.append("")
    lines.append("## Open frontier")
    lines.append("")
    for item in open_frontier:
        lines.append("- " + item)
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(result["summary"])
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(result["boundary"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("checkpoint_pass", result["checkpoint_pass"])
    print("closed_result_count", len(closed_results))
    print("open_frontier_count", len(open_frontier))


if __name__ == "__main__":
    main()
