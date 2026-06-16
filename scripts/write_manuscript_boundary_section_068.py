#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_065 = ROOT / "artifacts/json/skeptic_boundary_checkpoint_065.v1.json"
IN_067 = ROOT / "artifacts/json/local_completion_plateau_boundary_note_067.v1.json"

OUT_JSON = ROOT / "artifacts/json/manuscript_boundary_section_068.v1.json"
OUT_NOTE = ROOT / "notes/manuscript_boundary_section_068.md"
OUT_SECTION = ROOT / "paper/sections/10_local_completion_boundary.tex"

REQUIRED = [
    "local completion grammar",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
    "answer-label leakage remains open",
    "not a cosmic conclusion",
]

FORBIDDEN = [
    "Gap A is closed",
    "native closure achieved",
    "completion ladder proven natively",
    "answer-label leakage ruled out",
    "full shared_B universe derived",
    "the universe has a belly button",
    "cosmology is derived",
    "ontology is proven",
]


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def missing(text, phrases):
    return [p for p in phrases if p not in text]


def found(text, phrases):
    return [p for p in phrases if p in text]


def main():
    if not IN_065.exists():
        raise SystemExit("missing " + str(IN_065))
    if not IN_067.exists():
        raise SystemExit("missing " + str(IN_067))

    a065 = load_json(IN_065)
    a067 = load_json(IN_067)

    if not a065.get("audit_pass"):
        raise SystemExit("065 audit_pass is not true")
    if not a067.get("audit_pass"):
        raise SystemExit("067 audit_pass is not true")

    section_md = """# Local completion boundary

The current evidence supports a local completion grammar, not a cosmic conclusion.

The positive result is bounded but real. In the audited local register, two non-label native fields, slot_delta_mod15 and fiber_delta_mod60, recover the Euclidean order once the four groups are already known. This supports a finite inside/outside reading: outside boundary span rises while inside fiber residual falls. A further transition layer appears when C_delta_mod15 exposes twelve form-pure two-row microcells.

The negative result is equally important. The native four-form partition has not been derived. Delta fields alone do not reconstruct the four six-row forms. Flat row-field cuts did not recover the partition. Simple reciprocal or shared-endpoint incidence did not recover it. Six-component incidence refinement did not recover it. Microcell aggregation did not recover it. The visual 2 x 3 x 4 reading is supported at the count and microcell-distribution level only; no tested native sheet or channel coordinate was found.

Therefore this section records a plateau, not a closure theorem. The local completion grammar is a witness surface for a finite alignment in the artifact family. It is not native closure, not full role-labeled shared_B universe derivation, and not Gap A closure. answer-label leakage remains open.

The next mathematical frontier is the source-construction law for the four-form partition. Until that law is found, the allowed claim is narrow: a local completion grammar survives multiple tests, while the native grouping mechanism remains open.
"""

    section_tex = r"""\section{Local completion boundary}

The current evidence supports a local completion grammar, not a cosmic conclusion.

The positive result is bounded but real. In the audited local register, two non-label native fields, \texttt{slot\_delta\_mod15} and \texttt{fiber\_delta\_mod60}, recover the Euclidean order once the four groups are already known. This supports a finite inside/outside reading: outside boundary span rises while inside fiber residual falls. A further transition layer appears when \texttt{C\_delta\_mod15} exposes twelve form-pure two-row microcells.

The negative result is equally important. The native four-form partition has not been derived. Delta fields alone do not reconstruct the four six-row forms. Flat row-field cuts did not recover the partition. Simple reciprocal or shared-endpoint incidence did not recover it. Six-component incidence refinement did not recover it. Microcell aggregation did not recover it. The visual \(2 \times 3 \times 4\) reading is supported at the count and microcell-distribution level only; no tested native sheet or channel coordinate was found.

Therefore this section records a plateau, not a closure theorem. The local completion grammar is a witness surface for a finite alignment in the artifact family. It is not native closure, not full role-labeled \texttt{shared\_B} universe derivation, and not Gap A closure. answer-label leakage remains open.

The next mathematical frontier is the source-construction law for the four-form partition. Until that law is found, the allowed claim is narrow: a local completion grammar survives multiple tests, while the native grouping mechanism remains open.
"""

    gate_text = section_md
    missing_required = missing(gate_text, REQUIRED)
    forbidden_found = found(gate_text, FORBIDDEN)

    section_pass = len(missing_required) == 0 and len(forbidden_found) == 0

    result = {
        "status": "manuscript_boundary_section_recorded",
        "audit_id": "068",
        "audit_pass": section_pass,
        "verdict": "manuscript_boundary_section_written" if section_pass else "manuscript_boundary_section_phrase_gate_failed",
        "inputs": {
            "skeptic_boundary_checkpoint_065": str(IN_065),
            "local_completion_plateau_boundary_note_067": str(IN_067),
        },
        "outputs": {
            "note_markdown": str(OUT_NOTE),
            "tex_section": str(OUT_SECTION),
        },
        "checks": {
            "input_065_pass": bool(a065.get("audit_pass")),
            "input_067_pass": bool(a067.get("audit_pass")),
            "required_phrases_present": len(missing_required) == 0,
            "forbidden_phrases_absent": len(forbidden_found) == 0,
        },
        "missing_required_phrases": missing_required,
        "forbidden_phrases_found": forbidden_found,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)
    OUT_SECTION.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_NOTE.write_text(section_md + "\n", encoding="utf-8")
    OUT_SECTION.write_text(section_tex + "\n", encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("wrote", OUT_SECTION)
    print("status", result["status"])
    print("audit_pass", section_pass)
    print("verdict", result["verdict"])
    for k, v in result["checks"].items():
        print(k, v)


if __name__ == "__main__":
    main()
