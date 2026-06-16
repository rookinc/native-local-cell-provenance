#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUTS = {
    "057": "native_euclidean_ladder_selector_audit_057.v1.json",
    "058": "monotone_selector_independence_audit_058.v1.json",
    "059": "native_delta_partition_reconstruction_059.v1.json",
    "060": "inside_outside_boundary_grammar_audit_060.v1.json",
    "061": "boundary_cut_law_search_061.v1.json",
    "062": "reciprocal_incidence_cut_audit_062.v1.json",
    "063": "six_component_incidence_refinement_audit_063.v1.json",
    "064": "transition_microcell_aggregation_audit_064.v1.json",
    "065": "skeptic_boundary_checkpoint_065.v1.json",
    "066": "two_by_three_by_four_grid_audit_066.v1.json",
    "067": "local_completion_plateau_boundary_note_067.v1.json",
    "068": "manuscript_boundary_section_068.v1.json",
    "069": "wire_boundary_section_into_main_069.v1.json",
    "overleaf_zip": "overleaf_zip_build_001.v1.json",
}

OUT_JSON = ROOT / "artifacts/json/local_completion_grammar_handoff_070.v1.json"
OUT_NOTE = ROOT / "notes/local_completion_grammar_handoff_070.md"

REQUIRED = [
    "local completion grammar",
    "grammar handoff",
    "dependency ledger",
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


def pass_value(data):
    if "checkpoint_pass" in data:
        return bool(data.get("checkpoint_pass"))
    if "audit_pass" in data:
        return bool(data.get("audit_pass"))
    if data.get("status") == "overleaf_zip_build_recorded":
        return True
    return False


def missing(text, phrases):
    return [p for p in phrases if p not in text]


def found(text, phrases):
    return [p for p in phrases if p in text]


def main():
    deps = []
    for audit_id, filename in INPUTS.items():
        path = ROOT / "artifacts/json" / filename
        if not path.exists():
            raise SystemExit("missing dependency " + str(path))
        data = load_json(path)
        deps.append({
            "id": audit_id,
            "path": str(path.relative_to(ROOT)),
            "status": data.get("status"),
            "verdict": data.get("verdict"),
            "pass": pass_value(data),
        })

    grammar = {
        "name": "local_completion_grammar",
        "version": "v1",
        "artifact_id": "070",
        "source_project": "24-native-local-cell-provenance",
        "status": "bounded_handoff",
        "core_statement": (
            "The current evidence supports a local completion grammar, not a cosmic conclusion. "
            "The grammar is finite, local, and dependency-bound. It is not native closure, "
            "not full role-labeled shared_B universe derivation, and not Gap A closure. "
            "answer-label leakage remains open."
        ),
        "grammar_axes": {
            "order_axis": {
                "fields": ["slot_delta_mod15", "fiber_delta_mod60"],
                "support": ["057", "058"],
                "claim": (
                    "Opposite monotones recover the Euclidean order once the four groups are known."
                ),
                "boundary": (
                    "The fields do not themselves derive the four-form partition."
                ),
            },
            "inside_outside_axis": {
                "fields": ["slot_delta_mod15", "fiber_delta_mod60", "boundary_gap"],
                "support": ["060"],
                "claim": (
                    "outside boundary span rises while inside fiber residual falls."
                ),
                "boundary": (
                    "This is a bounded reading of paired finite deltas, not a physical or cosmic claim."
                ),
            },
            "transition_microcell_axis": {
                "fields": ["C_delta_mod15"],
                "support": ["063", "064"],
                "claim": (
                    "C_delta_mod15 exposes twelve form-pure two-row transition microcells."
                ),
                "boundary": (
                    "The twelve microcells did not aggregate into the four Euclidean forms in the tested quotient family."
                ),
            },
            "grid_hint_axis": {
                "shape": "2 x 3 x 4",
                "support": ["066"],
                "claim": (
                    "The visible count-level structure is compatible with two sheets, three channels, and four levels."
                ),
                "boundary": (
                    "No tested native row field supplied the sheet or channel coordinate."
                ),
            },
        },
        "closed_or_locked": [
            {
                "name": "non_label_monotone_order_signal",
                "support": ["057", "058"],
                "summary": "slot_delta_mod15 and fiber_delta_mod60 are non-label fields with opposite monotones recovering level order after grouping.",
            },
            {
                "name": "inside_outside_boundary_reading",
                "support": ["060"],
                "summary": "outside span and inside residual produce a bounded local completion reading.",
            },
            {
                "name": "transition_microcell_layer",
                "support": ["063", "064"],
                "summary": "twelve form-pure two-row C_delta microcells exist, three per level.",
            },
            {
                "name": "manuscript_boundary",
                "support": ["068", "069"],
                "summary": "the local completion boundary section is written and wired into paper/main.tex.",
            },
            {
                "name": "overleaf_bundle",
                "support": ["overleaf_zip"],
                "summary": "the Overleaf zip has been rebuilt with the boundary section included.",
            },
        ],
        "negative_results": [
            {
                "name": "delta_fields_do_not_partition_forms",
                "support": ["059"],
                "summary": "native delta fields alone do not reconstruct the four six-row groups.",
            },
            {
                "name": "flat_row_field_cut_not_found",
                "support": ["061"],
                "summary": "tested flat non-label row-field cuts did not derive the four-form partition.",
            },
            {
                "name": "simple_incidence_cut_not_found",
                "support": ["062"],
                "summary": "tested shared-endpoint and reciprocal incidence relations did not derive the four-form partition.",
            },
            {
                "name": "six_component_refinement_not_found",
                "support": ["063"],
                "summary": "six C-endpoint incidence components did not refine into four forms in the tested family.",
            },
            {
                "name": "microcell_aggregation_not_found",
                "support": ["064"],
                "summary": "tested microcell quotient aggregations did not recover the four Euclidean forms.",
            },
            {
                "name": "two_by_three_by_four_grid_not_confirmed",
                "support": ["066"],
                "summary": "the 2 x 3 x 4 count-level hint was not confirmed by native sheet/channel fields.",
            },
        ],
        "open_frontiers": [
            {
                "name": "native_four_form_partition",
                "question": "What source-construction law groups the 24 edge records into four six-row forms?",
                "status": "open",
            },
            {
                "name": "answer_label_leakage",
                "question": "Can the four-form grouping be derived without form_index, row order, target labels, or downstream answer labels?",
                "status": "open",
            },
            {
                "name": "source_construction_law",
                "question": "Does the grouping law live upstream in construction provenance rather than row-level fields?",
                "status": "open",
            },
            {
                "name": "full_role_labeled_shared_B_universe",
                "question": "Can the local cell be connected back to the full reciprocal WXYZTI answer-pair universe?",
                "status": "open",
            },
            {
                "name": "Gap_A_closure",
                "question": "Can the complete Gap A closure chain be proven after the local provenance bridge is solved?",
                "status": "open",
            },
        ],
        "allowed_claims": [
            "A local completion grammar survives multiple finite audits.",
            "There is a non-label monotone order signal once the four groups are known.",
            "There is a bounded inside/outside reading of paired deltas.",
            "There is a real twelve-microcell transition layer.",
            "The current manuscript includes a boundary section preserving the open problems.",
        ],
        "forbidden_claims": [
            "Do not claim native closure.",
            "Do not claim Gap A closure.",
            "Do not claim native proof of the completion ladder.",
            "Do not claim the answer-label leakage risk is resolved.",
            "Do not claim derivation of the full role-labeled shared_B universe.",
            "Do not claim cosmology, ontology, or a universe-scale navel metaphor.",
        ],
        "next_phase_recommendation": {
            "primary": "source_construction_audit",
            "reason": (
                "Repeated row-field, incidence, refinement, aggregation, and grid-coordinate tests failed. "
                "The missing grouping law is more likely upstream in construction provenance than in flat row features."
            ),
            "secondary": [
                "shuffle_and_ablation_tests",
                "README_plateau_summary",
                "manuscript_cleanup",
            ],
        },
    }

    statement = (
        "Artifact 070 is a grammar handoff JSON with a dependency ledger. "
        "It encapsulates the current local completion grammar, not a cosmic conclusion. "
        "It is not native closure, not full role-labeled shared_B universe derivation, and not Gap A closure. "
        "answer-label leakage remains open."
    )

    gate_text = statement + "\n" + json.dumps(grammar, indent=2, sort_keys=True)
    missing_required = missing(gate_text, REQUIRED)
    forbidden_found = found(gate_text, FORBIDDEN)

    checks = {
        "all_dependencies_exist": True,
        "all_dependencies_pass": all(x["pass"] for x in deps),
        "dependency_ledger_recorded": True,
        "grammar_handoff_recorded": True,
        "native_four_form_partition_proven": False,
        "answer_label_leakage_resolved": False,
        "cosmic_conclusion_allowed": False,
        "required_phrases_present": len(missing_required) == 0,
        "forbidden_phrases_absent": len(forbidden_found) == 0,
    }

    audit_pass = all([
        checks["all_dependencies_exist"],
        checks["all_dependencies_pass"],
        checks["dependency_ledger_recorded"],
        checks["grammar_handoff_recorded"],
        not checks["native_four_form_partition_proven"],
        not checks["answer_label_leakage_resolved"],
        not checks["cosmic_conclusion_allowed"],
        checks["required_phrases_present"],
        checks["forbidden_phrases_absent"],
    ])

    result = {
        "status": "local_completion_grammar_handoff_recorded",
        "audit_id": "070",
        "audit_pass": audit_pass,
        "verdict": "grammar_handoff_ready_for_next_phase" if audit_pass else "grammar_handoff_phrase_gate_failed",
        "statement": statement,
        "dependency_ledger": deps,
        "checks": checks,
        "grammar": grammar,
        "missing_required_phrases": missing_required,
        "forbidden_phrases_found": forbidden_found,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Local completion grammar handoff 070")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append("- audit_pass: `" + str(audit_pass) + "`")
    lines.append("- verdict: `" + result["verdict"] + "`")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("")
    lines.append("## Statement")
    lines.append("")
    lines.append(statement)
    lines.append("")
    lines.append("## Core grammar")
    lines.append("")
    lines.append(grammar["core_statement"])
    lines.append("")
    lines.append("## Axes")
    lines.append("")
    for name, axis in grammar["grammar_axes"].items():
        lines.append("- " + name + ": " + axis["claim"] + " Boundary: " + axis["boundary"])
    lines.append("")
    lines.append("## Open frontiers")
    lines.append("")
    for x in grammar["open_frontiers"]:
        lines.append("- " + x["name"] + ": " + x["question"])
    lines.append("")
    lines.append("## Next phase")
    lines.append("")
    lines.append("- primary: " + grammar["next_phase_recommendation"]["primary"])
    lines.append("- reason: " + grammar["next_phase_recommendation"]["reason"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("audit_pass", audit_pass)
    print("verdict", result["verdict"])
    for k, v in checks.items():
        print(k, v)


if __name__ == "__main__":
    main()
