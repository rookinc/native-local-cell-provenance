#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_012 = ROOT / "artifacts/json/native_g60_c_path_quotient_anchor_cover_012.v1.json"
IN_013 = ROOT / "artifacts/json/c_path_cover_theorem_section_013.v1.json"

MAIN = ROOT / "paper/main.tex"
ABSTRACT = ROOT / "paper/sections/00_abstract.tex"
SECTION = ROOT / "paper/sections/08_c_path_quotient_anchor_cover.tex"
BOUNDARY = ROOT / "paper/sections/06_boundary.tex"
CONCLUSION = ROOT / "paper/sections/07_conclusion.tex"

OUT_JSON = ROOT / "artifacts/json/c_path_cover_paper_boundary_audit_014.v1.json"
OUT_NOTE = ROOT / "notes/c_path_cover_paper_boundary_audit_014.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read(path):
    return path.read_text(encoding="utf-8")


def has_all(text, phrases):
    return {p: (p in text) for p in phrases}


def main():
    a012 = load_json(IN_012)
    a013 = load_json(IN_013)

    main = read(MAIN)
    abstract = read(ABSTRACT)
    section = read(SECTION)
    boundary = read(BOUNDARY)
    conclusion = read(CONCLUSION)

    all_paper_text = "\n".join([main, abstract, section, boundary, conclusion])

    include_cover = r"\input{sections/08_c_path_quotient_anchor_cover}"
    include_boundary = r"\input{sections/06_boundary}"
    include_conclusion = r"\input{sections/07_conclusion}"

    cover_pos = main.find(include_cover)
    boundary_pos = main.find(include_boundary)
    conclusion_pos = main.find(include_conclusion)

    required_closed_phrases = [
        "C-path quotient-anchor cover",
        "Every Project 22 C-path step is covered",
        "direct mod15 G60 residue support",
        "same-state unlifted anchor-path relay support",
        r"12/12\ \text{C-path steps covered}",
        r"6\ \text{direct residue steps}",
        r"6\ \text{unlifted anchor-relay steps}",
        r"0\ \text{uncovered steps}",
        "one completed intermediate cover theorem",
    ]

    required_boundary_phrases = [
        "does not derive the anchor paths or lift masks from native G60 provenance",
        "does not select unique mediators for every relay",
        "does not derive the full role-labeled shared",
        "does not close Gap A",
        "This paper does not claim Gap A closure",
        "does not yet derive the Project 22 local-cell kernel from native G60 provenance",
    ]

    forbidden_unqualified_phrases = [
        "Gap A is closed",
        "Gap A closure is proved",
        "we derive the local cell from native G60 provenance",
        "the local cell is derived from native G60 provenance",
        "unique mediator is selected for every relay",
        "full role-labeled shared_B edge universe is derived",
    ]

    closed_hits = has_all(all_paper_text, required_closed_phrases)
    boundary_hits = has_all(all_paper_text, required_boundary_phrases)
    forbidden_hits = has_all(all_paper_text, forbidden_unqualified_phrases)

    checks = {
        "artifact_012_theorem_pass": bool(a012.get("theorem_pass")),
        "artifact_013_section_recorded": a013.get("status") == "c_path_cover_theorem_section_recorded",
        "main_includes_cover_section": cover_pos >= 0,
        "cover_section_before_boundary_section": cover_pos >= 0 and boundary_pos >= 0 and cover_pos < boundary_pos,
        "cover_section_before_conclusion": cover_pos >= 0 and conclusion_pos >= 0 and cover_pos < conclusion_pos,
        "abstract_updated_for_intermediate_theorem": "one completed intermediate cover theorem" in abstract,
        "cover_section_contains_theorem": "C-path quotient-anchor cover" in section and "Every Project 22 C-path step is covered" in section,
        "cover_section_contains_boundary": "does not close Gap A" in section,
        "boundary_section_still_refuses_gap_a_closure": "This paper does not claim Gap A closure" in boundary,
        "all_required_closed_phrases_present": all(closed_hits.values()),
        "all_required_boundary_phrases_present": all(boundary_hits.values()),
        "no_forbidden_unqualified_claims_present": not any(forbidden_hits.values()),
        "counts_match_012": (
            a012.get("total_c_path_step_count") == 12
            and a012.get("direct_residue_count") == 6
            and a012.get("unlifted_anchor_relay_count") == 6
            and a012.get("uncovered_count") == 0
        ),
    }

    result = {
        "status": "c_path_cover_paper_boundary_audit_recorded",
        "audit_id": "014",
        "inputs": {
            "c_path_cover_012": str(IN_012),
            "section_013": str(IN_013),
            "main": str(MAIN),
            "abstract": str(ABSTRACT),
            "cover_section": str(SECTION),
            "boundary_section": str(BOUNDARY),
            "conclusion": str(CONCLUSION),
        },
        "closed_hits": closed_hits,
        "boundary_hits": boundary_hits,
        "forbidden_hits": forbidden_hits,
        "checks": checks,
        "boundary_pass": all(checks.values()),
        "closed_statement": (
            "The paper now records one completed intermediate theorem: every Project 22 C-path step is covered "
            "by direct mod15 G60 residue support or same-state unlifted anchor-path relay support."
        ),
        "open_boundary": (
            "The paper still does not derive the anchor paths or lift masks from native G60 provenance, does not select "
            "unique mediators for every relay, does not derive the full role-labeled shared_B edge universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    lines.append("# C-path cover paper boundary audit 014")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- boundary_pass: `" + str(result["boundary_pass"]) + "`")
    lines.append("- completed intermediate theorem present: `" + str(checks["cover_section_contains_theorem"]) + "`")
    lines.append("- forbidden unqualified claims absent: `" + str(checks["no_forbidden_unqualified_claims_present"]) + "`")
    lines.append("")
    lines.append("## Closed statement")
    lines.append("")
    lines.append(result["closed_statement"])
    lines.append("")
    lines.append("## Open boundary")
    lines.append("")
    lines.append(result["open_boundary"])
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Missing required closed phrases")
    lines.append("")
    missing_closed = [k for k, v in closed_hits.items() if not v]
    if missing_closed:
        for x in missing_closed:
            lines.append("- `" + x + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Missing required boundary phrases")
    lines.append("")
    missing_boundary = [k for k, v in boundary_hits.items() if not v]
    if missing_boundary:
        for x in missing_boundary:
            lines.append("- `" + x + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Forbidden hits")
    lines.append("")
    found_forbidden = [k for k, v in forbidden_hits.items() if v]
    if found_forbidden:
        for x in found_forbidden:
            lines.append("- `" + x + "`")
    else:
        lines.append("- none")
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("boundary_pass", result["boundary_pass"])
    print("closed theorem present", checks["cover_section_contains_theorem"])
    print("forbidden claims absent", checks["no_forbidden_unqualified_claims_present"])


if __name__ == "__main__":
    main()
