# Transition microcell aggregation audit 064

Status: transition_microcell_aggregation_audit_recorded

## Result

- audit_pass: `True`
- verdict: `transition_microcell_aggregation_not_found_in_tested_family`
- inside_outside_boundary_grammar_060_pass: `True`
- six_component_refinement_063_pass: `True`
- source_json_exists: `True`
- edge_records_found: `True`
- row_count_is_24: `True`
- base_component_count: `6`
- microcell_count_is_12: `True`
- all_microcells_are_form_pure: `True`
- all_microcells_have_two_rows: `True`
- form_index_used_only_for_evaluation: `True`
- microcell_feature_count: `204`
- aggregation_candidate_count: `20910`
- exact_aggregation_hit_count: `0`
- ordered_exact_aggregation_hit_count: `0`
- best_candidate_exists: `True`
- best_candidate_key: `C_delta_mod15_mod_2|C_delta_mod15_mod_4`
- best_candidate_group_count: `4`
- best_candidate_purity_total: `14`
- best_candidate_score: `10`
- answer_label_leakage_remains_open: `True`
- native_provenance_confirmed: `False`
- required_phrases_present: `True`
- forbidden_phrases_absent: `True`

## Statement

Artifact 064 is a transition microcell aggregation audit. It starts from the 12 pure transition cells exposed by C_delta_mod15 in 063 and searches for a native quotient law that aggregates them into the four Euclidean forms. form_index is used only for evaluation.

## Microcells

- microcell 0: base=0, C_delta=12, rows=2, forms={0: 2}, pure=True, outside=3, inside=57, gap=-54
- microcell 1: base=1, C_delta=3, rows=2, forms={1: 2}, pure=True, outside=12, inside=3, gap=9
- microcell 2: base=2, C_delta=3, rows=2, forms={1: 2}, pure=True, outside=12, inside=48, gap=-36
- microcell 3: base=3, C_delta=9, rows=2, forms={1: 2}, pure=True, outside=6, inside=9, gap=-3
- microcell 4: base=4, C_delta=10, rows=2, forms={2: 2}, pure=True, outside=5, inside=55, gap=-50
- microcell 5: base=4, C_delta=12, rows=2, forms={3: 2}, pure=True, outside=3, inside=57, gap=-54
- microcell 6: base=4, C_delta=2, rows=2, forms={2: 2}, pure=True, outside=13, inside=2, gap=11
- microcell 7: base=4, C_delta=6, rows=2, forms={0: 2}, pure=True, outside=9, inside=51, gap=-42
- microcell 8: base=5, C_delta=1, rows=2, forms={3: 2}, pure=True, outside=14, inside=1, gap=13
- microcell 9: base=5, C_delta=12, rows=2, forms={0: 2}, pure=True, outside=3, inside=12, gap=-9
- microcell 10: base=5, C_delta=2, rows=2, forms={3: 2}, pure=True, outside=13, inside=2, gap=11
- microcell 11: base=5, C_delta=3, rows=2, forms={2: 2}, pure=True, outside=12, inside=3, gap=9

## Best aggregation candidate

- key_name: `C_delta_mod15_mod_2|C_delta_mod15_mod_4`
- group_count: `4`
- purity_total: `14`
- score: `10`
- exact_aggregation: `False`
- ordered_exact_by_boundary_gap: `False`
- majority_order_by_boundary_gap: `[0, 1, 2, 1]`

### Best candidate groups

- key=(0, 0), microcells=3, rows=6, forms={0: 4, 3: 2}, majority=0, gap=-9
- key=(1, 3), microcells=3, rows=6, forms={1: 4, 2: 2}, majority=1, gap=9
- key=(0, 2), microcells=4, rows=8, forms={0: 2, 2: 4, 3: 2}, majority=2, gap=11
- key=(1, 1), microcells=2, rows=4, forms={1: 2, 3: 2}, majority=1, gap=13

## Top candidates

- key=C_delta_mod15_mod_2|C_delta_mod15_mod_4, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_2|outside_boundary_span_mod_4, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_2|slot_max_mod_4, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_4, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_4|base_component_id_floor_div_6, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_4|from_C_sum_mod_2, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_4|lift_q_signature, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_4|outside_boundary_span_mod_2, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_4|outside_boundary_span_mod_4, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]
- key=C_delta_mod15_mod_4|outside_plus_inside_mod3, groups=4, purity=14/24, score=10, exact=False, ordered_exact=False, order=[0, 1, 2, 1]

## Interpretation

Artifact 064 tests whether the pure transition-cell layer can be quotiented back into the four Euclidean forms. This is the natural next layer after 063: 063 found purity at 12 microcells, while 064 asks whether a native aggregation law recovers the four-form partition.

## Boundary

This is an aggregation audit, not native closure. A hit would be a candidate requiring validation; a miss only bounds the tested quotient family. answer-label leakage remains open, this is not full role-labeled shared_B universe derivation, and is not Gap A closure.
