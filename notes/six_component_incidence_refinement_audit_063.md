# Six-component incidence refinement audit 063

Status: six_component_incidence_refinement_audit_recorded

## Result

- audit_pass: `True`
- verdict: `six_component_refinement_not_found_in_tested_family`
- inside_outside_boundary_grammar_060_pass: `True`
- reciprocal_incidence_cut_062_pass: `True`
- source_json_exists: `True`
- edge_records_found: `True`
- row_count_is_24: `True`
- base_relation: `share_endpoint:from_C|to_C`
- base_component_count_is_6: `True`
- base_component_sizes: `[2, 2, 2, 2, 8, 8]`
- base_purity_total: `16`
- merge_only_reconstruction_possible: `False`
- candidate_field_count: `17`
- tested_refinement_count: `34`
- all_refinements_exclude_form_index_record_order_answer_labels: `True`
- form_index_used_only_for_evaluation: `True`
- exact_refinement_hit_count: `0`
- ordered_exact_refinement_hit_count: `0`
- best_refinement_exists: `True`
- best_refinement_family: `component_plus_field_partition`
- best_refinement_field: `from_C`
- best_refinement_component_count: `9`
- best_refinement_purity_total: `18`
- best_refinement_score: `-42`
- best_split_field: `derived.C_delta_mod15`
- best_split_purity_total: `24`
- answer_label_leakage_remains_open: `True`
- native_provenance_confirmed: `False`
- required_phrases_present: `True`
- forbidden_phrases_absent: `True`

## Statement

Artifact 063 is a six-component incidence refinement audit. It starts from the six incidence components found by 062 and tests whether a second native field can refine them into the four Euclidean forms. form_index is used only for evaluation.

## Base six incidence components

- component 0: rows=2, forms={0: 2}, majority=0, outside=3, inside=57, gap=-54, too_large=False
- component 1: rows=2, forms={1: 2}, majority=1, outside=12, inside=3, gap=9, too_large=False
- component 2: rows=2, forms={1: 2}, majority=1, outside=12, inside=48, gap=-36, too_large=False
- component 3: rows=2, forms={1: 2}, majority=1, outside=6, inside=9, gap=-3, too_large=False
- component 4: rows=8, forms={0: 2, 2: 4, 3: 2}, majority=2, outside=13, inside=2, gap=11, too_large=True
- component 5: rows=8, forms={0: 2, 2: 2, 3: 4}, majority=3, outside=14, inside=1, gap=13, too_large=True

## Best refinement

- family: `component_plus_field_partition`
- field: `from_C`
- component_count: `9`
- purity_total: `18`
- score: `-42`
- exact_partition: `False`
- ordered_exact_by_boundary_gap: `False`
- majority_order_by_boundary_gap: `[0, 2, 0, 1, 1, 1, 0, 2, 3]`

## Best component split purity

- field: `derived.C_delta_mod15`
- split_count: `12`
- split_purity_total: `24`

## Top refinements

- family=component_plus_field_partition, field=from_C, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 0, 1, 1, 1, 0, 2, 3]
- family=component_plus_field_partition, field=from_fiber, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 0, 1, 1, 1, 0, 2, 3]
- family=component_plus_field_partition, field=to_C, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 1, 0, 1, 1, 0, 3, 2]
- family=component_plus_field_partition, field=to_fiber, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 1, 0, 1, 1, 0, 3, 2]
- family=field_gated_C_endpoint_incidence, field=from_C, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 0, 1, 1, 1, 2, 0, 3]
- family=field_gated_C_endpoint_incidence, field=from_fiber, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 0, 1, 1, 1, 2, 0, 3]
- family=field_gated_C_endpoint_incidence, field=to_C, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 1, 0, 1, 1, 3, 0, 2]
- family=field_gated_C_endpoint_incidence, field=to_fiber, components=9, purity=18/24, score=-42, exact=False, ordered_exact=False, order=[0, 2, 1, 0, 1, 1, 3, 0, 2]
- family=component_plus_field_partition, field=derived.inside_captured_row, components=9, purity=16/24, score=-46, exact=False, ordered_exact=False, order=[0, 1, 1, 1, 0, 2, 1, 2, 3]
- family=field_gated_C_endpoint_incidence, field=derived.inside_captured_row, components=9, purity=16/24, score=-46, exact=False, ordered_exact=False, order=[0, 1, 1, 1, 0, 2, 1, 2, 3]

## Interpretation

The base C-endpoint incidence relation finds six incidence components. merge-only reconstruction is impossible when any component is larger than six rows, so the tested frontier is a refinement family: split large incidence components or gate incidence by a second native field.

## Boundary

This is a refinement audit, not native closure. A hit would be a candidate requiring validation; a miss only bounds the tested refinement family. answer-label leakage remains open, this is not full role-labeled shared_B universe derivation, and is not Gap A closure.
