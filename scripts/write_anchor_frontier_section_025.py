#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_017 = ROOT / "artifacts/json/native_g60_anchor_path_quotient_pair_theorem_017.v1.json"
IN_018 = ROOT / "artifacts/json/native_g60_anchor_lift_mask_sheet_selector_018.v1.json"
IN_023 = ROOT / "artifacts/json/native_g60_anchor_rank_selector_theorem_023.v1.json"
IN_024 = ROOT / "artifacts/json/local_cell_provenance_frontier_checkpoint_024.v1.json"

MAIN = ROOT / "paper/main.tex"
SECTION = ROOT / "paper/sections/09_anchor_quotient_rank_frontier.tex"

OUT_JSON = ROOT / "artifacts/json/anchor_frontier_paper_section_025.v1.json"
OUT_NOTE = ROOT / "notes/anchor_frontier_paper_section_025.md"


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    a017 = load(IN_017)
    a018 = load(IN_018)
    a023 = load(IN_023)
    a024 = load(IN_024)

    if not a017.get("theorem_pass"):
        raise SystemExit("017 theorem_pass is not true")
    if not a018.get("theorem_pass"):
        raise SystemExit("018 theorem_pass is not true")
    if not a023.get("theorem_pass"):
        raise SystemExit("023 theorem_pass is not true")
    if not a024.get("checkpoint_pass"):
        raise SystemExit("024 checkpoint_pass is not true")

    section_text = r"""
\section{Anchor quotient support and rank selector frontier}

The previous section establishes a quotient-anchor cover for the C-side of the inherited Project 22 local cell. We now record the corresponding anchor-side frontier.

First, the anchor paths are not literal walks in the copied canonical G60 edge list. Artifact \texttt{native\_g60\_anchor\_node\_path\_edge\_support\_015} found only 1 supported literal pair-step out of 12. This is a negative result: the anchor paths should not be interpreted as raw G60 pair-walks.

Second, after projection to mod15 residue pairs, the anchor paths become fully supported. Artifact \texttt{native\_g60\_anchor\_path\_quotient\_pair\_theorem\_017} proves that all 12 inherited anchor path steps are supported as quotient-pair steps. Thus the anchor paths are not arbitrary payloads, but quotient-visible structures.

Third, the inherited lift masks have a simple native sheet reading. Artifact \texttt{native\_g60\_anchor\_lift\_mask\_sheet\_selector\_018} proves that the lift mask is exactly recovered by the selector
\[
  \mathrm{lift}(v)=1 \quad\Longleftrightarrow\quad v \ge 15,
\]
equivalently \(\lfloor v/15 \rfloor = 1\). In words, lifted anchor positions are precisely the upper-sheet node labels on the inherited closed anchor paths.

Fourth, artifact \texttt{native\_g60\_anchor\_rank\_selector\_theorem\_023} gives a bounded conditional selector theorem for the observed anchor paths. Given the corrected quotient-pair candidate census, the observed anchor residue sets, the observed pair-size profiles, and the rank law
\[
  \mathrm{rank}=2+7b+2r-br,
\]
the selected support-rank candidate in each state exactly recovers the Project 22 anchor path. The four selected ranks are
\[
  O0\mapsto 2,\quad O1\mapsto 4,\quad B0\mapsto 9,\quad B1\mapsto 10.
\]

This moves the frontier. The remaining problem is no longer generic support. The remaining problem is provenance selection. The anchor residue sets, pair-size profiles, and rank law still need native or station-field derivation. The result above is therefore not a Gap A closure. It is a sharpened upstream target: native provenance must now explain why these quotient-supported anchor paths and this rank law are selected.
""".strip() + "\n"

    SECTION.parent.mkdir(parents=True, exist_ok=True)
    SECTION.write_text(section_text, encoding="utf-8")

    main_text = MAIN.read_text(encoding="utf-8")
    include_line = r"\input{sections/09_anchor_quotient_rank_frontier}"

    if include_line not in main_text:
        markers = [
            r"\input{sections/09_boundary}",
            r"\input{sections/10_boundary}",
            r"\input{sections/99_boundary}",
            r"\input{sections/09_conclusion}",
            r"\input{sections/10_conclusion}",
        ]

        inserted = False
        for marker in markers:
            if marker in main_text:
                main_text = main_text.replace(marker, include_line + "\n" + marker, 1)
                inserted = True
                break

        if not inserted:
            main_text = main_text.replace(r"\end{document}", include_line + "\n\n" + r"\end{document}", 1)

        MAIN.write_text(main_text, encoding="utf-8")

    checks = {
        "artifact_017_theorem_pass": a017.get("theorem_pass") is True,
        "artifact_018_theorem_pass": a018.get("theorem_pass") is True,
        "artifact_023_theorem_pass": a023.get("theorem_pass") is True,
        "artifact_024_checkpoint_pass": a024.get("checkpoint_pass") is True,
        "section_file_written": SECTION.exists(),
        "main_includes_anchor_frontier_section": include_line in MAIN.read_text(encoding="utf-8"),
        "section_mentions_not_gap_a_closure": "not a Gap A closure" in section_text,
        "section_mentions_provenance_selection": "provenance selection" in section_text,
    }

    result = {
        "status": "anchor_frontier_paper_section_recorded",
        "audit_id": "025",
        "section": str(SECTION),
        "main": str(MAIN),
        "checks": checks,
        "section_recorded": all(checks.values()),
        "summary": "Wrote the anchor quotient support and rank selector frontier into the paper.",
        "boundary": "This records the current frontier in the manuscript and preserves the statement that Gap A is not closed.",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    note = []
    note.append("# Anchor frontier paper section 025")
    note.append("")
    note.append("Status: " + result["status"])
    note.append("")
    note.append("## Result")
    note.append("")
    note.append("- section_recorded: `" + str(result["section_recorded"]) + "`")
    note.append("- section: `" + str(SECTION) + "`")
    note.append("")
    note.append("## Checks")
    note.append("")
    for k, v in checks.items():
        note.append("- " + k + ": `" + str(v) + "`")
    note.append("")
    note.append("## Summary")
    note.append("")
    note.append(result["summary"])
    note.append("")
    note.append("## Boundary")
    note.append("")
    note.append(result["boundary"])
    note.append("")

    OUT_NOTE.write_text("\n".join(note), encoding="utf-8")

    print("wrote", SECTION)
    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("section_recorded", result["section_recorded"])


if __name__ == "__main__":
    main()
