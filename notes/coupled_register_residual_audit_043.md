# Coupled register residual audit 043

Status: coupled_register_residual_audit_recorded

## Result

- audit_pass: `True`
- free_block_scalar_032_theorem_candidate_pass: `True`
- relay_selector_035_theorem_candidate_pass: `True`
- station_extract_041_pass: `True`
- station_scalar_join_042_pass: `True`
- all_join_checks: `True`
- target_count: `7`
- nontrivial_target_count: `6`
- nontrivial_targets_with_exact_coupled_candidate: `1`
- all_nontrivial_targets_have_exact_candidate: `False`

## Seed summary

- O0: `{'seed_set_count': 198, 'feature_count': 9814, 'joined_row_count': 6, 'join_checks': {'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True, 'station_role_count_is_6': True}}`
- O1: `{'seed_set_count': 198, 'feature_count': 9802, 'joined_row_count': 6, 'join_checks': {'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True, 'station_role_count_is_6': True}}`
- B0: `{'seed_set_count': 198, 'feature_count': 9862, 'joined_row_count': 6, 'join_checks': {'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True, 'station_role_count_is_6': True}}`
- B1: `{'seed_set_count': 198, 'feature_count': 9814, 'joined_row_count': 6, 'join_checks': {'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True, 'station_role_count_is_6': True}}`

## Target results

- free_min:
  - target_values: `{'O0': 8, 'O1': 0, 'B0': 0, 'B1': 2}`
  - target_bit_law: `{'coefficients': {'p0': 8, 'pb': -8, 'pr': -8, 'pbr': 10}, 'predictions': {'O0': 8, 'O1': 0, 'B0': 0, 'B1': 2}, 'coefficient_l1': 34}`
  - candidate_feature_count: `9718`
  - exact_candidate_count: `0`
  - exact_candidates_first_10: `[]`
  - nearest_candidates_first_5: `[{'feature': 'set__q3__to_C__range', 'values': {'O0': 9, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 3}, {'feature': 'set__q3__to_fiber_mod15__range', 'values': {'O0': 9, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 3}, {'feature': 'op__q0__to_C__cpath_minus__range', 'values': {'O0': 9, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 3}, {'feature': 'op__q3__to_C__inter_cpath__range', 'values': {'O0': 9, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 3}, {'feature': 'op__q0__to_fiber_mod15__cpath_minus__range', 'values': {'O0': 9, 'O1': 0, 'B0': 0, 'B1': 0}, 'l1_error': 3}]`
- free_size:
  - target_values: `{'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}`
  - target_bit_law: `{'coefficients': {'p0': 3, 'pb': 0, 'pr': 0, 'pbr': 0}, 'predictions': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'coefficient_l1': 3}`
  - candidate_feature_count: `9718`
  - exact_candidate_count: `240`
  - exact_candidates_first_10: `[{'feature': 'rows__shared__count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'rows__reverse__count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__all__to_A__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__all__to_B__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__all__to_C__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__all__from_A__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__all__from_B__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__all__from_C__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__all__to_slot__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}, {'feature': 'set__shared__to_A__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 0}]`
  - nearest_candidates_first_5: `[{'feature': 'set__q0__to_A__size', 'values': {'O0': 2, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'set__q0__to_B__size', 'values': {'O0': 2, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'set__q0__from_A__size', 'values': {'O0': 2, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'set__q0__from_B__size', 'values': {'O0': 2, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'set__q0__A_delta__size', 'values': {'O0': 2, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}]`
- free_sum:
  - target_values: `{'O0': 29, 'O1': 27, 'B0': 5, 'B1': 12}`
  - target_bit_law: `{'coefficients': {'p0': 29, 'pb': -24, 'pr': -2, 'pbr': 9}, 'predictions': {'O0': 29, 'O1': 27, 'B0': 5, 'B1': 12}, 'coefficient_l1': 64}`
  - candidate_feature_count: `9718`
  - exact_candidate_count: `0`
  - exact_candidates_first_10: `[]`
  - nearest_candidates_first_5: `[{'feature': 'op__q0__A_delta__cpath_minus__sum', 'values': {'O0': 27, 'O1': 24, 'B0': 5, 'B1': 11}, 'l1_error': 6}, {'feature': 'op__station_ZT__A_delta__cpath_minus__sum', 'values': {'O0': 27, 'O1': 24, 'B0': 5, 'B1': 11}, 'l1_error': 6}, {'feature': 'op__rolepair_WX_ZT__A_delta__cpath_minus__sum', 'values': {'O0': 27, 'O1': 24, 'B0': 5, 'B1': 11}, 'l1_error': 6}, {'feature': 'set__all__to_B__sum', 'values': {'O0': 27, 'O1': 24, 'B0': 7, 'B1': 11}, 'l1_error': 8}, {'feature': 'set__all__to_C__sum', 'values': {'O0': 27, 'O1': 24, 'B0': 7, 'B1': 11}, 'l1_error': 8}]`
- relay_max:
  - target_values: `{'O0': 7, 'O1': 9, 'B0': 8, 'B1': 13}`
  - target_bit_law: `{'coefficients': {'p0': 7, 'pb': 1, 'pr': 2, 'pbr': 3}, 'predictions': {'O0': 7, 'O1': 9, 'B0': 8, 'B1': 13}, 'coefficient_l1': 13}`
  - candidate_feature_count: `9718`
  - exact_candidate_count: `0`
  - exact_candidates_first_10: `[]`
  - nearest_candidates_first_5: `[{'feature': 'set__rolepair_IW_YZ__to_A__max', 'values': {'O0': 7, 'O1': 9, 'B0': 10, 'B1': 12}, 'l1_error': 3}, {'feature': 'set__rolepair_WX_ZT__from_A__max', 'values': {'O0': 7, 'O1': 9, 'B0': 10, 'B1': 12}, 'l1_error': 3}, {'feature': 'op__rolepair_IW_YZ__to_A__minus_cpath__max', 'values': {'O0': 7, 'O1': 9, 'B0': 10, 'B1': 12}, 'l1_error': 3}, {'feature': 'op__rolepair_WX_ZT__from_A__minus_cpath__max', 'values': {'O0': 7, 'O1': 9, 'B0': 10, 'B1': 12}, 'l1_error': 3}, {'feature': 'set__q0__A_delta__max', 'values': {'O0': 6, 'O1': 7, 'B0': 9, 'B1': 13}, 'l1_error': 4}]`
- relay_min:
  - target_values: `{'O0': 4, 'O1': 2, 'B0': 4, 'B1': 8}`
  - target_bit_law: `{'coefficients': {'p0': 4, 'pb': 0, 'pr': -2, 'pbr': 6}, 'predictions': {'O0': 4, 'O1': 2, 'B0': 4, 'B1': 8}, 'coefficient_l1': 12}`
  - candidate_feature_count: `9718`
  - exact_candidate_count: `0`
  - exact_candidates_first_10: `[]`
  - nearest_candidates_first_5: `[{'feature': 'op__shared__A_delta__minus_cpath__min', 'values': {'O0': 6, 'O1': 2, 'B0': 4, 'B1': 8}, 'l1_error': 2}, {'feature': 'set__shared__A_delta__min', 'values': {'O0': 6, 'O1': 2, 'B0': 2, 'B1': 8}, 'l1_error': 4}, {'feature': 'rolecouple__A_delta__shared_minus_reverse__min', 'values': {'O0': 6, 'O1': 2, 'B0': 2, 'B1': 8}, 'l1_error': 4}, {'feature': 'set__all__A_delta__size', 'values': {'O0': 4, 'O1': 4, 'B0': 4, 'B1': 4}, 'l1_error': 6}, {'feature': 'set__all__B_delta__size', 'values': {'O0': 3, 'O1': 3, 'B0': 4, 'B1': 4}, 'l1_error': 6}]`
- relay_size:
  - target_values: `{'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}`
  - target_bit_law: `{'coefficients': {'p0': 3, 'pb': -1, 'pr': 0, 'pbr': 1}, 'predictions': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'coefficient_l1': 5}`
  - candidate_feature_count: `9718`
  - exact_candidate_count: `24`
  - exact_candidates_first_10: `[{'feature': 'op__q0__B_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__q0__slot_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__shared__B_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__reverse__A_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__reverse__B_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__shared__slot_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__reverse__slot_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__station_IW__B_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__station_TI__A_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}, {'feature': 'op__station_WX__A_delta__cpath_minus__size', 'values': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'l1_error': 0}]`
  - nearest_candidates_first_5: `[{'feature': 'rows__shared__count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'rows__reverse__count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'set__all__to_A__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'set__all__to_B__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'set__all__to_C__size', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}]`
- relay_sum:
  - target_values: `{'O0': 16, 'O1': 15, 'B0': 12, 'B1': 31}`
  - target_bit_law: `{'coefficients': {'p0': 16, 'pb': -4, 'pr': -1, 'pbr': 20}, 'predictions': {'O0': 16, 'O1': 15, 'B0': 12, 'B1': 31}, 'coefficient_l1': 41}`
  - candidate_feature_count: `9718`
  - exact_candidate_count: `0`
  - exact_candidates_first_10: `[]`
  - nearest_candidates_first_5: `[{'feature': 'op__all__A_delta__minus_cpath__sum', 'values': {'O0': 19, 'O1': 15, 'B0': 13, 'B1': 30}, 'l1_error': 5}, {'feature': 'op__shared__A_delta__minus_cpath__sum', 'values': {'O0': 19, 'O1': 15, 'B0': 13, 'B1': 30}, 'l1_error': 5}, {'feature': 'set__all__A_delta__sum', 'values': {'O0': 30, 'O1': 15, 'B0': 15, 'B1': 30}, 'l1_error': 18}, {'feature': 'set__shared__A_delta__sum', 'values': {'O0': 30, 'O1': 15, 'B0': 15, 'B1': 30}, 'l1_error': 18}, {'feature': 'rolecouple__A_delta__union__sum', 'values': {'O0': 30, 'O1': 15, 'B0': 15, 'B1': 30}, 'l1_error': 18}]`

## Interpretation

Artifact 042 showed that scalar targets are not raw station-row aggregate readouts. This bounded audit searches coupled residue readouts using complements, C-path exclusions, role-class gates, role-pair gates, station-role gates, and q gates.

## Boundary

This is a bounded reduced four-state candidate search. Exact candidates are hypotheses, not full native derivations. This does not derive the full role-labeled shared_B universe and does not close Gap A.
