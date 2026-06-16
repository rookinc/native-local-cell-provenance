#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUTS = [
    ("057", "native_euclidean_ladder_selector_audit_057.v1.json"),
    ("058", "monotone_selector_independence_audit_058.v1.json"),
    ("059", "native_delta_partition_reconstruction_059.v1.json"),
    ("060", "inside_outside_boundary_grammar_audit_060.v1.json"),
    ("061", "boundary_cut_law_search_061.v1.json"),
    ("062", "reciprocal_incidence_cut_audit_062.v1.json"),
    ("063", "six_component_incidence_refinement_audit_063.v1.json"),
    ("064", "transition_microcell_aggregation_audit_064.v1.json"),
    ("065", "skeptic_boundary_checkpoint_065.v1.json"),
    ("066", "two_by_three_by_four_grid_audit_066.v1.json"),
]

OUT_JSON = ROOT / "artifacts/json/local_completion_plateau_boundary_note_067.v1.json"
OUT_CSV = ROOT / "artifacts/csv/local_completion_plateau_boundary_note_067.v1.csv"
OUT_NOTE = ROOT / "notes/local_completion_plateau_boundary_note_067.md"

REQUIRED_PHRASES = [
    "local completion plateau",
    "local completion grammar",
    "not native closure",
    "not Gap A closure",
    "not full role-labeled shared_B universe",
    "answer-label leakage remains open",
    "not a cosmic conclusion",
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


def pass_key(data):
    if "checkpoint_pass" in data:
        return bool(data.get("checkpoint_pass"))
    return bool(data.get("audit_pass"))


def main():
    inputs = []
    for audit_id, filename in INPUTS:
        path = ROOT / "artifacts/json" / filename
        if not path.exists():
            raise SystemExit("missing input " + str(path))
        data = load_json(path)
        inputs.append({
            "audit_id": audit_id,
            "path": str(path),
            "pass": pass_key(data),
            "verdict": data.get("verdict"),
        })

    locked_support = [
        {
            "name": "monotone order signal",
            "support": "057, 058",
            "claim": "slot_delta_mod15 and fiber_delta_mod60 recover the Euclidean order once the four groups are already known.",
        },
        {
            "name": "inside/outside reading",
            "support": "060",
            "claim": "outside boundary span rises while inside fiber residual falls, giving a bounded local completion grammar.",
        },
        {
            "name": "transition microcell layer",
            "support": "063, 064",
            "claim": "C_delta_mod15 exposes 12 form-pure two-row transition microcells.",
        },
        {
            "name": "count-level grid hint",
            "support": "066",
            "claim": "24 rows can be visually read as 2 x 3 x 4 at the count level, but native sheet and channel coordinates were not found.",
        },
    ]

    negative_results = [
        {
            "name": "delta partition failure",
            "support": "059",
            "claim": "native delta fields alone do not reconstruct the four six-row forms.",
        },
        {
            "name": "flat cut failure",
            "support": "061",
            "claim": "2,951 flat row-field cuts did not derive the four-form partition.",
        },
        {
            "name": "incidence cut failure",
            "support": "062",
            "claim": "40 reciprocal or shared-endpoint incidence cuts did not derive the four-form partition.",
        },
        {
            "name": "refinement failure",
            "support": "063",
            "claim": "six C-endpoint incidence components did not refine into the four forms in the tested family.",
        },
        {
            "name": "microcell aggregation failure",
            "support": "064",
            "claim": "20,910 tested microcell quotient aggregations did not recover the four forms.",
        },
        {
            "name": "grid coordinate failure",
            "support": "066",
            "claim": "no tested native row field supplied the two-sheet or three-channel coordinate.",
        },
    ]

    allowed_language = [
        "local completion grammar",
        "bounded inside/outside reading",
        "finite local alignment",
        "transition microcell layer",
        "open native four-form partition",
        "source-construction frontier",
    ]

    disallowed_language = [
        "Gap A closure",
        "native closure",
        "native proof of the completion ladder",
        "resolved answer-label leakage",
        "derivation of the full role-labeled shared_B universe",
        "cosmology or ontology conclusion",
        "universe-scale navel metaphor",
    ]

    next_work = [
        {
            "target": "source construction audit",
            "reason": "the missing grouping law may live upstream in the source construction rather than in row fields.",
        },
        {
            "target": "manuscript boundary section",
            "reason": "the project needs a human-readable boundary before more searches.",
        },
        {
            "target": "shuffle and ablation tests",
            "reason": "the monotone and microcell signals should be tested against label shuffles and source perturbations.",
        },
    ]

    plateau_statement = (
        "Artifact 067 records the local completion plateau. The current evidence supports a local completion grammar, not a cosmic conclusion. "
        "The strongest positive signals are a non-label monotone order, a bounded inside/outside reading, and a 12-cell transition microcell layer. "
        "The repeated negative results show that the native four-form partition has not been derived. "
        "This is not native closure, not full role-labeled shared_B universe derivation, and not Gap A closure. "
        "answer-label leakage remains open."
    )

    text_for_gate = plateau_statement + "\n" + "\n".join(allowed_language) + "\n" + "\n".join(disallowed_language)
    missing_required = missing(text_for_gate, REQUIRED_PHRASES)
    forbidden_found = found(text_for_gate, FORBIDDEN_PHRASES)

    checks = {
        "all_inputs_exist": True,
        "all_inputs_pass": all(x["pass"] for x in inputs),
        "local_completion_plateau_recorded": True,
        "native_four_form_partition_proven": False,
        "answer_label_leakage_resolved": False,
        "cosmic_conclusion_allowed": False,
        "required_phrases_present": len(missing_required) == 0,
        "forbidden_phrases_absent": len(forbidden_found) == 0,
    }

    artifact_pass = all([
        checks["all_inputs_exist"],
        checks["all_inputs_pass"],
        checks["local_completion_plateau_recorded"],
        not checks["native_four_form_partition_proven"],
        not checks["answer_label_leakage_resolved"],
        not checks["cosmic_conclusion_allowed"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "local_completion_plateau_boundary_note_recorded",
        "audit_id": "067",
        "audit_pass": artifact_pass,
        "verdict": "local_completion_plateau_recorded_without_closure",
        "inputs": inputs,
        "checks": checks,
        "locked_support": locked_support,
        "negative_results": negative_results,
        "allowed_language": allowed_language,
        "disallowed_language": disallowed_language,
        "next_work": next_work,
        "plateau_statement": plateau_statement,
        "missing_required_phrases": missing_required,
        "forbidden_phrases_found": forbidden_found,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "name", "support", "claim_or_reason"])
        for x in locked_support:
            w.writerow(["locked_support", x["name"], x["support"], x["claim"]])
        for x in negative_results:
            w.writerow(["negative_result", x["name"], x["support"], x["claim"]])
        for x in next_work:
            w.writerow(["next_work", x["target"], "", x["reason"]])

    lines = []
    lines.append("# Local completion plateau boundary note 067")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(artifact_pass) + "`")
    lines.append("- verdict: `" + result["verdict"] + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Plateau statement")
    lines.append("")
    lines.append(plateau_statement)
    lines.append("")
    lines.append("## Locked support")
    lines.append("")
    for x in locked_support:
        lines.append("- " + x["name"] + " (" + x["support"] + "): " + x["claim"])
    lines.append("")
    lines.append("## Negative results")
    lines.append("")
    for x in negative_results:
        lines.append("- " + x["name"] + " (" + x["support"] + "): " + x["claim"])
    lines.append("")
    lines.append("## Allowed language")
    lines.append("")
    for x in allowed_language:
        lines.append("- " + x)
    lines.append("")
    lines.append("## Disallowed language")
    lines.append("")
    for x in disallowed_language:
        lines.append("- " + x)
    lines.append("")
    lines.append("## Next work")
    lines.append("")
    for x in next_work:
        lines.append("- " + x["target"] + ": " + x["reason"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("audit_pass", artifact_pass)
    print("verdict", result["verdict"])
    for k, v in checks.items():
        print(k, v)


if __name__ == "__main__":
    main()
