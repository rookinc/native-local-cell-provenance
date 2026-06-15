#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_024 = ROOT / "artifacts/json/local_cell_provenance_frontier_checkpoint_024.v1.json"
IN_025 = ROOT / "artifacts/json/anchor_frontier_paper_section_025.v1.json"

MAIN = ROOT / "paper/main.tex"
SECTION = ROOT / "paper/sections/09_anchor_quotient_rank_frontier.tex"

OUT_JSON = ROOT / "artifacts/json/anchor_frontier_paper_boundary_audit_026.v1.json"
OUT_NOTE = ROOT / "notes/anchor_frontier_paper_boundary_audit_026.md"


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_first(text, needles):
    hits = []
    for n in needles:
        i = text.find(n)
        if i >= 0:
            hits.append((i, n))
    if not hits:
        return None
    return min(hits)[0]


def main():
    a024 = load(IN_024)
    a025 = load(IN_025)

    main_text = MAIN.read_text(encoding="utf-8")
    section_text = SECTION.read_text(encoding="utf-8")

    anchor_include = r"\input{sections/09_anchor_quotient_rank_frontier}"
    c_cover_include = r"\input{sections/08_c_path_quotient_anchor_cover}"

    boundary_needles = [
        r"\input{sections/09_boundary}",
        r"\input{sections/10_boundary}",
        r"\input{sections/99_boundary}",
        r"\section{Boundary}",
        r"\section{Boundaries}",
    ]

    conclusion_needles = [
        r"\input{sections/09_conclusion}",
        r"\input{sections/10_conclusion}",
        r"\input{sections/99_conclusion}",
        r"\section{Conclusion}",
    ]

    anchor_pos = main_text.find(anchor_include)
    c_cover_pos = main_text.find(c_cover_include)
    boundary_pos = find_first(main_text, boundary_needles)
    conclusion_pos = find_first(main_text, conclusion_needles)

    required_closed_phrases = [
        "not literal walks",
        "fully supported",
        "quotient-pair steps",
        "node-sheet",
        "v \\ge 15",
        "\\mathrm{rank}=2+7b+2r-br",
        "selected support-rank candidate",
        "exactly recovers the Project 22 anchor path",
    ]

    required_boundary_phrases = [
        "not a Gap A closure",
        "provenance selection",
        "anchor residue sets",
        "pair-size profiles",
        "rank law",
        "native or station-field derivation",
    ]

    forbidden_unqualified_phrases = [
        "Gap A is closed",
        "closes Gap A",
        "we have closed Gap A",
        "full role-labeled shared_B edge universe is derived",
        "rank law is native",
        "anchor residue sets are derived",
        "pair-size profiles are derived",
    ]

    missing_closed = [p for p in required_closed_phrases if p not in section_text]
    missing_boundary = [p for p in required_boundary_phrases if p not in section_text]
    forbidden_hits = [p for p in forbidden_unqualified_phrases if p in section_text or p in main_text]

    checks = {
        "frontier_checkpoint_024_pass": a024.get("checkpoint_pass") is True,
        "section_025_recorded": a025.get("section_recorded") is True,
        "main_file_exists": MAIN.exists(),
        "section_file_exists": SECTION.exists(),
        "main_includes_anchor_frontier_section": anchor_pos >= 0,
        "c_cover_section_present": c_cover_pos >= 0,
        "anchor_after_c_cover": c_cover_pos >= 0 and anchor_pos > c_cover_pos,
        "anchor_before_boundary_or_conclusion": (
            anchor_pos >= 0 and (
                (boundary_pos is not None and anchor_pos < boundary_pos)
                or (conclusion_pos is not None and anchor_pos < conclusion_pos)
            )
        ),
        "all_required_closed_phrases_present": not missing_closed,
        "all_required_boundary_phrases_present": not missing_boundary,
        "no_forbidden_unqualified_claims_present": not forbidden_hits,
    }

    result = {
        "status": "anchor_frontier_paper_boundary_audit_recorded",
        "audit_id": "026",
        "inputs": {
            "frontier_checkpoint_024": str(IN_024),
            "anchor_frontier_section_025": str(IN_025),
            "main": str(MAIN),
            "section": str(SECTION),
        },
        "positions": {
            "c_cover_include": c_cover_pos,
            "anchor_include": anchor_pos,
            "boundary_or_none": boundary_pos,
            "conclusion_or_none": conclusion_pos,
        },
        "checks": checks,
        "boundary_pass": all(checks.values()),
        "missing_required_closed_phrases": missing_closed,
        "missing_required_boundary_phrases": missing_boundary,
        "forbidden_hits": forbidden_hits,
        "closed_statement": (
            "The paper now records anchor quotient-pair support, node-sheet lift-mask recovery, "
            "and the bounded rank selector theorem."
        ),
        "open_boundary": (
            "The paper continues to state that Gap A is not closed and that native provenance must still derive "
            "the anchor residue sets, pair-size profiles, and rank law."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Anchor frontier paper boundary audit 026")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- boundary_pass: `" + str(result["boundary_pass"]) + "`")
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
    if missing_closed:
        for p in missing_closed:
            lines.append("- `" + p + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Missing required boundary phrases")
    lines.append("")
    if missing_boundary:
        for p in missing_boundary:
            lines.append("- `" + p + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Forbidden hits")
    lines.append("")
    if forbidden_hits:
        for p in forbidden_hits:
            lines.append("- `" + p + "`")
    else:
        lines.append("- none")
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("boundary_pass", result["boundary_pass"])
    print("missing_closed", len(missing_closed))
    print("missing_boundary", len(missing_boundary))
    print("forbidden_hits", len(forbidden_hits))


if __name__ == "__main__":
    main()
