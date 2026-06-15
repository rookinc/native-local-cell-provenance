#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_012 = ROOT / "artifacts/json/native_g60_c_path_quotient_anchor_cover_012.v1.json"

MAIN = ROOT / "paper/main.tex"
SECTION = ROOT / "paper/sections/08_c_path_quotient_anchor_cover.tex"

OUT_JSON = ROOT / "artifacts/json/c_path_cover_theorem_section_013.v1.json"
OUT_NOTE = ROOT / "notes/c_path_cover_theorem_section_013.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote", path)


def main():
    a012 = load_json(IN_012)

    if not a012.get("theorem_pass"):
        raise SystemExit("012 theorem_pass is not true")

    coverage = a012["coverage_by_state"]

    table_lines = []
    for state in ["O0", "O1", "B0", "B1"]:
        for r in coverage[state]:
            table_lines.append(
                f"{state} & {r['step']} & {r['from_c']}\\to {r['to_c']} & "
                f"\\texttt{{{r['support_class']}}} \\\\"
            )

    section = r"""\section{C-Path Quotient-Anchor Cover}

The first native-provenance tests show that the Project 22 C paths are not literal paths in the canonical G60 local edge payload.  Artifact 003 found zero literal G60 adjacency support for the twelve C-path steps.

The next audits show that this is not a failure of structure.  Artifact 004 found partial support after projecting native G60 vertices to residues modulo 15.  Artifact 006 proved that the direct residue-support pattern is exactly controlled by the local shell/rank bits.  Artifacts 007--011 then showed that every unsupported direct residue transition is repaired by a same-state unlifted anchor-path relay.

\begin{theorem}[C-path quotient-anchor cover]
Every Project 22 C-path step is covered by one of two mechanisms:
\[
    \text{direct mod15 G60 residue support}
\]
or
\[
    \text{same-state unlifted anchor-path relay support}.
\]
The direct half is selected by the bit/step law from artifact 006.  The complementary relay half is covered by artifact 011.  Therefore all twelve C-path steps are covered.
\end{theorem}

\paragraph{Coverage table.}
\[
\begin{array}{c|c|c|c}
\mathrm{state} & \mathrm{step} & C\ \mathrm{transition} & \mathrm{support}\\
\hline
""" + "\n".join(table_lines) + r"""
\end{array}
\]

Artifact 012 verifies the combined theorem:
\[
    12/12\ \text{C-path steps covered}.
\]
The split is exact:
\[
    6\ \text{direct residue steps}
    \quad+\quad
    6\ \text{unlifted anchor-relay steps}
    \quad+\quad
    0\ \text{uncovered steps}.
\]

\paragraph{Boundary.}
This is a C-path cover theorem over the mod15 residue quotient plus inherited Project 22 anchor paths and lift masks.  It does not derive the anchor paths or lift masks from native G60 provenance.  It does not select unique mediators for every relay.  It does not derive the full role-labeled shared\_B edge universe, and it does not close Gap A.
"""

    write(SECTION, section)

    include_line = r"\input{sections/08_c_path_quotient_anchor_cover}"
    main = MAIN.read_text(encoding="utf-8")

    if include_line not in main:
        anchor = r"\input{sections/06_boundary}"
        if anchor in main:
            main = main.replace(anchor, include_line + "\n" + anchor)
        else:
            main = main.replace(r"\input{sections/07_conclusion}", include_line + "\n" + r"\input{sections/07_conclusion}")
        write(MAIN, main)
    else:
        print("main already includes section 08")

    result = {
        "status": "c_path_cover_theorem_section_recorded",
        "audit_id": "013",
        "input": str(IN_012),
        "section": str(SECTION),
        "main": str(MAIN),
        "theorem_012_pass": bool(a012.get("theorem_pass")),
        "total_c_path_step_count": a012.get("total_c_path_step_count"),
        "direct_residue_count": a012.get("direct_residue_count"),
        "unlifted_anchor_relay_count": a012.get("unlifted_anchor_relay_count"),
        "uncovered_count": a012.get("uncovered_count"),
        "claim": "Wrote the C-path quotient-anchor cover theorem into the paper.",
        "boundary": "The theorem covers C paths but does not derive anchor paths or lift masks from native G60 provenance and does not close Gap A.",
    }

    write(OUT_JSON, json.dumps(result, indent=2, sort_keys=True) + "\n")

    note = """# C-path cover theorem section 013

Status: c_path_cover_theorem_section_recorded

## Claim

Wrote the C-path quotient-anchor cover theorem into the paper.

Artifact 012 verifies:

- 12/12 C-path steps covered
- 6 direct mod15 G60 residue steps
- 6 same-state unlifted anchor-path relay steps
- 0 uncovered steps

## Boundary

The theorem covers the Project 22 C paths using the mod15 residue quotient plus inherited Project 22 anchor paths and lift masks. It does not derive the anchor paths or lift masks from native G60 provenance, does not select unique mediators for every relay, does not derive the full role-labeled shared_B edge universe, and does not close Gap A.
"""
    write(OUT_NOTE, note)

    print("status", result["status"])
    print("total_c_path_step_count", result["total_c_path_step_count"])
    print("direct_residue_count", result["direct_residue_count"])
    print("unlifted_anchor_relay_count", result["unlifted_anchor_relay_count"])
    print("uncovered_count", result["uncovered_count"])


if __name__ == "__main__":
    main()
