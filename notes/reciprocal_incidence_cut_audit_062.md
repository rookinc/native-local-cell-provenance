# Reciprocal incidence cut audit 062

Status: reciprocal_incidence_cut_audit_recorded

## Result

- audit_pass: `True`
- verdict: `reciprocal_incidence_cut_not_found_in_tested_family`
- inside_outside_boundary_grammar_060_pass: `True`
- boundary_cut_law_061_pass: `True`
- source_json_exists: `True`
- edge_records_found: `True`
- row_count_is_24: `True`
- endpoint_field_count: `10`
- context_field_count: `3`
- relation_candidate_count: `40`
- tested_relation_count: `40`
- all_relations_exclude_form_index_record_order_answer_labels: `True`
- form_index_used_only_for_evaluation: `True`
- exact_incidence_cut_hit_count: `0`
- ordered_exact_incidence_cut_hit_count: `0`
- best_candidate_exists: `True`
- best_candidate_relation: `share_endpoint:from_C|to_C`
- best_candidate_score: `-16`
- best_candidate_purity_total: `16`
- best_candidate_component_count: `6`
- answer_label_leakage_remains_open: `True`
- native_provenance_confirmed: `False`
- required_phrases_present: `True`
- forbidden_phrases_absent: `True`

## Statement

Artifact 062 is a reciprocal incidence cut audit. It tests whether rows belong together because of shared endpoints, reciprocal transitions, or incidence neighborhoods: the nearest neighbor that answers back. form_index is used only for evaluation.

## Available fields

- endpoint_fields: `['from_C', 'to_C', 'from_A', 'to_A', 'from_B', 'to_B', 'from_slot', 'to_slot', 'from_fiber', 'to_fiber']`
- context_fields: `['edge_role', 'slot_delta_mod15', 'fiber_delta_mod60']`

## Best candidate

- relation_name: `share_endpoint:from_C|to_C`
- edge_count: `56`
- component_count: `6`
- purity_total: `16`
- score: `-16`
- exact_partition: `False`
- ordered_exact_by_boundary_gap: `False`
- majority_order_by_boundary_gap: `[0, 1, 1, 1, 2, 3]`

### Best candidate components

- rows=2, forms={0: 2}, majority=0, outside=3, inside=57, gap=-54
- rows=2, forms={1: 2}, majority=1, outside=12, inside=3, gap=9
- rows=2, forms={1: 2}, majority=1, outside=12, inside=48, gap=-36
- rows=2, forms={1: 2}, majority=1, outside=6, inside=9, gap=-3
- rows=8, forms={0: 2, 2: 4, 3: 2}, majority=2, outside=13, inside=2, gap=11
- rows=8, forms={0: 2, 2: 2, 3: 4}, majority=3, outside=14, inside=1, gap=13

## Top candidates

- relation=share_endpoint:from_C|to_C, components=6, purity=16/24, score=-16, exact=False, ordered_exact=False, order=[0, 1, 1, 1, 2, 3]
- relation=share_endpoint:from_fiber|to_fiber, components=6, purity=16/24, score=-16, exact=False, ordered_exact=False, order=[0, 1, 1, 1, 2, 3]
- relation=same_field:derived.C_delta_mod15, components=7, purity=18/24, score=-18, exact=False, ordered_exact=False, order=[2, 0, 0, 1, 1, 2, 3]
- relation=same_field:edge_role, components=6, purity=6/24, score=-18, exact=False, ordered_exact=False, order=[0, 0, 0, 0, 0, 0]
- relation=share_endpoint:from_A|to_A, components=2, purity=12/24, score=-24, exact=False, ordered_exact=False, order=[1, 0]
- relation=share_endpoint:from_B|to_B, components=2, purity=12/24, score=-24, exact=False, ordered_exact=False, order=[1, 0]
- relation=share_endpoint:from_slot|to_slot, components=2, purity=12/24, score=-24, exact=False, ordered_exact=False, order=[1, 0]
- relation=share_endpoint:from_A|to_A|from_B|to_B, components=2, purity=12/24, score=-24, exact=False, ordered_exact=False, order=[1, 0]
- relation=share_endpoint:from_C|to_C|from_slot|to_slot, components=2, purity=12/24, score=-24, exact=False, ordered_exact=False, order=[1, 0]
- relation=same_field:derived.inside_captured_row, components=2, purity=8/24, score=-30, exact=False, ordered_exact=False, order=[0, 2]

## Interpretation

Artifact 062 tests the hypothesis that the missing form cut is relational rather than scalar. It searches shared endpoints, reciprocal transitions, and incidence neighborhoods. The result bounds this tested incidence family but does not settle native provenance.

## Boundary

This is a relational cut audit, not native closure. A hit would be a candidate requiring validation; a miss only bounds the tested incidence family. answer-label leakage remains open, this is not full role-labeled shared_B universe derivation, and is not Gap A closure.
