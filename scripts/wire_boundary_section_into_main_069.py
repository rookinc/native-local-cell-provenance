#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAIN = ROOT / "paper/main.tex"
SECTION = ROOT / "paper/sections/10_local_completion_boundary.tex"

IN_068 = ROOT / "artifacts/json/manuscript_boundary_section_068.v1.json"

OUT_JSON = ROOT / "artifacts/json/wire_boundary_section_into_main_069.v1.json"
OUT_NOTE = ROOT / "notes/wire_boundary_section_into_main_069.md"

TOKEN = r"\input{sections/10_local_completion_boundary}"

ANCHORS = [
    r"\printbibliography",
    r"\bibliographystyle",
    r"\bibliography",
    r"\appendix",
    r"\end{document}",
]

REQUIRED_PHRASES = [
    "local completion boundary",
    "wired into main.tex",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
    "answer-label leakage remains open",
]

FORBIDDEN_PHRASES = [
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


def insert_before_anchor(text, token):
    if token in text:
        return text, False, "already_present"

    for anchor in ANCHORS:
        pos = text.find(anchor)
        if pos >= 0:
            before = text[:pos].rstrip()
            after = text[pos:].lstrip()
            new_text = before + "\n\n" + token + "\n\n" + after
            return new_text, True, anchor

    new_text = text.rstrip() + "\n\n" + token + "\n"
    return new_text, True, "end_of_file"


def main():
    if not IN_068.exists():
        raise SystemExit("missing " + str(IN_068))
    if not MAIN.exists():
        raise SystemExit("missing " + str(MAIN))
    if not SECTION.exists():
        raise SystemExit("missing " + str(SECTION))

    a068 = load_json(IN_068)
    if not a068.get("audit_pass"):
        raise SystemExit("068 audit_pass is not true")

    old_main = MAIN.read_text(encoding="utf-8")
    section_text = SECTION.read_text(encoding="utf-8")

    new_main, inserted, insertion_anchor = insert_before_anchor(old_main, TOKEN)

    if new_main != old_main:
        MAIN.write_text(new_main, encoding="utf-8")

    statement = (
        "Artifact 069 records that the local completion boundary section has been wired into main.tex. "
        "This is a manuscript assembly step, not native closure, not full role-labeled shared_B universe derivation, and not Gap A closure. "
        "answer-label leakage remains open."
    )

    note_text = (
        "# Wire boundary section into main 069\n\n"
        "Status: boundary_section_wired_into_main\n\n"
        "## Result\n\n"
        "- main_tex: `" + str(MAIN.relative_to(ROOT)) + "`\n"
        "- section_tex: `" + str(SECTION.relative_to(ROOT)) + "`\n"
        "- token: `" + TOKEN + "`\n"
        "- inserted: `" + str(inserted) + "`\n"
        "- insertion_anchor: `" + insertion_anchor + "`\n\n"
        "## Statement\n\n"
        + statement + "\n\n"
        "## Boundary\n\n"
        "This only wires the local completion boundary section into the manuscript. It does not upgrade the claim. "
        "The section remains a boundary statement: local completion grammar, not a cosmic conclusion.\n"
    )

    gate_text = statement + "\n" + note_text + "\n" + section_text
    missing_required = missing(gate_text, REQUIRED_PHRASES)
    forbidden_found = found(gate_text, FORBIDDEN_PHRASES)

    checks = {
        "input_068_pass": bool(a068.get("audit_pass")),
        "main_exists": MAIN.exists(),
        "section_exists": SECTION.exists(),
        "token_present_after": TOKEN in MAIN.read_text(encoding="utf-8"),
        "section_contains_boundary_language": "not Gap A closure" in section_text and "answer-label leakage remains open" in section_text,
        "required_phrases_present": len(missing_required) == 0,
        "forbidden_phrases_absent": len(forbidden_found) == 0,
    }

    audit_pass = all(checks.values())

    result = {
        "status": "boundary_section_wired_into_main",
        "audit_id": "069",
        "audit_pass": audit_pass,
        "verdict": "boundary_section_wired_into_main_tex" if audit_pass else "boundary_section_wire_failed",
        "inputs": {
            "manuscript_boundary_section_068": str(IN_068),
            "main_tex": str(MAIN),
            "section_tex": str(SECTION),
        },
        "outputs": {
            "main_tex": str(MAIN),
            "json": str(OUT_JSON),
            "note": str(OUT_NOTE),
        },
        "inserted": inserted,
        "insertion_anchor": insertion_anchor,
        "token": TOKEN,
        "checks": checks,
        "missing_required_phrases": missing_required,
        "forbidden_phrases_found": forbidden_found,
        "statement": statement,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_NOTE.write_text(note_text, encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("updated", MAIN)
    print("status", result["status"])
    print("audit_pass", audit_pass)
    print("verdict", result["verdict"])
    print("inserted", inserted)
    print("insertion_anchor", insertion_anchor)
    for k, v in checks.items():
        print(k, v)


if __name__ == "__main__":
    main()
