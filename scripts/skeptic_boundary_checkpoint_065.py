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
]

OUT_JSON = ROOT / "artifacts/json/skeptic_boundary_checkpoint_065.v1.json"
OUT_CSV = ROOT / "artifacts/csv/skeptic_boundary_checkpoint_065.v1.csv"
OUT_NOTE = ROOT / "notes/skeptic_boundary_checkpoint_065.md"

REQUIRED_PHRASES = [
    "skeptic boundary checkpoint",
    "local completion grammar",
    "not a cosmic conclusion",
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


def phrase_missing(text, phrases):
    return [p for p in phrases if p not in text]


def phrase_found(text, phrases):
    return [p for p in phrases if p in text]


def main():
    loaded = []
    for audit_id, name in INPUTS:
        path = ROOT / "artifacts/json" / name
        if not path.exists():
            raise SystemExit("missing input: " + str(path))
        data = load_json(path)
        loaded.append({
            "audit_id": audit_id,
            "path": str(path),
            "audit_pass": bool(data.get("audit_pass")),
            "verdict": data.get("verdict"),
        })

    loaded_by_id = {x["audit_id"]: x for x in loaded}

    proved_or_locked = [
        {
            "item": "non_label_monotone_order_signal",
            "support": "057 and 058",
            "statement": "slot_delta_mod15 and fiber_delta_mod60 are non-label edge-record fields whose opposite monotones recover the Euclidean order once the four groups are known.",
        },
        {
            "item": "inside_outside_boundary_reading",
            "support": "060",
            "statement": "outside boundary span rises while inside fiber residual falls; boundary_gap orders edge, hinge, closed_face, filled_cell.",
        },
        {
            "item": "transition_microcell_layer",
            "support": "063 and 064",
            "statement": "C_delta_mod15 exposes 12 form-pure two-row transition microcells.",
        },
    ]

    negative_or_bounded = [
        {
            "item": "delta_fields_do_not_partition_forms",
            "support": "059",
            "statement": "native delta fields alone do not reconstruct the four six-row form groups exactly.",
        },
        {
            "item": "flat_row_field_cut_not_found",
            "support": "061",
            "statement": "2,951 tested flat non-label row-field combinations did not cut the 24 rows into the four forms.",
        },
        {
            "item": "simple_incidence_cut_not_found",
            "support": "062",
            "statement": "40 tested shared-endpoint/reciprocal incidence relations did not yield the four-form cut.",
        },
        {
            "item": "six_component_refinement_not_found",
            "support": "063",
            "statement": "the six C-endpoint incidence components could not be refined into four forms by the tested second-field family.",
        },
        {
            "item": "microcell_aggregation_not_found",
            "support": "064",
            "statement": "20,910 tested microcell quotient aggregations did not recover the four Euclidean forms.",
        },
    ]

    interpretations_allowed = [
        "The current evidence supports a local completion grammar, not a cosmic conclusion.",
        "Inside/outside is a useful bounded reading of paired finite deltas.",
        "The microcell layer is a real local alignment in the artifact family.",
        "The missing proof is still the native four-form partition or source-construction law.",
    ]

    forbidden_claims = [
        "Do not claim Gap A closure.",
        "Do not claim native closure.",
        "Do not claim native proof of the completion ladder.",
        "Do not claim the answer-label leakage risk is resolved.",
        "Do not claim derivation of the full role-labeled shared_B universe.",
        "Do not claim cosmology, ontology, or any universe-scale navel metaphor.",
    ]

    next_allowed_targets = [
        {
            "target": "source_construction_audit",
            "reason": "the failed cut searches suggest the missing grouping law may be in the upstream construction process rather than row fields.",
        },
        {
            "target": "manuscript_boundary_section",
            "reason": "the project needs a clean written boundary before more searches.",
        },
        {
            "target": "falsification_tests",
            "reason": "shuffle/ablation tests can tell whether the monotone and microcell signals survive without form labels.",
        },
    ]

    checkpoint_statement = (
        "Artifact 065 is a skeptic boundary checkpoint. The current evidence supports a local completion grammar, not a cosmic conclusion. "
        "The surviving results are finite local alignments, while the native four-form partition remains unproved. "
        "This is not native closure, not full role-labeled shared_B universe derivation, and not Gap A closure. "
        "answer-label leakage remains open."
    )

    combined = checkpoint_statement + "\n" + "\n".join(forbidden_claims)
    missing = phrase_missing(combined, REQUIRED_PHRASES)
    forbidden_found = phrase_found(combined, FORBIDDEN_PHRASES)

    checks = {
        "all_inputs_exist": True,
        "all_inputs_pass": all(x["audit_pass"] for x in loaded),
        "audit_057_locked": loaded_by_id["057"]["audit_pass"],
        "audit_058_locked": loaded_by_id["058"]["audit_pass"],
        "audit_059_locked": loaded_by_id["059"]["audit_pass"],
        "audit_060_locked": loaded_by_id["060"]["audit_pass"],
        "audit_061_locked": loaded_by_id["061"]["audit_pass"],
        "audit_062_locked": loaded_by_id["062"]["audit_pass"],
        "audit_063_locked": loaded_by_id["063"]["audit_pass"],
        "audit_064_locked": loaded_by_id["064"]["audit_pass"],
        "native_four_form_partition_proven": False,
        "answer_label_leakage_resolved": False,
        "cosmic_conclusion_allowed": False,
        "required_phrases_present": len(missing) == 0,
        "forbidden_phrases_absent": len(forbidden_found) == 0,
    }

    checkpoint_pass = all([
        checks["all_inputs_exist"],
        checks["all_inputs_pass"],
        not checks["native_four_form_partition_proven"],
        not checks["answer_label_leakage_resolved"],
        not checks["cosmic_conclusion_allowed"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "skeptic_boundary_checkpoint_recorded",
        "audit_id": "065",
        "checkpoint_pass": checkpoint_pass,
        "audit_pass": checkpoint_pass,
        "verdict": "local_completion_grammar_not_cosmic_conclusion",
        "inputs": loaded,
        "checks": checks,
        "proved_or_locked": proved_or_locked,
        "negative_or_bounded": negative_or_bounded,
        "interpretations_allowed": interpretations_allowed,
        "forbidden_claims": forbidden_claims,
        "next_allowed_targets": next_allowed_targets,
        "checkpoint_statement": checkpoint_statement,
        "missing_required_phrases": missing,
        "forbidden_phrases_found": forbidden_found,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["class", "item", "support", "statement"])
        for x in proved_or_locked:
            w.writerow(["proved_or_locked", x["item"], x["support"], x["statement"]])
        for x in negative_or_bounded:
            w.writerow(["negative_or_bounded", x["item"], x["support"], x["statement"]])
        for x in next_allowed_targets:
            w.writerow(["next_allowed_target", x["target"], "", x["reason"]])

    lines = []
    lines.append("# Skeptic boundary checkpoint 065")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- checkpoint_pass: `" + str(checkpoint_pass) + "`")
    lines.append("- verdict: `" + result["verdict"] + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Checkpoint statement")
    lines.append("")
    lines.append(checkpoint_statement)
    lines.append("")
    lines.append("## Proved or locked")
    lines.append("")
    for x in proved_or_locked:
        lines.append("- " + x["item"] + " (" + x["support"] + "): " + x["statement"])
    lines.append("")
    lines.append("## Negative or bounded")
    lines.append("")
    for x in negative_or_bounded:
        lines.append("- " + x["item"] + " (" + x["support"] + "): " + x["statement"])
    lines.append("")
    lines.append("## Interpretations allowed")
    lines.append("")
    for x in interpretations_allowed:
        lines.append("- " + x)
    lines.append("")
    lines.append("## Forbidden claims")
    lines.append("")
    for x in forbidden_claims:
        lines.append("- " + x)
    lines.append("")
    lines.append("## Next allowed targets")
    lines.append("")
    for x in next_allowed_targets:
        lines.append("- " + x["target"] + ": " + x["reason"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("checkpoint_pass", checkpoint_pass)
    print("verdict", result["verdict"])
    for k, v in checks.items():
        print(k, v)


if __name__ == "__main__":
    main()
