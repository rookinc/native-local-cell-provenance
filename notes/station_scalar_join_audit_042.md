# Station scalar join audit 042

Status: station_scalar_join_audit_recorded

## Result

- audit_pass: `True`
- station_direct_derivation_pass: `False`
- free_block_scalar_032_theorem_candidate_pass: `True`
- relay_selector_035_theorem_candidate_pass: `True`
- station_extract_041_pass: `True`
- canonical_row_count_24: `True`
- all_state_join_checks: `True`
- target_count: `7`
- target_count_with_exact_station_feature: `1`
- station_direct_derivation_pass: `False`

## State joins

- O0:
  - c_path: `[11, 2, 14, 11]`
  - row_count: `6`
  - transition_counts: `{'(11, 2)': 2, '(2, 14)': 2, '(14, 11)': 2}`
  - role_class_counts: `{'reverse_partner': 3, 'shared_B': 3}`
  - role_pair_counts: `{'TI/XY': 2, 'IW/YZ': 2, 'WX/ZT': 2}`
  - station_role_counts: `{'TI': 1, 'XY': 1, 'YZ': 1, 'IW': 1, 'WX': 1, 'ZT': 1}`
  - checks: `{'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True}`
- O1:
  - c_path: `[13, 1, 10, 13]`
  - row_count: `6`
  - transition_counts: `{'(13, 1)': 2, '(1, 10)': 2, '(10, 13)': 2}`
  - role_class_counts: `{'reverse_partner': 3, 'shared_B': 3}`
  - role_pair_counts: `{'TI/XY': 2, 'IW/YZ': 2, 'WX/ZT': 2}`
  - station_role_counts: `{'TI': 1, 'XY': 1, 'YZ': 1, 'IW': 1, 'WX': 1, 'ZT': 1}`
  - checks: `{'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True}`
- B0:
  - c_path: `[2, 5, 0, 2]`
  - row_count: `6`
  - transition_counts: `{'(2, 5)': 2, '(5, 0)': 2, '(0, 2)': 2}`
  - role_class_counts: `{'reverse_partner': 3, 'shared_B': 3}`
  - role_pair_counts: `{'TI/XY': 2, 'IW/YZ': 2, 'WX/ZT': 2}`
  - station_role_counts: `{'TI': 1, 'XY': 1, 'YZ': 1, 'IW': 1, 'WX': 1, 'ZT': 1}`
  - checks: `{'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True}`
- B1:
  - c_path: `[4, 5, 2, 4]`
  - row_count: `6`
  - transition_counts: `{'(4, 5)': 2, '(5, 2)': 2, '(2, 4)': 2}`
  - role_class_counts: `{'reverse_partner': 3, 'shared_B': 3}`
  - role_pair_counts: `{'TI/XY': 2, 'IW/YZ': 2, 'WX/ZT': 2}`
  - station_role_counts: `{'TI': 1, 'XY': 1, 'YZ': 1, 'IW': 1, 'WX': 1, 'ZT': 1}`
  - checks: `{'row_count_is_6': True, 'transition_counts_are_2_each': True, 'shared_count_is_3': True, 'reverse_count_is_3': True, 'role_pair_count_is_3': True}`

## Scalar targets

- free_min:
  - target_values: `{'O0': 8, 'O1': 0, 'B0': 0, 'B1': 2}`
  - target_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 8, 'pb': -8, 'pr': -8, 'pbr': 10}, 'predictions': {'O0': 8, 'O1': 0, 'B0': 0, 'B1': 2}, 'coefficient_l1': 34}`
  - direct_exact_station_feature_count: `0`
  - nearest_station_features_by_l1_first_5: `[{'feature': 'all_from_B_min', 'values': {'O0': 2, 'O1': 1, 'B0': 0, 'B1': 2}, 'l1_error': 7}, {'feature': 'all_from_B_unique_min', 'values': {'O0': 2, 'O1': 1, 'B0': 0, 'B1': 2}, 'l1_error': 7}, {'feature': 'all_from_C_min', 'values': {'O0': 2, 'O1': 1, 'B0': 0, 'B1': 2}, 'l1_error': 7}, {'feature': 'all_from_C_unique_min', 'values': {'O0': 2, 'O1': 1, 'B0': 0, 'B1': 2}, 'l1_error': 7}, {'feature': 'all_from_fiber_min', 'values': {'O0': 2, 'O1': 1, 'B0': 0, 'B1': 2}, 'l1_error': 7}]`
- free_size:
  - target_values: `{'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}`
  - target_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 3, 'pb': 0, 'pr': 0, 'pbr': 0}, 'predictions': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'coefficient_l1': 3}`
  - direct_exact_station_feature_count: `140`
  - direct_exact_station_features_first_10: `[{'feature': 'all_C_int_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_fiber_int_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_fiber_mod_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_from_A_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_from_B_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_from_C_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_from_fiber_mod15_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_from_fiber_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_from_slot_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}, {'feature': 'all_lift_q_max', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}}]`
  - nearest_station_features_by_l1_first_5: `[{'feature': 'all_B_mod_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 4, 'B1': 4}, 'l1_error': 2}, {'feature': 'all_C_delta_mod15_unique_count', 'values': {'O0': 2, 'O1': 2, 'B0': 3, 'B1': 3}, 'l1_error': 2}, {'feature': 'all_C_mod_delta_unique_count', 'values': {'O0': 2, 'O1': 2, 'B0': 3, 'B1': 3}, 'l1_error': 2}, {'feature': 'all_slot_mod_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 4, 'B1': 4}, 'l1_error': 2}, {'feature': 'reverse_B_mod_delta_unique_count', 'values': {'O0': 2, 'O1': 2, 'B0': 3, 'B1': 3}, 'l1_error': 2}]`
- free_sum:
  - target_values: `{'O0': 29, 'O1': 27, 'B0': 5, 'B1': 12}`
  - target_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 29, 'pb': -24, 'pr': -2, 'pbr': 9}, 'predictions': {'O0': 29, 'O1': 27, 'B0': 5, 'B1': 12}, 'coefficient_l1': 64}`
  - direct_exact_station_feature_count: `0`
  - nearest_station_features_by_l1_first_5: `[{'feature': 'all_from_B_unique_sum', 'values': {'O0': 27, 'O1': 24, 'B0': 7, 'B1': 11}, 'l1_error': 8}, {'feature': 'all_from_C_unique_sum', 'values': {'O0': 27, 'O1': 24, 'B0': 7, 'B1': 11}, 'l1_error': 8}, {'feature': 'all_from_fiber_mod15_unique_sum', 'values': {'O0': 27, 'O1': 24, 'B0': 7, 'B1': 11}, 'l1_error': 8}, {'feature': 'all_from_fiber_unique_sum', 'values': {'O0': 27, 'O1': 24, 'B0': 7, 'B1': 11}, 'l1_error': 8}, {'feature': 'all_from_slot_unique_sum', 'values': {'O0': 27, 'O1': 24, 'B0': 7, 'B1': 11}, 'l1_error': 8}]`
- relay_max:
  - target_values: `{'O0': 7, 'O1': 9, 'B0': 8, 'B1': 13}`
  - target_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 7, 'pb': 1, 'pr': 2, 'pbr': 3}, 'predictions': {'O0': 7, 'O1': 9, 'B0': 8, 'B1': 13}, 'coefficient_l1': 13}`
  - direct_exact_station_feature_count: `0`
  - nearest_station_features_by_l1_first_5: `[{'feature': 'all_from_A_max', 'values': {'O0': 7, 'O1': 9, 'B0': 12, 'B1': 12}, 'l1_error': 5}, {'feature': 'all_from_A_unique_max', 'values': {'O0': 7, 'O1': 9, 'B0': 12, 'B1': 12}, 'l1_error': 5}, {'feature': 'all_to_A_max', 'values': {'O0': 7, 'O1': 9, 'B0': 12, 'B1': 12}, 'l1_error': 5}, {'feature': 'all_to_A_unique_max', 'values': {'O0': 7, 'O1': 9, 'B0': 12, 'B1': 12}, 'l1_error': 5}, {'feature': 'reverse_from_A_max', 'values': {'O0': 7, 'O1': 9, 'B0': 12, 'B1': 12}, 'l1_error': 5}]`
- relay_min:
  - target_values: `{'O0': 4, 'O1': 2, 'B0': 4, 'B1': 8}`
  - target_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 4, 'pb': 0, 'pr': -2, 'pbr': 6}, 'predictions': {'O0': 4, 'O1': 2, 'B0': 4, 'B1': 8}, 'coefficient_l1': 12}`
  - direct_exact_station_feature_count: `0`
  - nearest_station_features_by_l1_first_5: `[{'feature': 'shared_A_mod_delta_min', 'values': {'O0': 6, 'O1': 2, 'B0': 2, 'B1': 8}, 'l1_error': 4}, {'feature': 'shared_A_mod_delta_unique_min', 'values': {'O0': 6, 'O1': 2, 'B0': 2, 'B1': 8}, 'l1_error': 4}, {'feature': 'all_A_int_delta_unique_count', 'values': {'O0': 4, 'O1': 4, 'B0': 4, 'B1': 4}, 'l1_error': 6}, {'feature': 'all_A_mod_delta_unique_count', 'values': {'O0': 4, 'O1': 4, 'B0': 4, 'B1': 4}, 'l1_error': 6}, {'feature': 'all_B_int_delta_unique_count', 'values': {'O0': 4, 'O1': 4, 'B0': 4, 'B1': 4}, 'l1_error': 6}]`
- relay_size:
  - target_values: `{'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}`
  - target_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 3, 'pb': -1, 'pr': 0, 'pbr': 1}, 'predictions': {'O0': 3, 'O1': 3, 'B0': 2, 'B1': 3}, 'coefficient_l1': 5}`
  - direct_exact_station_feature_count: `0`
  - nearest_station_features_by_l1_first_5: `[{'feature': 'all_C_int_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'all_fiber_int_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'all_fiber_mod_delta_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'all_from_A_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}, {'feature': 'all_from_B_unique_count', 'values': {'O0': 3, 'O1': 3, 'B0': 3, 'B1': 3}, 'l1_error': 1}]`
- relay_sum:
  - target_values: `{'O0': 16, 'O1': 15, 'B0': 12, 'B1': 31}`
  - target_bit_law: `{'formula': 'p0 + pb*b + pr*r + pbr*b*r', 'coefficients': {'p0': 16, 'pb': -4, 'pr': -1, 'pbr': 20}, 'predictions': {'O0': 16, 'O1': 15, 'B0': 12, 'B1': 31}, 'coefficient_l1': 41}`
  - direct_exact_station_feature_count: `0`
  - nearest_station_features_by_l1_first_5: `[{'feature': 'all_A_mod_delta_sum', 'values': {'O0': 30, 'O1': 15, 'B0': 15, 'B1': 30}, 'l1_error': 18}, {'feature': 'all_A_mod_delta_unique_sum', 'values': {'O0': 30, 'O1': 15, 'B0': 15, 'B1': 30}, 'l1_error': 18}, {'feature': 'shared_A_mod_delta_sum', 'values': {'O0': 30, 'O1': 15, 'B0': 15, 'B1': 30}, 'l1_error': 18}, {'feature': 'shared_A_mod_delta_unique_sum', 'values': {'O0': 30, 'O1': 15, 'B0': 15, 'B1': 30}, 'l1_error': 18}, {'feature': 'all_C_delta_mod15_unique_sum', 'values': {'O0': 18, 'O1': 12, 'B0': 15, 'B1': 15}, 'l1_error': 24}]`

## Interpretation

This joins each local Lift/Twist state to the canonical WXYZTI station rows using the state's C path transitions. It then tests whether the scalar targets from 032 and 035 are direct readouts of station-register summaries.

## Boundary

This is a join and feature audit. Exact station features are evidence of station-register provenance, not a full generator. Failure to find exact station features does not refute the 036 pipeline; it means the scalar laws need a richer register law or a different join.
